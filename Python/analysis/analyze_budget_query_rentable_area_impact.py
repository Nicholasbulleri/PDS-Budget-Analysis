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
Analyze impact of adding rentablearea to budget query (sector + project type).
Compares: gross->usable only vs gross->usable->rentable.
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
    print("  " + " | ".join(str(c) for c in columns))
    print("  " + "-" * 60)
    for row in rows:
        print("  ", row)
    return rows


def main():
    # Old area: COALESCE(NULLIF(grossarea, 0), usablearea)
    # New area: COALESCE(NULLIF(grossarea, 0), NULLIF(usablearea, 0), NULLIF(rentablearea, 0))

    # 1) Row count comparison
    run("""
        WITH base_old AS (
            SELECT p.id AS project_id, gt.originalbudgetamount, gt.totalprojectedbudgetamount,
                   COALESCE(NULLIF(p.grossarea, 0), p.usablearea) AS area
            FROM work_dynamics.curated.generictask gt
            INNER JOIN work_dynamics.curated.project p ON gt.projectidentifier = p.workitemidentifier
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
              AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
              AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) IS NOT NULL
              AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) > 0
        ),
        base_new AS (
            SELECT p.id AS project_id, gt.originalbudgetamount, gt.totalprojectedbudgetamount,
                   COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) AS area
            FROM work_dynamics.curated.generictask gt
            INNER JOIN work_dynamics.curated.project p ON gt.projectidentifier = p.workitemidentifier
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
              AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
              AND COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) IS NOT NULL
              AND COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) > 0
        )
        SELECT
            'Old (gross->usable)' AS area_logic,
            COUNT(DISTINCT project_id) AS project_count,
            COUNT(*) AS task_row_count,
            ROUND(SUM(originalbudgetamount), 2) AS total_original_budget,
            ROUND(SUM(totalprojectedbudgetamount), 2) AS total_projected_budget,
            ROUND(SUM(area), 2) AS total_area
        FROM base_old
        UNION ALL
        SELECT
            'New (gross->usable->rentable)' AS area_logic,
            COUNT(DISTINCT project_id),
            COUNT(*),
            ROUND(SUM(originalbudgetamount), 2),
            ROUND(SUM(totalprojectedbudgetamount), 2),
            ROUND(SUM(area), 2)
        FROM base_new
    """, "1) Base comparison: project count, task rows, totals")

    # 2) Projects added by rentablearea (in new but not in old)
    run("""
        WITH base_old AS (
            SELECT DISTINCT p.id AS project_id
            FROM work_dynamics.curated.generictask gt
            INNER JOIN work_dynamics.curated.project p ON gt.projectidentifier = p.workitemidentifier
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
              AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
              AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) IS NOT NULL
              AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) > 0
        ),
        base_new AS (
            SELECT DISTINCT p.id AS project_id
            FROM work_dynamics.curated.generictask gt
            INNER JOIN work_dynamics.curated.project p ON gt.projectidentifier = p.workitemidentifier
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
              AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
              AND COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) IS NOT NULL
              AND COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) > 0
        )
        SELECT COUNT(*) AS projects_added_by_rentablearea
        FROM base_new n
        LEFT JOIN base_old o ON o.project_id = n.project_id
        WHERE o.project_id IS NULL
    """, "2) Projects added (have rentablearea but not gross/usable)")

    # 3) By sourcesystem: projects added
    run("""
        WITH base_old AS (
            SELECT DISTINCT p.id AS project_id, p.sourcesystem
            FROM work_dynamics.curated.generictask gt
            INNER JOIN work_dynamics.curated.project p ON gt.projectidentifier = p.workitemidentifier
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
              AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
              AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) IS NOT NULL
              AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) > 0
        ),
        base_new AS (
            SELECT DISTINCT p.id AS project_id, p.sourcesystem
            FROM work_dynamics.curated.generictask gt
            INNER JOIN work_dynamics.curated.project p ON gt.projectidentifier = p.workitemidentifier
            WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
              AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
              AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
              AND COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) IS NOT NULL
              AND COALESCE(NULLIF(p.grossarea, 0), NULLIF(p.usablearea, 0), NULLIF(p.rentablearea, 0)) > 0
        )
        SELECT n.sourcesystem, COUNT(*) AS projects_added
        FROM base_new n
        LEFT JOIN base_old o ON o.project_id = n.project_id
        WHERE o.project_id IS NULL
        GROUP BY n.sourcesystem
        ORDER BY projects_added DESC
    """, "3) Projects added by rentablearea, by sourcesystem")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Budget query now uses: grossarea -> usablearea -> rentablearea")
    print("Run the budget query script to regenerate CSV/Excel with new logic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
