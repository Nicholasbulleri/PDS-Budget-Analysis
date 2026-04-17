#!/usr/bin/env python3
"""
Run sql/generictask_data_profile_by_source.sql via EDP and write results to CSV.
"""
import csv
import sys
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
SQL_FILE = PROJECT_ROOT / "sql" / "profiling" / "generictask_data_profile_by_source.sql"
OUT_CSV = PROJECT_ROOT / "data" / "profiling" / "generictask_data_profile_by_source_results.csv"


def main():
    try:
        from edp_connection import execute_query
    except ImportError:
        print("Run from project root so edp_connection is on path.")
        return 1

    if not SQL_FILE.exists():
        print(f"SQL file not found: {SQL_FILE}")
        return 1

    query = SQL_FILE.read_text(encoding="utf-8")
    print("Running generictask_data_profile_by_source.sql ...")
    columns, results = execute_query(query)
    print(f"Retrieved {len(results)} rows, {len(columns)} columns.")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(results)
    print(f"Written to {OUT_CSV}")

    if results:
        print("\nPreview (first 5 rows, first 8 cols):")
        preview_cols = columns[:8]
        print("  " + " | ".join(f"{c[:14]:>14}" for c in preview_cols))
        print("  " + "-" * (16 * len(preview_cols)))
        for row in results[:5]:
            print("  " + " | ".join(f"{str(v)[:14]:>14}" for v in row[:8]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
