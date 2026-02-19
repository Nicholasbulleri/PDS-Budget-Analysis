#!/usr/bin/env python3
"""
Sector analysis part 2: project -> property/company links, jllbusinessline, propertyextended.
"""
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
    print(f"  Columns: {cols}")
    for r in rows[:25]:
        print(" ", r)
    if len(rows) > 25:
        print(f"  ... and {len(rows) - 25} more")
    return cols, rows

def main():
    print("=== Sector sources (property, company, jllbusinessline) ===\n")

    # 1) project columns that could link to property or space
    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'project'
          AND (LOWER(column_name) LIKE '%property%' OR LOWER(column_name) LIKE '%building%' OR LOWER(column_name) LIKE '%site%' OR LOWER(column_name) LIKE '%location%' OR LOWER(column_name) LIKE '%portfolio%')
        ORDER BY ordinal_position
    """, "1) project: property/building/site columns")

    # 2) jllbusinessline population for Closed USD (could be sector proxy?)
    run("""
        SELECT jllbusinessline, COUNT(*) AS cnt
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND phasetext = 'Closed'
        GROUP BY jllbusinessline
        ORDER BY cnt DESC
    """, "2) Closed USD: jllbusinessline distribution")

    # 3) propertyextended: key and industrysector
    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'propertyextended'
          AND (LOWER(column_name) LIKE '%id%' OR LOWER(column_name) LIKE '%identifier%' OR LOWER(column_name) LIKE '%industry%' OR LOWER(column_name) LIKE '%sector%')
        ORDER BY ordinal_position
    """, "3) propertyextended: id and industry/sector columns")

    # 4) Can we join project to propertyextended? (e.g. project.propertyidentifier = propertyextended.xxx)
    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'propertyextended'
        ORDER BY ordinal_position
        LIMIT 30
    """, "4) propertyextended: first 30 columns")

    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'project'
          AND LOWER(column_name) LIKE '%property%'
        ORDER BY ordinal_position
    """, "5) project: property-related columns")

    # 6) Join project -> propertyextended on common key and industrysector coverage for Closed USD
    run("""
        SELECT 
            COUNT(DISTINCT p.id) AS closed_usd_projects,
            COUNT(DISTINCT CASE WHEN pe.industrysectorname IS NOT NULL AND TRIM(pe.industrysectorname) <> '' THEN p.id END) AS with_property_sector
        FROM work_dynamics.curated.project p
        LEFT JOIN work_dynamics.curated.propertyextended pe ON p.propertyidentifier = pe.propertyidentifier
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
    """, "6) Closed USD: join to propertyextended on propertyidentifier -> industrysectorname")

    # 7) If join works: sample industrysectorname values
    run("""
        SELECT pe.industrysectorname, pe.industrysector, COUNT(DISTINCT p.id) AS cnt
        FROM work_dynamics.curated.project p
        INNER JOIN work_dynamics.curated.propertyextended pe ON p.propertyidentifier = pe.propertyidentifier
        WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
          AND pe.industrysectorname IS NOT NULL AND TRIM(pe.industrysectorname) <> ''
        GROUP BY pe.industrysectorname, pe.industrysector
        ORDER BY cnt DESC
    """, "7) Closed USD: industrysectorname from propertyextended (when join works)")

    # 8) phub_oneviewclientproperty: how to link to project?
    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'phub_oneviewclientproperty'
        ORDER BY ordinal_position
        LIMIT 25
    """, "8) phub_oneviewclientproperty: columns")

    # 9) company table: full column list for sector/segment
    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'company'
        ORDER BY ordinal_position
    """, "9) company: all columns")

    # 10) project.companyidentifier -> company: does company have sector-like field?
    run("""
        SELECT c.column_name
        FROM system.information_schema.columns c
        WHERE c.table_catalog = 'work_dynamics' AND c.table_schema = 'curated' AND c.table_name = 'company'
          AND (LOWER(c.column_name) LIKE '%sector%' OR LOWER(c.column_name) LIKE '%segment%' OR LOWER(c.column_name) LIKE '%industry%' OR LOWER(c.column_name) LIKE '%business%' OR LOWER(c.column_name) = 'id' OR LOWER(c.column_name) LIKE '%identifier%')
        ORDER BY c.ordinal_position
    """, "10) company: sector/segment/industry/id columns")

    print("\n=== Done ===")

if __name__ == "__main__":
    main()
