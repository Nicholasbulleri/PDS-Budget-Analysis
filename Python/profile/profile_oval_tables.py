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

"""
Profile all Oval_* tables in work_dynamics.curated.
Discovers the tables, describes their schemas, pulls row counts,
sample data, and basic column-level stats.
"""
import sys, os, json

from edp_connection import execute_query

CATALOG = "work_dynamics"
SCHEMA = "curated"
PREFIX = "Oval_"

def discover_tables():
    q = f"SHOW TABLES IN {CATALOG}.{SCHEMA} LIKE '{PREFIX}*'"
    cols, rows = execute_query(q)
    tables = [r[1] for r in rows]  # tableName is typically index 1
    return sorted(tables)

def describe_table(table):
    fqn = f"{CATALOG}.{SCHEMA}.{table}"
    cols, rows = execute_query(f"DESCRIBE TABLE {fqn}")
    schema_rows = []
    for r in rows:
        col_name = r[0].strip() if r[0] else ""
        if col_name == "" or col_name.startswith("#"):
            break
        schema_rows.append({
            "column": col_name,
            "type": (r[1].strip() if r[1] else ""),
            "comment": (r[2].strip() if len(r) > 2 and r[2] else "")
        })
    return schema_rows

def get_row_count(table):
    fqn = f"{CATALOG}.{SCHEMA}.{table}"
    cols, rows = execute_query(f"SELECT COUNT(*) AS cnt FROM {fqn}")
    return rows[0][0]

def get_sample(table, n=5):
    fqn = f"{CATALOG}.{SCHEMA}.{table}"
    cols, rows = execute_query(f"SELECT * FROM {fqn} LIMIT {n}")
    return cols, rows

def get_distinct_counts(table, columns):
    """Get distinct count for each column (batch in one query)."""
    fqn = f"{CATALOG}.{SCHEMA}.{table}"
    exprs = ", ".join(f"COUNT(DISTINCT `{c}`) AS `dc_{c}`" for c in columns)
    null_exprs = ", ".join(f"SUM(CASE WHEN `{c}` IS NULL THEN 1 ELSE 0 END) AS `null_{c}`" for c in columns)
    q = f"SELECT {exprs}, {null_exprs} FROM {fqn}"
    cols, rows = execute_query(q)
    result = {}
    for i, c in enumerate(columns):
        result[c] = {
            "distinct": rows[0][i],
            "nulls": rows[0][len(columns) + i]
        }
    return result

def get_table_properties(table):
    """Get extended table properties (owner, location, created, etc.)."""
    fqn = f"{CATALOG}.{SCHEMA}.{table}"
    cols, rows = execute_query(f"DESCRIBE TABLE EXTENDED {fqn}")
    props = {}
    capture = False
    for r in rows:
        key = (r[0].strip() if r[0] else "").lower()
        val = (r[1].strip() if r[1] else "")
        if key.startswith("# detailed table"):
            capture = True
            continue
        if capture and key:
            props[key] = val
    return props

def main():
    print("=" * 80)
    print(f"  OVAL TABLE PROFILING — {CATALOG}.{SCHEMA}")
    print("=" * 80)

    tables = discover_tables()
    print(f"\nDiscovered {len(tables)} Oval_ tables:")
    for t in tables:
        print(f"  - {t}")

    profiles = {}

    for table in tables:
        print(f"\n{'─' * 80}")
        print(f"  TABLE: {CATALOG}.{SCHEMA}.{table}")
        print(f"{'─' * 80}")

        # Schema
        schema = describe_table(table)
        col_names = [c["column"] for c in schema]
        print(f"\n  Columns ({len(schema)}):")
        for c in schema:
            comment_str = f"  -- {c['comment']}" if c['comment'] else ""
            print(f"    {c['column']:45s} {c['type']:25s}{comment_str}")

        # Row count
        row_count = get_row_count(table)
        print(f"\n  Row count: {row_count:,}")

        # Distinct & null counts
        print(f"\n  Column-level distinct / null counts:")
        stats = get_distinct_counts(table, col_names)
        for c in col_names:
            d = stats[c]["distinct"]
            n = stats[c]["nulls"]
            null_pct = (n / row_count * 100) if row_count > 0 else 0
            print(f"    {c:45s}  distinct={d:>10,}   nulls={n:>10,} ({null_pct:5.1f}%)")

        # Table properties
        props = get_table_properties(table)
        if props:
            print(f"\n  Table properties:")
            for k, v in props.items():
                if v and k in ("owner", "created time", "last access", "created by",
                               "type", "provider", "location", "table properties",
                               "storage properties", "comment"):
                    print(f"    {k:30s} {v}")

        # Sample data
        sample_cols, sample_rows = get_sample(table, 3)
        print(f"\n  Sample rows (first 3):")
        header = " | ".join(f"{c[:30]:30s}" for c in sample_cols)
        print(f"    {header}")
        print(f"    {'-' * len(header)}")
        for row in sample_rows:
            vals = " | ".join(f"{str(v)[:30]:30s}" for v in row)
            print(f"    {vals}")

        profiles[table] = {
            "row_count": row_count,
            "column_count": len(schema),
            "schema": schema,
            "stats": {c: {"distinct": stats[c]["distinct"], "nulls": stats[c]["nulls"]} for c in col_names},
            "properties": props
        }

    # Summary
    print(f"\n\n{'=' * 80}")
    print("  SUMMARY")
    print(f"{'=' * 80}")
    print(f"\n  {'Table':<50s} {'Rows':>12s} {'Columns':>10s}")
    print(f"  {'─' * 72}")
    for table in tables:
        p = profiles[table]
        print(f"  {table:<50s} {p['row_count']:>12,} {p['column_count']:>10}")

    # Save full profile to JSON
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            "data", "oval_table_profiles.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    serializable = {}
    for t, p in profiles.items():
        sp = dict(p)
        sp["stats"] = {k: {sk: int(sv) for sk, sv in v.items()} for k, v in p["stats"].items()}
        sp["row_count"] = int(p["row_count"])
        serializable[t] = sp
    with open(out_path, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    print(f"\n  Full profile saved to: {out_path}")

if __name__ == "__main__":
    main()
