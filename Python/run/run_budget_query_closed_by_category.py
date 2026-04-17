#!/usr/bin/env python3
"""
Run the budget Closed query grouped by 3 categories (FF&E + Millwork, Soft Costs, Construction).
Uncategorized tasks are excluded. Output is much smaller than the full task-level query.
Reads the SQL from budget_core_query_closed_by_category.sql or uses embedded query.
"""
import csv
import os

try:
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except (PermissionError, FileNotFoundError):
        pass
except ImportError:
    pass

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
SQL_DIR = os.path.join(PROJECT_ROOT, "sql", "budget")
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "budget")
SQL_FILE = os.path.join(SQL_DIR, "budget_core_query_closed_by_category.sql")
OUT_CSV = os.path.join(DATA_DIR, "budget_query_results_curated_closed_by_category.csv")


def get_query():
    if os.path.isfile(SQL_FILE):
        with open(SQL_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    raise FileNotFoundError(SQL_FILE)


def main():
    from edp_connection import execute_query

    query = get_query()
    print("Running budget Closed query (by category, Uncategorized excluded)...")
    columns, results = execute_query(query)
    print(f"Retrieved {len(results)} rows, columns: {columns}")

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(results)
    print(f"Results written to {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
