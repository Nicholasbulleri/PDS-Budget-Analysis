#!/usr/bin/env python3
"""
Analyze patterns in the 5,132 closed USD projects missing budget in generictask (gt).
Dimensions: geography (country, top cities), sector, source system, client (projectcustomer),
and business line (for comparison). Outputs counts and % of the 5,132.
"""
import os
import csv

try:
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except (PermissionError, FileNotFoundError):
        pass
except ImportError:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(SCRIPT_DIR, "missing_budget_patterns.csv")

# CTE for projects missing budget (same logic as closed_projects_missing_budget_by_business_line.sql)
MISSING_BUDGET_CTE = """
WITH closed_usd AS (
  SELECT
    p.id,
    p.workitemidentifier,
    COALESCE(NULLIF(TRIM(p.jllbusinessline), ''), '(No business line)') AS business_line,
    COALESCE(NULLIF(TRIM(p.country), ''), '(No country)') AS country,
    COALESCE(NULLIF(TRIM(p.city), ''), '(No city)') AS city,
    COALESCE(NULLIF(TRIM(p.sector), ''), '(No sector)') AS sector,
    COALESCE(NULLIF(TRIM(p.sourcesystem), ''), '(No source)') AS sourcesystem,
    COALESCE(NULLIF(TRIM(p.projectcustomer), ''), '(No client)') AS projectcustomer,
    COALESCE(NULLIF(TRIM(p.jllmarket), ''), '(No market)') AS jllmarket
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
)
"""


def run(conn, sql, title):
    from edp_connection import execute_query
    if conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
    else:
        cols, rows = execute_query(sql)
    print(title)
    print("-" * 60)
    if not rows:
        print("  (no rows)")
        return rows
    for row in rows:
        print("  ", row)
    print()
    return rows


def main():
    from edp_connection import connect_databricks, execute_query
    # Single connection to avoid repeated auth
    conn = connect_databricks()
    if not conn:
        print("Failed to connect.")
        return 1

    total_missing = 5132
    all_rows = []

    # 1) By country
    q_country = MISSING_BUDGET_CTE + """
SELECT country, COUNT(*) AS cnt,
       ROUND(100.0 * COUNT(*) / 5132, 1) AS pct_of_missing
FROM missing
GROUP BY country
ORDER BY cnt DESC
LIMIT 25
"""
    rows = run(conn, q_country, "1) By country (top 25)")
    for r in rows:
        all_rows.append(("country", r[0], r[1], r[2]))

    # 2) By sector
    q_sector = MISSING_BUDGET_CTE + """
SELECT sector, COUNT(*) AS cnt,
       ROUND(100.0 * COUNT(*) / 5132, 1) AS pct_of_missing
FROM missing
GROUP BY sector
ORDER BY cnt DESC
LIMIT 25
"""
    rows = run(conn, q_sector, "2) By sector (top 25)")
    for r in rows:
        all_rows.append(("sector", r[0], r[1], r[2]))

    # 3) By source system
    q_source = MISSING_BUDGET_CTE + """
SELECT sourcesystem, COUNT(*) AS cnt,
       ROUND(100.0 * COUNT(*) / 5132, 1) AS pct_of_missing
FROM missing
GROUP BY sourcesystem
ORDER BY cnt DESC
"""
    rows = run(conn, q_source, "3) By source system")
    for r in rows:
        all_rows.append(("source_system", r[0], r[1], r[2]))

    # 4) By business line (we already have this; include for consistency)
    q_bl = MISSING_BUDGET_CTE + """
SELECT business_line, COUNT(*) AS cnt,
       ROUND(100.0 * COUNT(*) / 5132, 1) AS pct_of_missing
FROM missing
GROUP BY business_line
ORDER BY cnt DESC
"""
    rows = run(conn, q_bl, "4) By business line")
    for r in rows:
        all_rows.append(("business_line", r[0], r[1], r[2]))

    # 5) By client (projectcustomer) - top 30
    q_client = MISSING_BUDGET_CTE + """
SELECT projectcustomer, COUNT(*) AS cnt,
       ROUND(100.0 * COUNT(*) / 5132, 1) AS pct_of_missing
FROM missing
GROUP BY projectcustomer
ORDER BY cnt DESC
LIMIT 30
"""
    rows = run(conn, q_client, "5) By client (projectcustomer, top 30)")
    for r in rows:
        all_rows.append(("client", r[0], r[1], r[2]))

    # 6) By city (top 25) - geography drill-down
    q_city = MISSING_BUDGET_CTE + """
SELECT city, country, COUNT(*) AS cnt,
       ROUND(100.0 * COUNT(*) / 5132, 1) AS pct_of_missing
FROM missing
GROUP BY city, country
ORDER BY cnt DESC
LIMIT 25
"""
    rows = run(conn, q_city, "6) By city + country (top 25)")
    for r in rows:
        all_rows.append(("city", f"{r[0]} | {r[1]}", r[2], r[3]))

    # 7) By jllmarket (top 20)
    q_market = MISSING_BUDGET_CTE + """
SELECT jllmarket, COUNT(*) AS cnt,
       ROUND(100.0 * COUNT(*) / 5132, 1) AS pct_of_missing
FROM missing
GROUP BY jllmarket
ORDER BY cnt DESC
LIMIT 20
"""
    rows = run(conn, q_market, "7) By JLL market (top 20)")
    for r in rows:
        all_rows.append(("jll_market", r[0], r[1], r[2]))

    # 8) Cross: country × business line (top 20 combinations)
    q_cross = MISSING_BUDGET_CTE + """
SELECT country, business_line, COUNT(*) AS cnt,
       ROUND(100.0 * COUNT(*) / 5132, 1) AS pct_of_missing
FROM missing
GROUP BY country, business_line
ORDER BY cnt DESC
LIMIT 20
"""
    rows = run(conn, q_cross, "8) Country × business line (top 20)")
    for r in rows:
        all_rows.append(("country_x_business_line", f"{r[0]} | {r[1]}", r[2], r[3]))

    conn.close()

    # Write combined CSV
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["segment_type", "segment_value", "closed_projects_missing_budget", "pct_of_5132"])
        w.writerows(all_rows)
    print(f"Combined results written to {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
