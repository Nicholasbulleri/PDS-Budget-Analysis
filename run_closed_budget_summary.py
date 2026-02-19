#!/usr/bin/env python3
"""Print total closed USD projects, how many are missing budget in gt, and % missing."""
import os
try:
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except (PermissionError, FileNotFoundError):
        pass
except ImportError:
    pass

SUMMARY_SQL = """
WITH closed_usd AS (
  SELECT p.id
  FROM work_dynamics.curated.project p
  WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
),
projects_with_budget AS (
  SELECT DISTINCT p.id AS project_id
  FROM work_dynamics.curated.generictask gt
  INNER JOIN work_dynamics.curated.project p
    ON gt.projectidentifier = p.workitemidentifier
  WHERE p.currencytype = 'USD'
    AND p.phasetext = 'Closed'
    AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
    AND gt.originalbudgetamount IS NOT NULL
    AND gt.originalbudgetamount <> 0
)
SELECT
  (SELECT COUNT(*) FROM closed_usd) AS total_closed_usd_projects,
  (SELECT COUNT(*) FROM closed_usd c LEFT JOIN projects_with_budget w ON w.project_id = c.id WHERE w.project_id IS NULL) AS closed_projects_missing_budget
"""

def main():
    from edp_connection import execute_query
    cols, rows = execute_query(SUMMARY_SQL)
    if not rows:
        print("No summary row returned.")
        return 1
    total = int(rows[0][0])
    missing = int(rows[0][1])
    pct = (100.0 * missing / total) if total else 0
    print("Closed USD projects (budget in generictask):")
    print(f"  Total closed USD projects:     {total:,}")
    print(f"  Missing budget in gt:           {missing:,}")
    print(f"  Percent missing budget:         {pct:.1f}%")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
