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
Catalog the full ds_pds_global schema: list all tables, their types,
row counts (approximate), and column inventories.

Connects ONCE at startup, reuses that single connection for all queries.
"""
import os
import json

from edp_connection import connect_to_edp

OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "analysis", "ds_pds_global_catalog.json")

def run_query(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [desc[0] for desc in cursor.description] if cursor.description else []
    rows = cursor.fetchall()
    cursor.close()
    return cols, rows

def main():
    catalog_name = "work_dynamics"
    schema_name = "ds_pds_global"

    print("Connecting to Databricks (one-time login)...")
    conn = connect_to_edp()
    print("Connected.\n")

    print(f"=== Cataloging {catalog_name}.{schema_name} ===\n")

    print("Step 1: Listing all tables and views...")
    cols, rows = run_query(conn, f"SHOW TABLES IN {catalog_name}.{schema_name}")
    print(f"  Column headers: {cols}")
    tables = []
    for row in rows:
        tbl = {"database": row[0], "tableName": row[1], "isTemporary": row[2] if len(row) > 2 else None}
        tables.append(tbl)
        print(f"  - {tbl['tableName']}")

    print(f"\nFound {len(tables)} objects.\n")

    results = []
    for i, t in enumerate(tables):
        tname = t["tableName"]
        fqn = f"{catalog_name}.{schema_name}.{tname}"
        print(f"[{i+1}/{len(tables)}] {tname}...", end=" ", flush=True)

        try:
            _, desc_rows = run_query(conn, f"DESCRIBE TABLE {fqn}")
            columns = []
            for r in desc_rows:
                col_name = r[0] if r[0] else ""
                if col_name.startswith("#") or col_name.strip() == "" or col_name.startswith("Part"):
                    continue
                columns.append({
                    "name": col_name,
                    "type": r[1] if len(r) > 1 else None,
                    "comment": r[2] if len(r) > 2 else None
                })
        except Exception as e:
            print(f"DESCRIBE failed: {e}", end=" ")
            columns = []

        try:
            _, cnt_rows = run_query(conn, f"SELECT count(*) FROM {fqn}")
            row_count = cnt_rows[0][0] if cnt_rows else None
        except Exception as e:
            print(f"COUNT failed: {e}", end=" ")
            row_count = None

        extended = {}
        try:
            _, ext_rows = run_query(conn, f"DESCRIBE TABLE EXTENDED {fqn}")
            capture = False
            for r in ext_rows:
                key = (r[0] or "").strip()
                val = (r[1] or "").strip() if len(r) > 1 else ""
                if key == "# Detailed Table Information":
                    capture = True
                    continue
                if capture and key:
                    extended[key] = val
        except:
            pass

        results.append({
            "table_name": tname,
            "fqn": fqn,
            "row_count": row_count,
            "column_count": len(columns),
            "columns": columns,
            "table_type": extended.get("Type", ""),
            "provider": extended.get("Provider", ""),
            "owner": extended.get("Owner", ""),
            "created_at": extended.get("Created Time", ""),
            "last_access": extended.get("Last Access", ""),
            "comment": extended.get("Comment", ""),
            "location": extended.get("Location", ""),
        })

        rc = f"{row_count:,}" if row_count is not None else "?"
        print(f"{len(columns)} cols, {rc} rows")

    print("\n" + "=" * 80)
    print(f"FULL CATALOG: {catalog_name}.{schema_name}")
    print("=" * 80)
    for r in sorted(results, key=lambda x: x["table_name"]):
        prefix = "dim" if r["table_name"].startswith("dim_") else "fact" if r["table_name"].startswith("fact_") else "id_res" if r["table_name"].startswith("id_") else "other"
        rc = f"{r['row_count']:,}" if r['row_count'] is not None else "?"
        print(f"\n[{prefix.upper():6s}] {r['table_name']}")
        print(f"  Type: {r['table_type']}  |  Rows: {rc}  |  Columns: {r['column_count']}")
        for c in r["columns"]:
            comment_str = f"  -- {c['comment']}" if c['comment'] else ""
            print(f"    {c['name']:40s} {c['type']}{comment_str}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {OUTPUT_PATH}")

    conn.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
