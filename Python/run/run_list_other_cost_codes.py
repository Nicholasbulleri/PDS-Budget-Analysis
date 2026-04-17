#!/usr/bin/env python3
"""Run list_other_cost_codes.sql and write results to CSV."""
import csv
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
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
SQL_DIR = os.path.join(PROJECT_ROOT, "sql", "cost_codes")
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "cost_codes")
SQL_FILE = os.path.join(SQL_DIR, "Identify_other_cost_codes_not_mapped.sql")
OUT_CSV = os.path.join(PROJECT_ROOT, "data", "analysis", "other_cost_codes.csv")


def main():
    from edp_connection import execute_query

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        query = f.read()

    print("Running query: cost codes mapping to Other...")
    columns, results = execute_query(query)
    print(f"Retrieved {len(results)} distinct cost codes")

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(results)

    print(f"Written to {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
