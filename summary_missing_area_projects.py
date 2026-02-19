#!/usr/bin/env python3
"""
Summary: how many closed USD projects had budget in gt but missing/zero area.
Compares distinct project counts (include vs exclude area filter) and row counts from the two outputs.
"""
import os

try:
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except (PermissionError, FileNotFoundError):
        pass
except ImportError:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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

# Same but only with positive area
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
  AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) IS NOT NULL
  AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) > 0
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
        with open(os.path.join(SCRIPT_DIR, "budget_query_results_curated_closed_by_category_with_state_using_mapping.csv")) as f:
            include_rows = sum(1 for _ in f) - 1
        with open(os.path.join(SCRIPT_DIR, "budget_query_results_curated_closed_by_category_with_state_using_mapping_excludes_missing_area.csv")) as f:
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
    print("Summary: {:,.0f} closed USD projects had budget in generictask but missing or zero area (both grossarea and usablearea).".format(projects_missing_area))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
