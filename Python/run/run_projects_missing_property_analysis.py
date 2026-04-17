#!/usr/bin/env python3
"""
Run projects_missing_property_analysis.sql: count projects missing property by source system and month/year (Clarizen + Ingenious).
Outputs CSV: sourcesystem, year_month, total_projects, projects_missing_property, pct_missing_property.
"""
import os
import csv

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))
except (ImportError, PermissionError, FileNotFoundError):
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
SQL_DIR = os.path.join(PROJECT_ROOT, "sql", "projects")
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "projects")
SQL_FILE = os.path.join(SQL_DIR, "projects_missing_property_analysis.sql")
OUT_CSV = os.path.join(DATA_DIR, "projects_missing_property_analysis.csv")


def main():
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        query = f.read()

    from edp_connection import execute_query

    columns, rows = execute_query(query)
    if not columns:
        print("No columns returned.")
        return 1

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
