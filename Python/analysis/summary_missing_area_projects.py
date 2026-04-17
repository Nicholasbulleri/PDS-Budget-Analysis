#!/usr/bin/env python3
"""
Summary: how many closed USD projects had budget in gt but missing/zero area.
Compares distinct project counts (include vs exclude area filter) and row counts from the two outputs.
Writes missing_area_summary.csv for the budget dashboard.
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
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "quality")
BUDGET_DATA = os.path.join(PROJECT_ROOT, "data", "budget")
OUT_CSV = os.path.join(PROJECT_ROOT, "data", "quality", "missing_area_summary.csv")

# Distinct projects: closed USD with budget in generictask
Q_WITH_BUDGET = """
SELECT COUNT(DISTINCT p.id) AS cnt
FROM work_dynamics.curated.generictask gt
INNER JOIN work_dynamics.curated.project p
  ON gt.projectidentifier = p.workitemidentifier
WHERE p.currencytype = 'USD'
  AND p.phasetext = 'Closed'
  AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
  AND gt.originalbudgetamount IS NOT NULL
  AND gt.originalbudgetamount <> 0
"""

# Same but only with positive area (grossarea -> usablearea -> rentablearea; matches budget/project queries)
Q_WITH_BUDGET_AND_AREA = """
SELECT COUNT(DISTINCT p.id) AS cnt
FROM work_dynamics.curated.generictask gt
INNER JOIN work_dynamics.curated.project p
  ON gt.projectidentifier = p.workitemidentifier
WHERE p.currencytype = 'USD'
  AND p.phasetext = 'Closed'
  AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
  AND gt.originalbudgetamount IS NOT NULL
  AND gt.originalbudgetamount <> 0
  AND COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) IS NOT NULL
  AND COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) > 0
"""


def main():
    from edp_connection import execute_query

    _, r1 = execute_query(Q_WITH_BUDGET)
    _, r2 = execute_query(Q_WITH_BUDGET_AND_AREA)
    projects_with_budget = int(r1[0][0]) if r1 else 0
    projects_with_budget_and_area = int(r2[0][0]) if r2 else 0
    projects_missing_area = projects_with_budget - projects_with_budget_and_area

    # Row counts from the two output files (if present)
    include_rows = 9686   # from last run
    exclude_rows = 6621  # from last run
    try:
        with open(os.path.join(BUDGET_DATA, "budget_query_results_curated_closed_by_category_with_state_using_mapping.csv")) as f:
            include_rows = sum(1 for _ in f) - 1
        with open(os.path.join(BUDGET_DATA, "budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area.csv")) as f:
            exclude_rows = sum(1 for _ in f) - 1
    except FileNotFoundError:
        pass

    row_diff = include_rows - exclude_rows

    print("=" * 60)
    print("Budget closed: projects with budget but missing/zero area")
    print("=" * 60)
    print()
    print("Distinct projects (from Databricks):")
    print(f"  With budget (any area):              {projects_with_budget:,}")
    print(f"  With budget AND positive area:      {projects_with_budget_and_area:,}")
    print(f"  With budget but MISSING/ZERO area:  {projects_missing_area:,}")
    print()
    print("Output row counts (aggregated by category × city × country × sector):")
    print(f"  Include missing area:  {include_rows:,} rows")
    print(f"  Exclude missing area:  {exclude_rows:,} rows")
    print(f"  Row difference:        {row_diff:,} rows")
    print()
    print("Summary: {:,.0f} closed USD projects had budget in generictask but missing or zero area (grossarea, usablearea, and rentablearea).".format(projects_missing_area))

    # Write CSV for dashboard (metric, value)
    rows = [
        ("Distinct projects with budget (any area)", projects_with_budget),
        ("Distinct projects with budget AND positive area", projects_with_budget_and_area),
        ("Distinct projects with budget but MISSING/ZERO area", projects_missing_area),
        ("Output rows (include missing area)", include_rows),
        ("Output rows (exclude missing area)", exclude_rows),
    ]
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerows(rows)
    print(f"\nWritten: {OUT_CSV}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
