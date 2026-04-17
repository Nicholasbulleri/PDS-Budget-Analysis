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

"""Why project->propertyextended join fails; jllbusinessline as sector proxy."""
import os
try:
    from dotenv import load_dotenv
    try: load_dotenv()
    except (PermissionError, FileNotFoundError): pass
except ImportError: pass

def run(q, name):
    from edp_connection import execute_query
    cols, rows = execute_query(q)
    print(f"\n{name}")
    print(f"  {cols}")
    for r in rows[:20]:
        print(" ", r)
    if len(rows) > 20:
        print(f"  ... +{len(rows)-20} more")
    return rows

def main():
    # Closed USD: how many have propertyidentifier populated?
    run("""
        SELECT 
            CASE WHEN propertyidentifier IS NOT NULL AND TRIM(propertyidentifier) <> '' THEN 'has_property_id' ELSE 'null_or_blank' END AS prop,
            COUNT(*) AS cnt
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND phasetext = 'Closed'
        GROUP BY 1
    """, "1) Closed USD: propertyidentifier populated?")

    # propertyextended: sample propertyidentifier and industrysectorname
    run("""
        SELECT propertyidentifier, industrysectorname, industrysector, sourcesystem
        FROM work_dynamics.curated.propertyextended
        WHERE industrysectorname IS NOT NULL AND TRIM(industrysectorname) <> ''
        LIMIT 15
    """, "2) propertyextended: sample propertyidentifier format")

    # project (Closed USD): sample propertyidentifier format
    run("""
        SELECT propertyidentifier, sector, sourcesystem
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND phasetext = 'Closed' AND propertyidentifier IS NOT NULL AND TRIM(propertyidentifier) <> ''
        LIMIT 15
    """, "3) project Closed USD: sample propertyidentifier format")

    # Do any project.propertyidentifier values exist in propertyextended?
    run("""
        SELECT COUNT(*) AS matching_projects
        FROM work_dynamics.curated.project p
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
          AND EXISTS (SELECT 1 FROM work_dynamics.curated.propertyextended pe WHERE pe.propertyidentifier = p.propertyidentifier)
    """, "4) Closed USD projects with propertyidentifier in propertyextended")

    # propertyextended: does it use a different key (e.g. sourcepropertynumber = project.sourceprojectid)?
    run("""
        SELECT p.propertyidentifier, p.sourceprojectid, pe.propertyidentifier AS pe_prop_id, pe.sourcepropertynumber, pe.industrysectorname
        FROM work_dynamics.curated.project p
        INNER JOIN work_dynamics.curated.propertyextended pe ON pe.sourcepropertynumber = CAST(p.sourceprojectid AS STRING)
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
        LIMIT 10
    """, "5) Join project to propertyextended on sourceprojectid = sourcepropertynumber?")

    # jllbusinessline: map to sector-like for reporting (PDS - Healthcare -> Healthcare, PDS - Office -> Office, etc.)
    run("""
        SELECT jllbusinessline, COUNT(*) AS cnt
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND phasetext = 'Closed' AND jllbusinessline IS NOT NULL
        GROUP BY jllbusinessline
        ORDER BY cnt DESC
    """, "6) jllbusinessline values (Closed USD) - can infer sector?")

    # sourcesystem for Closed: Clarizen vs Ingenious (we know Cost Code Item = Clarizen)
    run("""
        SELECT sourcesystem, COUNT(*) AS cnt,
               SUM(CASE WHEN sector IS NOT NULL AND TRIM(sector) <> '' THEN 1 ELSE 0 END) AS with_sector
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND phasetext = 'Closed'
        GROUP BY sourcesystem
    """, "7) Closed USD: sector by sourcesystem")

    print("\n=== Done ===")

if __name__ == "__main__":
    main()
