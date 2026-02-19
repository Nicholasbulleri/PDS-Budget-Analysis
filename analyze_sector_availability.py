#!/usr/bin/env python3
"""
Analyze sector availability: Construct vs Closed, and whether sector exists elsewhere.
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
    for r in rows[:30]:
        print(" ", r)
    if len(rows) > 30:
        print(f"  ... and {len(rows) - 30} more")
    return cols, rows

def main():
    print("=== Sector availability analysis ===\n")

    # 1) project.sector: non-null rate by phase (USD)
    run("""
        SELECT phasetext, 
               COUNT(*) AS total_projects,
               SUM(CASE WHEN sector IS NOT NULL AND TRIM(sector) <> '' THEN 1 ELSE 0 END) AS with_sector,
               ROUND(100.0 * SUM(CASE WHEN sector IS NOT NULL AND TRIM(sector) <> '' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_with_sector
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD'
        GROUP BY phasetext
        ORDER BY total_projects DESC
    """, "1) project.sector by phase (USD)")

    # 2) Columns on project that contain 'sector' or similar
    run("""
        SELECT column_name, data_type
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'project'
          AND (LOWER(column_name) LIKE '%sector%' OR LOWER(column_name) LIKE '%segment%' OR LOWER(column_name) LIKE '%industry%' OR LOWER(column_name) LIKE '%business%')
        ORDER BY ordinal_position
    """, "2) project table: sector/segment/industry columns")

    # 3) Sample of Closed USD projects: sector and other identifiers (source, workitemidentifier, etc.)
    run("""
        SELECT sector, sourcesystem, workitemidentifier, sourceprojectid, 
               COUNT(*) OVER (PARTITION BY sector) AS cnt_sector
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND phasetext = 'Closed'
        LIMIT 20
    """, "3) Sample Closed USD: sector, sourcesystem, identifiers")

    # 4) Tables that reference project or have sector (information_schema or SHOW)
    run("""
        SELECT table_name, column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated'
          AND LOWER(column_name) LIKE '%sector%'
        ORDER BY table_name, ordinal_position
    """, "4) All curated tables with a 'sector' column")

    # 5) Company / property / client tables that might have sector and link to project
    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'company'
          AND LOWER(column_name) IN ('sector', 'segment', 'industry', 'workitemidentifier', 'id', 'companyidentifier')
        ORDER BY ordinal_position
    """, "5) company table: sector/link columns")

    # 6) If project has company/organization link, check company.sector
    run("""
        SELECT column_name
        FROM system.information_schema.columns
        WHERE table_catalog = 'work_dynamics' AND table_schema = 'curated' AND table_name = 'project'
          AND (LOWER(column_name) LIKE '%company%' OR LOWER(column_name) LIKE '%org%' OR LOWER(column_name) LIKE '%client%' OR LOWER(column_name) LIKE '%account%')
        ORDER BY ordinal_position
    """, "6) project: company/org/client/account columns")

    # 7) Distinct sector values for Construct vs Closed (to see if same domain)
    run("""
        SELECT phasetext, sector, COUNT(*) AS cnt
        FROM work_dynamics.curated.project
        WHERE currencytype = 'USD' AND sector IS NOT NULL AND TRIM(sector) <> ''
        GROUP BY phasetext, sector
        ORDER BY phasetext, cnt DESC
    """, "7) Distinct sector values by phase (USD, non-null)")

    # 8) Same project in Construct vs Closed: does sector differ? (projects that appear in both phases - if key exists)
    # We may not have same project in two phases; instead check: for Closed projects missing sector, is there a Construct record with sector we could use (same project id)?
    run("""
        SELECT 
            COUNT(DISTINCT p_closed.id) AS closed_projects_missing_sector,
            COUNT(DISTINCT p_const.id) AS construct_projects_with_sector
        FROM work_dynamics.curated.project p_closed
        LEFT JOIN work_dynamics.curated.project p_const 
          ON p_const.workitemidentifier = p_closed.workitemidentifier AND p_const.phasetext = 'Construct' AND p_const.currencytype = 'USD' AND p_const.sector IS NOT NULL AND TRIM(p_const.sector) <> ''
        WHERE p_closed.currencytype = 'USD' AND p_closed.phasetext = 'Closed'
          AND (p_closed.sector IS NULL OR TRIM(p_closed.sector) = '')
    """, "8) Closed missing sector: how many have same workitemidentifier in Construct with sector?")

    # 9) If 8 shows overlap: we can fill sector from Construct by workitemidentifier
    run("""
        SELECT p_const.sector, COUNT(DISTINCT p_closed.id) AS closed_projects_fillable
        FROM work_dynamics.curated.project p_closed
        INNER JOIN work_dynamics.curated.project p_const 
          ON p_const.workitemidentifier = p_closed.workitemidentifier AND p_const.phasetext = 'Construct' AND p_const.currencytype = 'USD' AND p_const.sector IS NOT NULL AND TRIM(p_const.sector) <> ''
        WHERE p_closed.currencytype = 'USD' AND p_closed.phasetext = 'Closed'
          AND (p_closed.sector IS NULL OR TRIM(p_closed.sector) = '')
        GROUP BY p_const.sector
        ORDER BY closed_projects_fillable DESC
    """, "9) Sector values we could backfill for Closed (from Construct same workitemidentifier)")

    print("\n=== Done ===")

if __name__ == "__main__":
    main()
