#!/usr/bin/env python3
"""
Data quality Issue 1: Projects missing property mapping (and thus area measurement).
Outputs counts by source system (Clarizen, Ingenious) for the Data Quality dashboard.
Writes data_quality_missing_area_by_source.csv: sourcesystem, projects_with_budget, projects_with_area, projects_missing_area.
"""
import csv
import os

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
OUT_CSV = os.path.join(PROJECT_ROOT, "data", "quality", "data_quality_missing_area_by_source.csv")

# Closed USD projects with budget (any area) – by source
Q_WITH_BUDGET_BY_SOURCE = """
SELECT
    LOWER(TRIM(COALESCE(p.sourcesystem, ''))) AS sourcesystem,
    COUNT(DISTINCT p.id) AS projects_with_budget
FROM work_dynamics.curated.generictask gt
INNER JOIN work_dynamics.curated.project p
    ON gt.projectidentifier = p.workitemidentifier
WHERE p.currencytype = 'USD'
  AND p.phasetext = 'Closed'
  AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
  AND gt.originalbudgetamount IS NOT NULL
  AND gt.originalbudgetamount <> 0
GROUP BY LOWER(TRIM(COALESCE(p.sourcesystem, '')))
"""

# Closed USD projects with budget AND positive area – by source
Q_WITH_BUDGET_AND_AREA_BY_SOURCE = """
SELECT
    LOWER(TRIM(COALESCE(p.sourcesystem, ''))) AS sourcesystem,
    COUNT(DISTINCT p.id) AS projects_with_area
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
GROUP BY LOWER(TRIM(COALESCE(p.sourcesystem, '')))
"""


def main():
    os.chdir(PROJECT_ROOT)
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    except ImportError:
        pass

    from edp_connection import execute_query

    _, r1 = execute_query(Q_WITH_BUDGET_BY_SOURCE)
    _, r2 = execute_query(Q_WITH_BUDGET_AND_AREA_BY_SOURCE)
    by_budget = {row[0]: int(row[1]) for row in (r1 or []) if row[0] in ("clarizen", "ingenious")}
    by_area = {row[0]: int(row[1]) for row in (r2 or []) if row[0] in ("clarizen", "ingenious")}

    rows = []
    for src in ("clarizen", "ingenious"):
        with_budget = by_budget.get(src, 0)
        with_area = by_area.get(src, 0)
        missing = with_budget - with_area
        rows.append({
            "sourcesystem": src,
            "projects_with_budget": with_budget,
            "projects_with_area": with_area,
            "projects_missing_area": missing,
        })

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["sourcesystem", "projects_with_budget", "projects_with_area", "projects_missing_area"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT_CSV} ({len(rows)} rows).")
    for r in rows:
        print(f"  {r['sourcesystem']}: {r['projects_missing_area']:,} missing area of {r['projects_with_budget']:,} with budget")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
