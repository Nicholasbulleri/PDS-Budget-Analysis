#!/usr/bin/env python3
"""
Data profile of work_dynamics.curated.generictask by source system.
Reports for each column: completeness (non-null %), distinct count, and flags ID/reference columns.
"""

import sys
import csv
from pathlib import Path

import sys
from pathlib import Path

for _p in Path(__file__).resolve().parents:
    if (_p / "repo_paths.py").is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break
else:
    raise RuntimeError("Not inside project Python tree")
from repo_paths import repo_root

PROJECT_ROOT = repo_root()
try:
    from edp_connection import connect_to_edp
except ImportError:
    connect_to_edp = None

TABLE_CATALOG = "work_dynamics"
TABLE_SCHEMA = "curated"
TABLE_NAME = "generictask"
SOURCE_COLUMN = "sourcesystem"
OUTPUT_CSV = PROJECT_ROOT / "data" / "profiling" / "generictask_data_profile_by_source.csv"
OUTPUT_MD = PROJECT_ROOT / "markdown" / "generictask_data_profile_by_source.md"


def is_id_or_reference(column_name: str) -> bool:
    if not column_name:
        return False
    lower = column_name.lower()
    if lower in ("id", "key"):
        return True
    if lower.endswith("_id") or lower.endswith("id"):
        return True
    if "identifier" in lower:
        return True
    if "_key" in lower or lower.endswith("_key"):
        return True
    if "reference" in lower and ("id" in lower or "key" in lower):
        return True
    return False


