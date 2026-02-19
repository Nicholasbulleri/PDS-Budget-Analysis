#!/usr/bin/env python3
"""
Diagnose why budget query returns fewer projects than total Closed USD projects.
Checks: total Closed USD projects, how many have generictask budget rows, join key alignment.
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


def run(q, name):
    from edp_connection import execute_query
    cols, rows = execute_query(q)
    val = rows[0][0] if rows else None
    print(f"  {name}: {val}")
    return val


def main():
    print("Diagnosing budget query coverage (Closed, USD)...\n")

    # 1) Total Closed USD projects (your 55,138)
    run("""
        SELECT COUNT(*) AS cnt
        FROM work_dynamics.curated.project p
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
    """, "Total Closed USD projects (project table)")

    # 2) Distinct projects that have at least one generictask row (budget, non-zero original)
    run("""
        SELECT COUNT(DISTINCT p.id) AS cnt
        FROM work_dynamics.curated.generictask gt
        INNER JOIN work_dynamics.curated.project p
            ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD'
          AND p.phasetext = 'Closed'
          AND gt.internaltasktypetext = 'budget'
          AND gt.originalbudgetamount <> 0
    """, "Closed USD projects WITH ≥1 generictask (budget, non-zero)")

    # 3) Total generictask rows (budget, non-zero) for Closed USD projects
    run("""
        SELECT COUNT(*) AS cnt
        FROM work_dynamics.curated.generictask gt
        INNER JOIN work_dynamics.curated.project p
            ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD'
          AND p.phasetext = 'Closed'
          AND gt.internaltasktypetext = 'budget'
          AND gt.originalbudgetamount <> 0
    """, "Total generictask rows (budget, non-zero) for those projects")

    # 4) Generictask rows for Closed USD without requiring budget type (to see if join/key is the issue)
    run("""
        SELECT COUNT(*) AS cnt
        FROM work_dynamics.curated.generictask gt
        INNER JOIN work_dynamics.curated.project p
            ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
    """, "Total generictask rows (any type) for Closed USD projects")

    # 5) Distinct Closed USD projects that have ANY generictask row (any type)
    run("""
        SELECT COUNT(DISTINCT p.id) AS cnt
        FROM work_dynamics.curated.generictask gt
        INNER JOIN work_dynamics.curated.project p
            ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
    """, "Closed USD projects with ≥1 generictask (any type)")

    # 6) Sum of project_count from the actual budget query (should match distinct projects with budget)
    run("""
        SELECT SUM(project_count) AS cnt
        FROM (
            SELECT COUNT(p.id) AS project_count
            FROM work_dynamics.curated.generictask gt
            INNER JOIN work_dynamics.curated.project p
                ON gt.projectidentifier = p.workitemidentifier
            WHERE p.currencytype = 'USD'
              AND p.phasetext = 'Closed'
              AND gt.internaltasktypetext = 'budget'
              AND gt.originalbudgetamount <> 0
            GROUP BY gt.costcode, gt.taskname, p.city, p.country, p.sector
        ) x
    """, "Sum(project_count) from grouped budget query (total project-row involvements)")

    print("\nDone. If 'Closed USD projects WITH ≥1 generictask' << 55,138, the gap is missing gt records or join key.")


if __name__ == "__main__":
    main()
