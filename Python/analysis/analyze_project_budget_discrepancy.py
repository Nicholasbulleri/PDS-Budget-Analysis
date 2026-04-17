#!/usr/bin/env python3
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

"""
Analyze budget discrepancy: why do category sums not match project totals?
For "THE PASS" @ 4100 Raleigh St: total was ~$48M but 3 categories sum to ~$8.5M.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def run(sql, title):
    from edp_connection import execute_query
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    columns, rows = execute_query(sql)
    if not rows:
        print("  (no rows)")
        return rows
    print("  " + " | ".join(str(c) for c in columns))
    print("  " + "-" * 60)
    for row in rows:
        print("  ", row)
    return rows


def main():
    # Use sourceprojectid from CSV: 24682P4171460 for "THE PASS" @ 4100 Raleigh St
    run("""
        WITH proj AS (
            SELECT p.id, p.workitemidentifier, p.projectname, p.sourceprojectid
            FROM work_dynamics.curated.project p
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
              AND p.sourceprojectid = '24682P4171460'
        ),
        all_tasks AS (
            SELECT gt.taskname, gt.originalbudgetamount, gt.totalprojectedbudgetamount,
                   gt.internaltasktypetext
            FROM work_dynamics.curated.generictask gt
            INNER JOIN proj ON gt.projectidentifier = proj.workitemidentifier
            WHERE gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
        )
        SELECT COUNT(*) AS task_count, SUM(originalbudgetamount) AS total_original
        FROM all_tasks
    """, "1) Total budget for sourceprojectid 24682P4171460 (all task rows)")

    # Show unmapped tasknames and their amounts
    run("""
        WITH proj AS (
            SELECT p.id, p.workitemidentifier
            FROM work_dynamics.curated.project p
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
              AND p.sourceprojectid = '24682P4171460'
        ),
        all_tasks AS (
            SELECT gt.taskname, gt.originalbudgetamount,
                   CASE
                       WHEN LOWER(TRIM(gt.taskname)) RLIKE '^(11|12)[\\\\s\\\\-]' THEN 'FF&E + Millwork'
                       WHEN LOWER(TRIM(gt.taskname)) RLIKE '^[0-9]{2}[\\\\s\\\\-]' THEN 'Construction'
                       WHEN LOWER(TRIM(gt.taskname)) RLIKE '^\\\\s*\\\\-[\\\\s]*[0-9]{2}\\\\s' THEN 'Construction'
                       WHEN LOWER(TRIM(gt.taskname)) RLIKE 'div[\\\\s]*[0-9]+' THEN 'Construction'
                       WHEN LOWER(gt.taskname) LIKE '%soft%' AND (LOWER(gt.taskname) LIKE '%contingency%' OR LOWER(gt.taskname) LIKE '%cost%') THEN 'Soft Costs'
                       WHEN LOWER(gt.taskname) LIKE '%design%' AND (LOWER(gt.taskname) LIKE '%contingency%' OR LOWER(gt.taskname) LIKE '%allowance%') THEN 'Soft Costs'
                       WHEN LOWER(gt.taskname) LIKE '%contingency%' AND (LOWER(gt.taskname) LIKE '%ff&e%' OR LOWER(gt.taskname) LIKE '%furniture%') THEN 'FF&E + Millwork'
                       WHEN LOWER(gt.taskname) LIKE '%contingency%' OR LOWER(gt.taskname) LIKE '%allowance%' THEN 'Construction'
                       WHEN LOWER(gt.taskname) LIKE '%furniture%' OR LOWER(gt.taskname) LIKE '%millwork%' OR LOWER(gt.taskname) LIKE '%ff&e%' OR LOWER(gt.taskname) LIKE '%ffe%'
                            OR LOWER(gt.taskname) LIKE '%artwork%' OR LOWER(gt.taskname) LIKE '% signage%' OR LOWER(gt.taskname) LIKE '%branding%'
                            OR LOWER(gt.taskname) LIKE '%audio visual%' OR LOWER(gt.taskname) LIKE '%a/v%' OR LOWER(gt.taskname) LIKE '% it %' OR LOWER(gt.taskname) LIKE '% it'
                            OR LOWER(gt.taskname) LIKE '%equipment%' OR LOWER(gt.taskname) LIKE '%appliances%' OR LOWER(gt.taskname) LIKE '%blinds%'
                            OR LOWER(gt.taskname) LIKE '%workstations%' OR LOWER(gt.taskname) LIKE '%seating%' OR LOWER(gt.taskname) LIKE '%carpet%'
                            OR LOWER(gt.taskname) LIKE '%(it)%' OR LOWER(gt.taskname) LIKE '%information technology%'
                       THEN 'FF&E + Millwork'
                       WHEN LOWER(gt.taskname) LIKE '%architect%' OR LOWER(gt.taskname) LIKE '%designer%' OR LOWER(gt.taskname) LIKE '%engineer%'
                            OR LOWER(gt.taskname) LIKE '%consultant%' OR LOWER(gt.taskname) LIKE '%expeditor%' OR LOWER(gt.taskname) LIKE '%permit%'
                            OR LOWER(gt.taskname) LIKE '% pm fee%' OR LOWER(gt.taskname) LIKE '%jll %' OR LOWER(gt.taskname) LIKE '%project management%'
                            OR LOWER(gt.taskname) LIKE '%inspection%' OR LOWER(gt.taskname) LIKE '%survey%' OR LOWER(gt.taskname) LIKE '%legal%'
                            OR LOWER(gt.taskname) LIKE '%insurance%' OR LOWER(gt.taskname) LIKE '%leed%' OR LOWER(gt.taskname) LIKE '%sustainability%'
                            OR LOWER(gt.taskname) LIKE '%design fee%' OR LOWER(gt.taskname) LIKE '%reimbursable%' OR LOWER(gt.taskname) LIKE '%admin fee%'
                            OR LOWER(gt.taskname) LIKE '%management fee%' OR LOWER(gt.taskname) LIKE '%soft cost%'
                       THEN 'Soft Costs'
                       WHEN LOWER(gt.taskname) LIKE '%general contractor%' OR LOWER(gt.taskname) LIKE '% gc %' OR LOWER(gt.taskname) LIKE 'gc %' OR LOWER(gt.taskname) LIKE '% gmp %'
                            OR LOWER(gt.taskname) LIKE '%construction %' OR LOWER(gt.taskname) LIKE '%concrete%' OR LOWER(gt.taskname) LIKE '%structural%'
                            OR LOWER(gt.taskname) LIKE '%electrical%' OR LOWER(gt.taskname) LIKE '%plumbing%' OR LOWER(gt.taskname) LIKE '%hvac%'
                            OR LOWER(gt.taskname) LIKE '%demolition%' OR LOWER(gt.taskname) LIKE '%sitework%' OR LOWER(gt.taskname) LIKE '%earthwork%'
                            OR LOWER(gt.taskname) LIKE '%general conditions%' OR LOWER(gt.taskname) LIKE '%drywall%' OR LOWER(gt.taskname) LIKE '%framing%'
                            OR LOWER(gt.taskname) LIKE '%flooring%' OR LOWER(gt.taskname) LIKE '%ceilings%' OR LOWER(gt.taskname) LIKE '%painting%'
                            OR LOWER(gt.taskname) LIKE '%fire protection%' OR LOWER(gt.taskname) LIKE '%fire sprinkler%' OR LOWER(gt.taskname) LIKE '%roofing%'
                            OR LOWER(gt.taskname) LIKE '%facade%' OR LOWER(gt.taskname) LIKE '%cladding%' OR LOWER(gt.taskname) LIKE '%hard cost%'
                            OR LOWER(TRIM(gt.taskname)) LIKE '$%'
                            OR LOWER(TRIM(gt.taskname)) RLIKE '^[0-9]+\\\\.' OR LOWER(TRIM(gt.taskname)) RLIKE '^[0-9]+\\\\s+[a-z]'
                       THEN 'Construction'
                       ELSE NULL
                   END AS cost_code_category
            FROM work_dynamics.curated.generictask gt
            INNER JOIN proj ON gt.projectidentifier = proj.workitemidentifier
            WHERE gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
        )
        SELECT taskname, originalbudgetamount, cost_code_category
        FROM all_tasks
        ORDER BY originalbudgetamount DESC
        LIMIT 50
    """, "2) Top 50 task rows by amount (taskname, amount, mapped category)")

    run("""
        WITH proj AS (
            SELECT p.id, p.workitemidentifier
            FROM work_dynamics.curated.project p
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
              AND p.sourceprojectid = '24682P4171460'
        ),
        all_tasks AS (
            SELECT gt.taskname, gt.originalbudgetamount,
                   CASE
                       WHEN LOWER(TRIM(gt.taskname)) RLIKE '^(11|12)[\\\\s\\\\-]' THEN 'FF&E + Millwork'
                       WHEN LOWER(TRIM(gt.taskname)) RLIKE '^[0-9]{2}[\\\\s\\\\-]' THEN 'Construction'
                       WHEN LOWER(TRIM(gt.taskname)) RLIKE '^\\\\s*\\\\-[\\\\s]*[0-9]{2}\\\\s' THEN 'Construction'
                       WHEN LOWER(TRIM(gt.taskname)) RLIKE 'div[\\\\s]*[0-9]+' THEN 'Construction'
                       WHEN LOWER(gt.taskname) LIKE '%soft%' AND (LOWER(gt.taskname) LIKE '%contingency%' OR LOWER(gt.taskname) LIKE '%cost%') THEN 'Soft Costs'
                       WHEN LOWER(gt.taskname) LIKE '%design%' AND (LOWER(gt.taskname) LIKE '%contingency%' OR LOWER(gt.taskname) LIKE '%allowance%') THEN 'Soft Costs'
                       WHEN LOWER(gt.taskname) LIKE '%contingency%' AND (LOWER(gt.taskname) LIKE '%ff&e%' OR LOWER(gt.taskname) LIKE '%furniture%') THEN 'FF&E + Millwork'
                       WHEN LOWER(gt.taskname) LIKE '%contingency%' OR LOWER(gt.taskname) LIKE '%allowance%' THEN 'Construction'
                       WHEN LOWER(gt.taskname) LIKE '%furniture%' OR LOWER(gt.taskname) LIKE '%millwork%' OR LOWER(gt.taskname) LIKE '%ff&e%' OR LOWER(gt.taskname) LIKE '%ffe%'
                            OR LOWER(gt.taskname) LIKE '%artwork%' OR LOWER(gt.taskname) LIKE '% signage%' OR LOWER(gt.taskname) LIKE '%branding%'
                            OR LOWER(gt.taskname) LIKE '%audio visual%' OR LOWER(gt.taskname) LIKE '%a/v%' OR LOWER(gt.taskname) LIKE '% it %' OR LOWER(gt.taskname) LIKE '% it'
                            OR LOWER(gt.taskname) LIKE '%equipment%' OR LOWER(gt.taskname) LIKE '%appliances%' OR LOWER(gt.taskname) LIKE '%blinds%'
                            OR LOWER(gt.taskname) LIKE '%workstations%' OR LOWER(gt.taskname) LIKE '%seating%' OR LOWER(gt.taskname) LIKE '%carpet%'
                            OR LOWER(gt.taskname) LIKE '%(it)%' OR LOWER(gt.taskname) LIKE '%information technology%'
                       THEN 'FF&E + Millwork'
                       WHEN LOWER(gt.taskname) LIKE '%architect%' OR LOWER(gt.taskname) LIKE '%designer%' OR LOWER(gt.taskname) LIKE '%engineer%'
                            OR LOWER(gt.taskname) LIKE '%consultant%' OR LOWER(gt.taskname) LIKE '%expeditor%' OR LOWER(gt.taskname) LIKE '%permit%'
                            OR LOWER(gt.taskname) LIKE '% pm fee%' OR LOWER(gt.taskname) LIKE '%jll %' OR LOWER(gt.taskname) LIKE '%project management%'
                            OR LOWER(gt.taskname) LIKE '%inspection%' OR LOWER(gt.taskname) LIKE '%survey%' OR LOWER(gt.taskname) LIKE '%legal%'
                            OR LOWER(gt.taskname) LIKE '%insurance%' OR LOWER(gt.taskname) LIKE '%leed%' OR LOWER(gt.taskname) LIKE '%sustainability%'
                            OR LOWER(gt.taskname) LIKE '%design fee%' OR LOWER(gt.taskname) LIKE '%reimbursable%' OR LOWER(gt.taskname) LIKE '%admin fee%'
                            OR LOWER(gt.taskname) LIKE '%management fee%' OR LOWER(gt.taskname) LIKE '%soft cost%'
                       THEN 'Soft Costs'
                       WHEN LOWER(gt.taskname) LIKE '%general contractor%' OR LOWER(gt.taskname) LIKE '% gc %' OR LOWER(gt.taskname) LIKE 'gc %' OR LOWER(gt.taskname) LIKE '% gmp %'
                            OR LOWER(gt.taskname) LIKE '%construction %' OR LOWER(gt.taskname) LIKE '%concrete%' OR LOWER(gt.taskname) LIKE '%structural%'
                            OR LOWER(gt.taskname) LIKE '%electrical%' OR LOWER(gt.taskname) LIKE '%plumbing%' OR LOWER(gt.taskname) LIKE '%hvac%'
                            OR LOWER(gt.taskname) LIKE '%demolition%' OR LOWER(gt.taskname) LIKE '%sitework%' OR LOWER(gt.taskname) LIKE '%earthwork%'
                            OR LOWER(gt.taskname) LIKE '%general conditions%' OR LOWER(gt.taskname) LIKE '%drywall%' OR LOWER(gt.taskname) LIKE '%framing%'
                            OR LOWER(gt.taskname) LIKE '%flooring%' OR LOWER(gt.taskname) LIKE '%ceilings%' OR LOWER(gt.taskname) LIKE '%painting%'
                            OR LOWER(gt.taskname) LIKE '%fire protection%' OR LOWER(gt.taskname) LIKE '%fire sprinkler%' OR LOWER(gt.taskname) LIKE '%roofing%'
                            OR LOWER(gt.taskname) LIKE '%facade%' OR LOWER(gt.taskname) LIKE '%cladding%' OR LOWER(gt.taskname) LIKE '%hard cost%'
                            OR LOWER(TRIM(gt.taskname)) LIKE '$%'
                            OR LOWER(TRIM(gt.taskname)) RLIKE '^[0-9]+\\\\.' OR LOWER(TRIM(gt.taskname)) RLIKE '^[0-9]+\\\\s+[a-z]'
                       THEN 'Construction'
                       ELSE NULL
                   END AS cost_code_category
            FROM work_dynamics.curated.generictask gt
            INNER JOIN proj ON gt.projectidentifier = proj.workitemidentifier
            WHERE gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
        )
        SELECT
            CASE WHEN cost_code_category IS NULL THEN 'UNMAPPED' ELSE 'Mapped' END AS status,
            COUNT(*) AS task_count,
            ROUND(SUM(originalbudgetamount), 2) AS total_original
        FROM all_tasks
        GROUP BY 1
    """, "3) Mapped vs unmapped summary")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("If unmapped > 0: tasknames don't match our 3-category patterns.")
    print("Fix: Add 'Other' category for unmapped, or expand category mapping.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
