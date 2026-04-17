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
Analyze curated budgetdetail: how many Ingenious projects that are Closed or In-Progress
have at least one budget detail record. Link: project.id = budgetdetail.projectidentifier.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))
except (ImportError, PermissionError, FileNotFoundError):
    pass


def main():
    from edp_connection import execute_query

    print("Ingenious (Closed / In-Progress) projects with ≥1 budgetdetail record")
    print("work_dynamics.curated.project ↔ work_dynamics.curated.budgetdetail")
    print("=" * 60)

    # Total count
    q_total = """
        SELECT COUNT(DISTINCT p.id) AS cnt
        FROM work_dynamics.curated.project p
        INNER JOIN work_dynamics.curated.budgetdetail bd
            ON bd.projectidentifier = p.id
            AND bd.sourcesystem = 'ingenious'
        WHERE p.sourcesystem = 'ingenious'
          AND LOWER(TRIM(COALESCE(p.phasetext, ''))) IN ('closed', 'in progress')
    """
    cols, rows = execute_query(q_total)
    total = rows[0][0] if rows else 0
    print(f"\nIngenious closed or in-progress projects with ≥1 budget detail record: {total:,}")

    # Breakdown by phasetext
    q_breakdown = """
        SELECT p.phasetext, COUNT(DISTINCT p.id) AS project_count
        FROM work_dynamics.curated.project p
        INNER JOIN work_dynamics.curated.budgetdetail bd
            ON bd.projectidentifier = p.id
            AND bd.sourcesystem = 'ingenious'
        WHERE p.sourcesystem = 'ingenious'
          AND LOWER(TRIM(COALESCE(p.phasetext, ''))) IN ('closed', 'in progress')
        GROUP BY p.phasetext
        ORDER BY project_count DESC
    """
    cols, rows = execute_query(q_breakdown)
    print("\nBy phase:")
    for row in rows:
        print(f"  {row[0] or '(NULL)'}: {row[1]:,}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
