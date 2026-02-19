#!/usr/bin/env python3
"""
Run the core budget query against work_dynamics.curated via EDP Databricks connection.
Uses edp_connection (same as analyze EDP tables agent / analyze_ingenious_curated_views).
Authentication: Azure CLI cached login (run 'az login' once in browser, then cached)
or service principal via .env (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID).
Outputs results to CSV for use with the taskname category mapping.
"""

import csv
import os

# Load .env so EDP connection gets DATABRICKS_* and optional AZURE_* (same as other EDP agents)
try:
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except (PermissionError, FileNotFoundError):
        pass
except ImportError:
    pass

# Optional: limit rows for testing (set to None for full result)
LIMIT = os.environ.get("BUDGET_QUERY_LIMIT")  # e.g. "1000"

BUDGET_QUERY_CONSTRUCT = """
SELECT
    gt.costcode,
    gt.taskname,
    p.city,
    p.country,
    p.sector,
    SUM(COALESCE(NULLIF(p.grossarea, 0), p.usablearea)) AS area,
    SUM(gt.originalbudgetamount) AS total_original_budget,
    SUM(gt.totalprojectedbudgetamount) AS total_projected_budget,
    COUNT(p.id) AS project_count
FROM work_dynamics.curated.generictask gt
INNER JOIN work_dynamics.curated.project p
    ON gt.projectidentifier = p.workitemidentifier
WHERE p.currencytype = 'USD'
  AND p.phasetext = 'Construct'
  AND gt.internaltasktypetext = 'budget'
  AND gt.originalbudgetamount <> 0
GROUP BY gt.costcode, gt.taskname, p.city, p.country, p.sector
"""

BUDGET_QUERY_CLOSED = """
SELECT
    gt.costcode,
    gt.taskname,
    p.city,
    p.country,
    p.sector,
    SUM(COALESCE(NULLIF(p.grossarea, 0), p.usablearea)) AS area,
    SUM(gt.originalbudgetamount) AS total_original_budget,
    SUM(gt.totalprojectedbudgetamount) AS total_projected_budget,
    COUNT(p.id) AS project_count
FROM work_dynamics.curated.generictask gt
INNER JOIN work_dynamics.curated.project p
    ON gt.projectidentifier = p.workitemidentifier
WHERE p.currencytype = 'USD'
  AND p.phasetext = 'Closed'
  AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
  AND gt.originalbudgetamount IS NOT NULL
  AND gt.originalbudgetamount <> 0
GROUP BY gt.costcode, gt.taskname, p.city, p.country, p.sector
"""


def main():
    from edp_connection import execute_query

    phase = os.environ.get("BUDGET_QUERY_PHASE", "Construct").lower()
    query = BUDGET_QUERY_CLOSED if phase == "closed" else BUDGET_QUERY_CONSTRUCT
    if LIMIT:
        query = query.rstrip(";").strip() + f"\nLIMIT {int(LIMIT)}"

    print(f"Connecting to EDP Databricks and running budget query (phase={phase})...")
    columns, results = execute_query(query)
    print(f"Retrieved {len(results)} rows, columns: {columns}")

    out_path = f"budget_query_results_curated_{phase}.csv"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(results)
    print(f"Results written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
