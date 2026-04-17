"""
Run dim_project_budget_benchmarking_filtered SQL and save results to CSV.
"""
import csv
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
SQL_FILE = PROJECT_ROOT / "sql" / "dim" / "dim_project_budget_benchmarking_filtered.sql"
OUTPUT_CSV = PROJECT_ROOT / "data" / "dim" / "dim_project_budget_benchmarking_filtered.csv"


def main():
    from edp_connection import connect_databricks

    sql = SQL_FILE.read_text(encoding="utf-8").strip().rstrip(";")
    print(f"Loaded SQL ({len(sql):,} chars)")

    print("Connecting to Databricks...")
    conn = connect_databricks()
    cursor = conn.cursor()

    print("Executing query (this may take a minute)...")
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    print(f"Fetched {len(rows):,} rows, {len(columns)} columns")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(columns)
        for row in rows:
            w.writerow(row)
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
