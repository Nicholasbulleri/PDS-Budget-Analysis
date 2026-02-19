#!/usr/bin/env python3
"""
Run a fresh count of projects in work_dynamics.curated.project.
Outputs: total, by source system, and Ingenious breakdown (status, with budget, with budgetdetail).
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


def main():
    from edp_connection import execute_query

    print("Project counts – work_dynamics.curated")
    print("=" * 60)

    # 1. Total projects
    q_total = "SELECT COUNT(*) AS cnt FROM work_dynamics.curated.project"
    cols, rows = execute_query(q_total)
    total = rows[0][0] if rows else 0
    print(f"Total projects: {total:,}")

    # 2. By source system
    q_by_source = """
        SELECT sourcesystem, COUNT(*) AS cnt
        FROM work_dynamics.curated.project
        GROUP BY sourcesystem
        ORDER BY cnt DESC
    """
    cols, rows = execute_query(q_by_source)
    print("\nBy source system:")
    for row in rows:
        print(f"  {row[0] or '(NULL)'}: {row[1]:,}")

    # 3. Ingenious: total and by status (excluding requested, cancelled, draft)
    q_ing = """
        SELECT
            COUNT(*) AS total_ingenious,
            COUNT(CASE WHEN LOWER(COALESCE(phasetext,'')) NOT IN ('requested','cancelled','draft') THEN 1 END) AS active_status
        FROM work_dynamics.curated.project
        WHERE sourcesystem = 'ingenious'
    """
    cols, rows = execute_query(q_ing)
    if rows:
        print(f"\nIngenious: total {rows[0][0]:,}, with active status (excl. requested/cancelled/draft): {rows[0][1]:,}")

    q_ing_status = """
        SELECT phasetext, COUNT(*) AS cnt
        FROM work_dynamics.curated.project
        WHERE sourcesystem = 'ingenious'
        GROUP BY phasetext
        ORDER BY cnt DESC
    """
    cols, rows = execute_query(q_ing_status)
    print("\nIngenious by phasetext:")
    for row in rows:
        print(f"  {row[0] or '(NULL)'}: {row[1]:,}")

    # 4. Ingenious (active status): with originalbudgetamount vs with budgetdetail
    q_with_amt = """
        SELECT COUNT(DISTINCT p.id)
        FROM work_dynamics.curated.project p
        WHERE p.sourcesystem = 'ingenious'
          AND LOWER(COALESCE(p.phasetext,'')) NOT IN ('requested','cancelled','draft')
          AND p.originalbudgetamount IS NOT NULL
    """
    cols, rows = execute_query(q_with_amt)
    with_amt = rows[0][0] if rows else 0

    q_with_bd = """
        SELECT COUNT(DISTINCT bd.projectidentifier)
        FROM work_dynamics.curated.budgetdetail bd
        INNER JOIN work_dynamics.curated.project p ON p.id = bd.projectidentifier AND p.sourcesystem = 'ingenious'
        WHERE bd.sourcesystem = 'ingenious'
          AND LOWER(COALESCE(p.phasetext,'')) NOT IN ('requested','cancelled','draft')
    """
    cols, rows = execute_query(q_with_bd)
    with_bd = rows[0][0] if rows else 0

    print("\nIngenious (active status, excl. requested/cancelled/draft):")
    print(f"  Projects with originalbudgetamount: {with_amt:,}")
    print(f"  Projects with at least one budgetdetail record: {with_bd:,}")
    print(f"  With amount but no budgetdetail: {with_amt - with_bd:,}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
