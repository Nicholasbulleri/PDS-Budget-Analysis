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
Bay Area closed USD projects missing budget in gt: what type are they?
Bay Area = US cities: Mountain View, Sunnyvale, San Bruno, San Jose, San Francisco,
Palo Alto, Oakland, Santa Clara, San Mateo, Fremont, Hayward, Redwood City,
South San Francisco, Berkeley, Alameda, Emeryville.
Breakdown by: sector, business line, and any project-type columns on curated.project.
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

# Bay Area cities (US) - match case-insensitively in SQL
BAY_AREA_CITIES = (
    "Mountain View", "Sunnyvale", "San Bruno", "San Jose", "San Francisco",
    "Palo Alto", "Oakland", "Santa Clara", "San Mateo", "Fremont", "Hayward",
    "Redwood City", "South San Francisco", "Berkeley", "Alameda", "Emeryville",
    "Milpitas", "Cupertino", "Los Altos", "Menlo Park", "San Carlos", "Belmont",
    "Foster City", "Daly City", "Colma", "Brisbane", "Burlingame", "San Leandro"
)
# SQL IN list
CITY_LIST = ", ".join(f"'{c}'" for c in BAY_AREA_CITIES)

MISSING_BUDGET_CTE = """
WITH closed_usd AS (
  SELECT
    p.id,
    COALESCE(NULLIF(TRIM(p.jllbusinessline), ''), '(No business line)') AS business_line,
    COALESCE(NULLIF(TRIM(p.sector), ''), '(No sector)') AS sector,
    COALESCE(NULLIF(TRIM(p.sourcesystem), ''), '(No source)') AS sourcesystem,
    TRIM(p.city) AS city,
    TRIM(p.country) AS country
  FROM work_dynamics.curated.project p
  WHERE p.currencytype = 'USD'
    AND p.phasetext = 'Closed'
),
projects_with_budget AS (
  SELECT DISTINCT p.id AS project_id
  FROM work_dynamics.curated.generictask gt
  INNER JOIN work_dynamics.curated.project p
    ON gt.projectidentifier = p.workitemidentifier
  WHERE p.currencytype = 'USD'
    AND p.phasetext = 'Closed'
    AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
    AND gt.originalbudgetamount IS NOT NULL
    AND gt.originalbudgetamount <> 0
),
missing AS (
  SELECT c.*
  FROM closed_usd c
  LEFT JOIN projects_with_budget w ON w.project_id = c.id
  WHERE w.project_id IS NULL
),
bay_area_missing AS (
  SELECT * FROM missing
  WHERE UPPER(TRIM(country)) = 'UNITED STATES'
    AND UPPER(TRIM(city)) IN (""" + ", ".join(f"'{c.upper()}'" for c in BAY_AREA_CITIES) + """)
)
"""


def run_query(conn, sql, title):
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    print(title)
    print("-" * 70)
    if not rows:
        print("  (no rows)")
        return rows
    for row in rows:
        print("  ", row)
    print()
    return rows


def main():
    from edp_connection import connect_databricks

    conn = connect_databricks()
    if not conn:
        print("Failed to connect.")
        return 1

    # 1) Total Bay Area missing-budget count
    q_count = MISSING_BUDGET_CTE + "SELECT COUNT(*) AS bay_area_missing FROM bay_area_missing"
    run_query(conn, q_count, "Bay Area (US) closed projects missing budget in gt – total count")

    # 2) By sector
    q_sector = MISSING_BUDGET_CTE + """
SELECT sector, COUNT(*) AS cnt, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM bay_area_missing), 1) AS pct
FROM bay_area_missing
GROUP BY sector
ORDER BY cnt DESC
"""
    run_query(conn, q_sector, "By sector")

    # 3) By business line
    q_bl = MISSING_BUDGET_CTE + """
SELECT business_line, COUNT(*) AS cnt, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM bay_area_missing), 1) AS pct
FROM bay_area_missing
GROUP BY business_line
ORDER BY cnt DESC
"""
    run_query(conn, q_bl, "By business line")

    # 4) By city (breakdown within Bay Area)
    q_city = MISSING_BUDGET_CTE + """
SELECT city, COUNT(*) AS cnt, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM bay_area_missing), 1) AS pct
FROM bay_area_missing
GROUP BY city
ORDER BY cnt DESC
"""
    run_query(conn, q_city, "By city (Bay Area)")

    # 5) Check if project has type-like columns and run by projecttypename / jllprojecttypetext / projecttype
    type_queries = []
    # Try columns that might exist on curated.project (unified table)
    for col in ["projecttypename", "jllprojecttypetext", "projecttype", "projectservicetypename", "servicetypetext", "fitouttype", "scopetext"]:
        # Add column to CTE and run – use a separate small query to test column existence
        type_queries.append((col, f"""
WITH closed_usd AS (
  SELECT p.id, TRIM(p.city) AS city, TRIM(p.country) AS country
  FROM work_dynamics.curated.project p
  WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
),
projects_with_budget AS (
  SELECT DISTINCT p.id AS project_id
  FROM work_dynamics.curated.generictask gt
  INNER JOIN work_dynamics.curated.project p ON gt.projectidentifier = p.workitemidentifier
  WHERE p.currencytype = 'USD' AND p.phasetext = 'Closed'
  AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
  AND gt.originalbudgetamount IS NOT NULL AND gt.originalbudgetamount <> 0
),
missing AS (
  SELECT c.id, c.city, c.country
  FROM closed_usd c
  LEFT JOIN projects_with_budget w ON w.project_id = c.id
  WHERE w.project_id IS NULL
),
bay_area_missing AS (
  SELECT m.id, p.{col} AS type_val
  FROM missing m
  INNER JOIN work_dynamics.curated.project p ON p.id = m.id
  WHERE UPPER(TRIM(m.country)) = 'UNITED STATES'
  AND UPPER(TRIM(m.city)) IN (""" + ", ".join(f"'{c.upper()}'" for c in BAY_AREA_CITIES) + """)
)
SELECT COALESCE(NULLIF(TRIM(CAST(type_val AS STRING)), ''), '(blank/null)') AS type_val, COUNT(*) AS cnt
FROM bay_area_missing
GROUP BY 1
ORDER BY cnt DESC
LIMIT 25
"""))

    for col_name, sql in type_queries:
        try:
            rows = run_query(conn, sql, f"By {col_name} (Bay Area missing budget)")
            if rows and any(str(r[0]) != '(blank/null)' for r in rows):
                break  # show first column that has data
        except Exception as e:
            err = str(e).lower()
            if "unresolved_column" in err or "cannot resolve" in err or "column" in err:
                pass  # column doesn't exist, skip
            else:
                print(f"  Error for {col_name}: {e}\n")

    # 6) Sector × business line for Bay Area
    q_cross = MISSING_BUDGET_CTE + """
SELECT sector, business_line, COUNT(*) AS cnt
FROM bay_area_missing
GROUP BY sector, business_line
ORDER BY cnt DESC
LIMIT 25
"""
    run_query(conn, q_cross, "Sector × business line (Bay Area missing budget)")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
