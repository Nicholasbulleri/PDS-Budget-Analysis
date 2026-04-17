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
Analyze Ingenious closed USD projects: area + budget funnel.
Area: grossarea -> usablearea -> rentablearea (first non-null, non-zero).
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


def run(sql, title):
    from edp_connection import execute_query
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    columns, rows = execute_query(sql)
    if not rows:
        print("  (no rows)")
        return rows
    # Print header
    print("  " + " | ".join(str(c) for c in columns))
    print("  " + "-" * 60)
    for row in rows:
        print("  ", row)
    return rows


def main():
    # 1) Total Ingenious closed USD projects
    run("""
        SELECT sourcesystem, COUNT(*) AS total_closed_usd
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND phasetext = 'Closed'
        GROUP BY sourcesystem
        ORDER BY total_closed_usd DESC
    """, "1) Closed USD projects by sourcesystem (all)")

    # 2) Ingenious: area breakdown (gross -> usable -> rentable)
    run("""
        SELECT
            CASE
                WHEN COALESCE(NULLIF(grossarea, 0), NULLIF(usablearea, 0), NULLIF(rentablearea, 0)) IS NULL THEN 'NULL (no area)'
                WHEN COALESCE(NULLIF(grossarea, 0), NULLIF(usablearea, 0), NULLIF(rentablearea, 0)) <= 0 THEN 'Zero or negative'
                ELSE 'Has positive area'
            END AS area_status,
            COUNT(*) AS cnt
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND phasetext = 'Closed' AND sourcesystem = 'ingenious'
        GROUP BY 1
        ORDER BY cnt DESC
    """, "2) Ingenious Closed USD: area status (gross->usable->rentable)")

    # 3) Ingenious: has budget in generictask? (before area filter)
    run("""
        SELECT
            CASE WHEN w.project_id IS NOT NULL THEN 'Has budget in gt' ELSE 'No budget in gt' END AS budget_status,
            COUNT(*) AS cnt
        FROM work_dynamics.curated.project p
        LEFT JOIN (
            SELECT DISTINCT p2.id AS project_id
            FROM work_dynamics.curated.generictask gt
            INNER JOIN work_dynamics.curated.project p2 ON gt.projectidentifier = p2.workitemidentifier
            WHERE p2.currencytype = 'USD' AND p2.phasetext = 'Closed' AND p2.sourcesystem = 'ingenious'
              AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
        ) w ON w.project_id = p.id
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed' AND p.sourcesystem = 'ingenious'
        GROUP BY 1
    """, "3) Ingenious Closed USD: has budget in generictask?")

    # 4) Ingenious: funnel - area + budget combined
    run("""
        WITH ingenious_closed AS (
            SELECT p.id, p.workitemidentifier,
                   COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) AS area
            FROM work_dynamics.curated.project p
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed' AND p.sourcesystem = 'ingenious'
        ),
        with_budget AS (
            SELECT DISTINCT ic.id
            FROM ingenious_closed ic
            INNER JOIN work_dynamics.curated.generictask gt ON gt.projectidentifier = ic.workitemidentifier
            WHERE gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
        )
        SELECT
            'Total Ingenious Closed USD' AS stage, COUNT(*) AS cnt FROM ingenious_closed
        UNION ALL
        SELECT '  -> With positive area', COUNT(*) FROM ingenious_closed WHERE area IS NOT NULL AND area > 0
        UNION ALL
        SELECT '  -> With budget in gt', COUNT(*) FROM with_budget
        UNION ALL
        SELECT '  -> With area AND budget (final)', COUNT(*)
        FROM ingenious_closed ic
        INNER JOIN with_budget wb ON wb.id = ic.id
        WHERE ic.area IS NOT NULL AND ic.area > 0
    """, "4) Ingenious funnel: area + budget")

    # 5) Ingenious with budget but missing area - how many?
    run("""
        SELECT COUNT(DISTINCT p.id) AS ingenious_with_budget_missing_area
        FROM work_dynamics.curated.project p
        INNER JOIN work_dynamics.curated.generictask gt ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed' AND p.sourcesystem = 'ingenious'
          AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
          AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
          AND (COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) IS NULL
               OR COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) <= 0)
    """, "5) Ingenious: has budget but missing/zero area (excluded from results)")

    # 6) Compare: Clarizen vs Ingenious area population (gross->usable->rentable)
    run("""
        SELECT sourcesystem,
               COUNT(*) AS total,
               SUM(CASE WHEN COALESCE(NULLIF(grossarea, 0), NULLIF(usablearea, 0), NULLIF(rentablearea, 0)) IS NOT NULL
                        AND COALESCE(NULLIF(grossarea, 0), NULLIF(usablearea, 0), NULLIF(rentablearea, 0)) > 0 THEN 1 ELSE 0 END) AS with_positive_area,
               ROUND(100.0 * SUM(CASE WHEN COALESCE(NULLIF(grossarea, 0), NULLIF(usablearea, 0), NULLIF(rentablearea, 0)) IS NOT NULL
                        AND COALESCE(NULLIF(grossarea, 0), NULLIF(usablearea, 0), NULLIF(rentablearea, 0)) > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_with_area
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND phasetext = 'Closed'
          AND sourcesystem IN ('ingenious', 'clarizen')
        GROUP BY sourcesystem
    """, "6) Area population: Ingenious vs Clarizen (gross->usable->rentable)")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Area = grossarea -> usablearea -> rentablearea (first non-null, non-zero).")
    print("Final count = projects with both positive area AND budget in generictask.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
