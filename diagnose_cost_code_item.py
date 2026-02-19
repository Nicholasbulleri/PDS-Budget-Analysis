#!/usr/bin/env python3
"""Check if Cost Code Item has budget amount columns populated for Closed USD."""
import os
try:
    from dotenv import load_dotenv
    try: load_dotenv()
    except (PermissionError, FileNotFoundError): pass
except ImportError: pass

def run(q, name):
    from edp_connection import execute_query
    cols, rows = execute_query(q)
    print(f"\n{name}\n  {cols}")
    for r in rows[:15]:
        print(" ", r)
    if len(rows) > 15:
        print(f"  ... +{len(rows)-15} more")
    return rows

def main():
    # Cost Code Item: non-zero originalbudgetamount?
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
          AND gt.internaltasktypetext = 'Cost Code Item'
        GROUP BY 1
    """, "Cost Code Item: originalbudgetamount NULL/0/non-zero (rows, projects)")

    # Distinct projects with Cost Code Item AND non-zero original
    run("""
        SELECT COUNT(DISTINCT p.id) AS projects_with_cost_code_item_nonzero_budget
        FROM work_dynamics.curated.generictask gt
        INNER JOIN work_dynamics.curated.project p
            ON gt.projectidentifier = p.workitemidentifier
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
          AND gt.internaltasktypetext = 'Cost Code Item'
          AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
    """, "Closed USD projects with Cost Code Item + non-zero originalbudgetamount")

if __name__ == "__main__":
    main()
