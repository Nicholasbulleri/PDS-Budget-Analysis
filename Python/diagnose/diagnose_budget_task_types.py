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
Check internaltasktypetext and originalbudgetamount for Closed USD in generictask.
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
    print(f"\n{name}\n  Columns: {cols}")
    for r in rows[:25]:
        print(" ", r)
    if len(rows) > 25:
        print(f"  ... and {len(rows) - 25} more rows")
    return rows


def main():
    print("Closed USD in generictask: task types and budget amounts\n")

    # 1) Distinct internaltasktypetext for Closed USD
    run("""
        SELECT gt.internaltasktypetext, COUNT(*) AS cnt, COUNT(DISTINCT p.id) AS projects
        FROM work_dynamics.curated.generictask gt
        INNER JOIN work_dynamics.curated.project p
            ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
        GROUP BY gt.internaltasktypetext
        ORDER BY cnt DESC
    """, "internaltasktypetext for Closed USD (row count, distinct projects)")

    # 2) For rows where internaltasktypetext = 'budget': distribution of originalbudgetamount
    run("""
        SELECT 
            CASE WHEN gt.originalbudgetamount IS NULL THEN 'NULL'
                 WHEN gt.originalbudgetamount = 0 THEN '0'
                 ELSE 'non-zero' END AS amount_type,
            COUNT(*) AS cnt,
            COUNT(DISTINCT p.id) AS projects
        FROM work_dynamics.curated.generictask gt
        INNER JOIN work_dynamics.curated.project p
            ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
          AND gt.internaltasktypetext = 'budget'
        GROUP BY 1
    """, "Budget rows: originalbudgetamount NULL / 0 / non-zero")

    # 3) Sample of task types that might be budget-related (e.g. contain 'budget')
    run("""
        SELECT gt.internaltasktypetext, COUNT(*) AS cnt
        FROM work_dynamics.curated.generictask gt
        INNER JOIN work_dynamics.curated.project p
            ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
          AND LOWER(COALESCE(gt.internaltasktypetext, '')) LIKE '%budget%'
        GROUP BY gt.internaltasktypetext
        ORDER BY cnt DESC
    """, "Task types containing 'budget' for Closed USD")


if __name__ == "__main__":
    main()