def get_columns(conn):
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            SELECT column_name, data_type
            FROM system.information_schema.columns
            WHERE table_catalog = '{TABLE_CATALOG}'
              AND table_schema = '{TABLE_SCHEMA}'
              AND table_name = '{TABLE_NAME}'
            ORDER BY ordinal_position
        """)
        rows = cursor.fetchall()
    finally:
        cursor.close()
    return [(r[0], r[1]) for r in (rows or []) if r and len(r) >= 2]


def escape_column(name: str) -> str:
    if not name:
        return name
    if any(
        name.lower() == w
        for w in ("from", "order", "group", "key", "select", "where", "table", "index")
    ):
        return f"`{name}`"
    if "." in name or " " in name or "-" in name:
        return f"`{name}`"
    return name


def profile_column_by_source(conn, column_name: str, data_type: str):
    esc = escape_column(column_name)
    use_distinct = data_type.upper() not in ("ARRAY", "MAP", "STRUCT", "BINARY")
    distinct_expr = f"COUNT(DISTINCT {esc})" if use_distinct else "NULL"
    sql = f"""
        SELECT
            LOWER(TRIM(COALESCE(CAST({escape_column(SOURCE_COLUMN)} AS STRING), ''))) AS source_system,
            COUNT(*) AS row_count,
            COUNT({esc}) AS non_null_count,
            {distinct_expr} AS distinct_count
        FROM {TABLE_CATALOG}.{TABLE_SCHEMA}.{TABLE_NAME}
        GROUP BY LOWER(TRIM(COALESCE(CAST({escape_column(SOURCE_COLUMN)} AS STRING), '')))
    """
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except Exception as e:
        return [("_error", 0, 0, 0, str(e))]
    finally:
        cursor.close()
    out = []
    for r in (rows or []):
        if r and len(r) >= 4:
            out.append((r[0], r[1], r[2], r[3], None))
        elif r and len(r) >= 1:
            out.append((r[0], 0, 0, 0, str(r)))
    return out


def run_profile(conn, columns, verbose=True):
    results = []
    n = len(columns)
    for i, (col_name, data_type) in enumerate(columns, 1):
        if verbose:
            print(f"  [{i}/{n}] {col_name} ({data_type})", end=" ", flush=True)
        try:
            rows = profile_column_by_source(conn, col_name, data_type)
            is_id = is_id_or_reference(col_name)
            for source_system, row_count, non_null_count, distinct_count, err in rows:
                pct = (100.0 * non_null_count / row_count) if row_count and row_count > 0 else 0.0
                results.append({
                    "column_name": col_name,
                    "data_type": data_type,
                    "is_id_or_reference": "Y" if is_id else "",
                    "source_system": source_system or "(blank)",
                    "row_count": row_count,
                    "non_null_count": non_null_count,
                    "pct_complete": round(pct, 1),
                    "distinct_count": distinct_count if distinct_count is not None else "",
                    "error": err or "",
                })
            if verbose:
                print("ok", flush=True)
        except Exception as e:
            if verbose:
                print(f"error: {e}", flush=True)
            results.append({
                "column_name": col_name,
                "data_type": data_type,
                "is_id_or_reference": "Y" if is_id_or_reference(col_name) else "",
                "source_system": "_error",
                "row_count": 0,
                "non_null_count": 0,
                "pct_complete": 0,
                "distinct_count": "",
                "error": str(e),
            })
    return results


def write_csv(results, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not results:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "column_name", "data_type", "is_id_or_reference",
                "source_system", "row_count", "non_null_count", "pct_complete", "distinct_count", "error"
            ],
        )
        w.writeheader()
        w.writerows(results)
    print(f"Wrote {path}")


def write_markdown(results, path, columns_with_types, sources):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    by_col = {}
    for r in results:
        c = r["column_name"]
        if c not in by_col:
            by_col[c] = []
        by_col[c].append(r)

    src_headers = " | ".join(s for s in sources)
    src_dashes = " | ".join("---" for _ in sources)
    lines = [
        "# Generictask table data profile by source system",
        "",
        f"Table: `{TABLE_CATALOG}.{TABLE_SCHEMA}.{TABLE_NAME}`",
        "",
        f"| Column | Data type | ID/Reference | {src_headers} | Notes |",
        f"|--------|-----------|--------------|{src_dashes}|-------|",
    ]
    for col_name, data_type in columns_with_types:
        rows = by_col.get(col_name, [])
        by_src = {r["source_system"]: r for r in rows}
        is_id = any(r.get("is_id_or_reference") == "Y" for r in rows)
        id_ref = "Yes" if is_id else ""
        cells = []
        for s in sources:
            r = by_src.get(s)
            if r and r.get("row_count", 0) > 0:
                pct = r.get("pct_complete", 0)
                cnt = r.get("non_null_count", 0)
                cells.append(f"{pct}% ({cnt:,})")
            else:
                cells.append("—")
        cell_str = " | ".join(cells)
        err = next((r.get("error") or "" for r in rows if r.get("error")), "")
        notes = err[:80] + "…" if len(err) > 80 else err
        lines.append(f"| {col_name} | {data_type} | {id_ref} | {cell_str} | {notes} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {path}")


def main():
    if not connect_to_edp:
        print("edp_connection not available; run from project root with Python path set.")
        return 1
    print(f"Connecting to EDP to profile {TABLE_CATALOG}.{TABLE_SCHEMA}.{TABLE_NAME}...")
    conn = connect_to_edp()
    if not conn:
        print("Failed to connect.")
        return 1
    print("Fetching generictask table columns...")
    columns = get_columns(conn)
    if not columns:
        print("No columns found. Check table_catalog/schema/name and permissions.")
        return 1
    print(f"Found {len(columns)} columns. Profiling by source system (this may take a while)...")
    results = run_profile(conn, columns, verbose=True)
    conn.close()

    sources = sorted({r["source_system"] for r in results if r.get("source_system") and r["source_system"] not in ("_error",)})
    write_csv(results, OUTPUT_CSV)
    write_markdown(results, OUTPUT_MD, columns, sources)

    id_cols = sorted({r["column_name"] for r in results if r.get("is_id_or_reference") == "Y"})
    print(f"\nColumns flagged as ID/Reference ({len(id_cols)}): {', '.join(id_cols[:20])}{'...' if len(id_cols) > 20 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
