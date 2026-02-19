#!/usr/bin/env python3
"""Quick check: source system for Cost Code Item vs budget in Closed USD budget query."""
import os
try:
    from dotenv import load_dotenv
    try: load_dotenv()
    except (PermissionError, FileNotFoundError): pass
except ImportError: pass

def run(q, name):
    from edp_connection import execute_query
    cols, rows = execute_query(q)
    print(f"\n{name}\n  Columns: {cols}")
    for r in rows:
        print(" ", r)
    return rows

def main():
    # 1) Check if generictask has source column(s)
    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'generictask'
          AND LOWER(column_name) LIKE '%source%'
        ORDER BY ordinal_position
    """, "generictask columns containing 'source'")

    # 2) Same for project
    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'project'
          AND LOWER(column_name) LIKE '%source%'
        ORDER BY ordinal_position
    """, "project columns containing 'source'")

    # 3) For the same filter as Closed budget query: group by internaltasktypetext + gt.sourcesystem
    run("""
        SELECT 
            gt.internaltasktypetext,
            gt.sourcesystem,
            COUNT(*) AS row_count,
            COUNT(DISTINCT p.id) AS project_count
        FROM work_dynamics.curated.generictask gt
        INNER JOIN work_dynamics.curated.project p
            ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD'
          AND p.phasetext = 'Closed'
          AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
          AND gt.originalbudgetamount IS NOT NULL
          AND gt.originalbudgetamount <> 0
        GROUP BY gt.internaltasktypetext, gt.sourcesystem
        ORDER BY gt.internaltasktypetext, 3 DESC
    """, "By internaltasktypetext + gt.sourcesystem")

if __name__ == "__main__":
    main()
