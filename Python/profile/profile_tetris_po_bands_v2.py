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
Tetris PO Band Analysis v2
- Includes all projects (with and without POs)
- Shows % with PO coverage
- Adds sector (Asset_Class, Industry) and location (Country, City) to bands
"""
import sys, os

from edp_connection import execute_query

FQ = "edp_sourcesystem.tetris"

BAND_CASE = """
  CASE
    WHEN po.total_po_amt IS NULL THEN '0. No POs'
    WHEN po.total_po_amt < 50000 THEN '1. <50K'
    WHEN po.total_po_amt < 250000 THEN '2. 50K-250K'
    WHEN po.total_po_amt < 1000000 THEN '3. 250K-1M'
    WHEN po.total_po_amt < 5000000 THEN '4. 1M-5M'
    WHEN po.total_po_amt < 10000000 THEN '5. 5M-10M'
    ELSE '6. 10M+'
  END
"""

BASE_JOIN = f"""
FROM {FQ}.tetris_project p
LEFT JOIN (
  SELECT
    TS_Project_ID,
    COUNT(*) AS po_count,
    SUM(CAST(REGEXP_REPLACE(PO_Amount, '[^0-9.-]', '') AS DOUBLE)) AS total_po_amt
  FROM {FQ}.tetris_purchaseorder
  WHERE udp_delete_flag = 'N'
  GROUP BY TS_Project_ID
) po ON p.Project_TS_ID = po.TS_Project_ID
WHERE p.udp_delete_flag = 'N'
"""


def run(query, label):
    print(f"\n{'='*90}")
    print(f"  {label}")
    print(f"{'='*90}")
    cols, rows = execute_query(query)
    print(f"  Columns: {cols}")
    print(f"  Rows: {len(rows)}")
    for r in rows:
        print(f"  {dict(zip(cols, r))}")
    return cols, rows


# ─── 1. Summary with totals and % coverage ───
run(f"""
SELECT
  po_band,
  project_count,
  ROUND(100.0 * project_count / SUM(project_count) OVER (), 1) AS pct_of_total,
  avg_po_count,
  median_po_count,
  avg_total_po_amt,
  avg_area,
  median_area,
  pct_with_area,
  avg_forecast_rev,
  avg_forecast_cost,
  avg_actual_cost
FROM (
  SELECT
    {BAND_CASE} AS po_band,
    COUNT(*) AS project_count,
    ROUND(AVG(COALESCE(po.po_count, 0)), 1) AS avg_po_count,
    ROUND(PERCENTILE_APPROX(COALESCE(po.po_count, 0), 0.5), 0) AS median_po_count,
    ROUND(AVG(po.total_po_amt), 0) AS avg_total_po_amt,
    ROUND(AVG(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN CAST(p.Area AS DOUBLE) END), 0) AS avg_area,
    ROUND(PERCENTILE_APPROX(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN CAST(p.Area AS DOUBLE) END, 0.5), 0) AS median_area,
    ROUND(100.0 * SUM(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_with_area,
    ROUND(AVG(CAST(p.Project_forecast_revenue AS DOUBLE)), 0) AS avg_forecast_rev,
    ROUND(AVG(CAST(p.Project_forecast_costs AS DOUBLE)), 0) AS avg_forecast_cost,
    ROUND(AVG(CAST(p.Project_actual_costs AS DOUBLE)), 0) AS avg_actual_cost
  {BASE_JOIN}
  GROUP BY {BAND_CASE}
) t
ORDER BY po_band
""", "1. PO Band Summary (ALL projects, with % of total)")


# ─── 2. Sector (Asset_Class) by PO band ───
run(f"""
SELECT
  po_band,
  Asset_Class,
  project_count,
  pct_of_band,
  avg_po_count,
  avg_total_po_amt,
  avg_area
FROM (
  SELECT
    po_band,
    Asset_Class,
    project_count,
    pct_of_band,
    avg_po_count,
    avg_total_po_amt,
    avg_area,
    ROW_NUMBER() OVER (PARTITION BY po_band ORDER BY project_count DESC) AS rn
  FROM (
    SELECT
      {BAND_CASE} AS po_band,
      COALESCE(p.Asset_Class, '(not set)') AS Asset_Class,
      COUNT(*) AS project_count,
      ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY {BAND_CASE}), 1) AS pct_of_band,
      ROUND(AVG(COALESCE(po.po_count, 0)), 1) AS avg_po_count,
      ROUND(AVG(po.total_po_amt), 0) AS avg_total_po_amt,
      ROUND(AVG(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN CAST(p.Area AS DOUBLE) END), 0) AS avg_area
    {BASE_JOIN}
    GROUP BY {BAND_CASE}, COALESCE(p.Asset_Class, '(not set)')
  ) agg
) ranked
WHERE rn <= 8
ORDER BY po_band, project_count DESC
""", "2. Asset Class (Sector) by PO Band - Top 8 per band")


# ─── 3. Industry by PO band ───
run(f"""
SELECT
  po_band,
  Industry,
  project_count,
  pct_of_band,
  avg_total_po_amt,
  avg_area
FROM (
  SELECT
    po_band,
    Industry,
    project_count,
    pct_of_band,
    avg_total_po_amt,
    avg_area,
    ROW_NUMBER() OVER (PARTITION BY po_band ORDER BY project_count DESC) AS rn
  FROM (
    SELECT
      {BAND_CASE} AS po_band,
      COALESCE(p.Industry, '(not set)') AS Industry,
      COUNT(*) AS project_count,
      ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY {BAND_CASE}), 1) AS pct_of_band,
      ROUND(AVG(po.total_po_amt), 0) AS avg_total_po_amt,
      ROUND(AVG(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN CAST(p.Area AS DOUBLE) END), 0) AS avg_area
    {BASE_JOIN}
    GROUP BY {BAND_CASE}, COALESCE(p.Industry, '(not set)')
  ) agg
) ranked
WHERE rn <= 8
ORDER BY po_band, project_count DESC
""", "3. Industry by PO Band - Top 8 per band")


# ─── 4. Country by PO band ───
run(f"""
SELECT
  po_band,
  Country,
  project_count,
  pct_of_band,
  avg_po_count,
  avg_total_po_amt,
  avg_area
FROM (
  SELECT
    po_band,
    Country,
    project_count,
    pct_of_band,
    avg_po_count,
    avg_total_po_amt,
    avg_area,
    ROW_NUMBER() OVER (PARTITION BY po_band ORDER BY project_count DESC) AS rn
  FROM (
    SELECT
      {BAND_CASE} AS po_band,
      p.Country,
      COUNT(*) AS project_count,
      ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY {BAND_CASE}), 1) AS pct_of_band,
      ROUND(AVG(COALESCE(po.po_count, 0)), 1) AS avg_po_count,
      ROUND(AVG(po.total_po_amt), 0) AS avg_total_po_amt,
      ROUND(AVG(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN CAST(p.Area AS DOUBLE) END), 0) AS avg_area
    {BASE_JOIN}
    GROUP BY {BAND_CASE}, p.Country
  ) agg
) ranked
WHERE rn <= 8
ORDER BY po_band, project_count DESC
""", "4. Country by PO Band - Top 8 per band")


# ─── 5. City (from portfolio) by PO band ───
run(f"""
SELECT
  po_band,
  City,
  project_count,
  pct_of_band,
  avg_total_po_amt,
  avg_area
FROM (
  SELECT
    po_band,
    City,
    project_count,
    pct_of_band,
    avg_total_po_amt,
    avg_area,
    ROW_NUMBER() OVER (PARTITION BY po_band ORDER BY project_count DESC) AS rn
  FROM (
    SELECT
      {BAND_CASE} AS po_band,
      COALESCE(pf.City, '(not set)') AS City,
      COUNT(*) AS project_count,
      ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY {BAND_CASE}), 1) AS pct_of_band,
      ROUND(AVG(po.total_po_amt), 0) AS avg_total_po_amt,
      ROUND(AVG(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN CAST(p.Area AS DOUBLE) END), 0) AS avg_area
    FROM {FQ}.tetris_project p
    LEFT JOIN (
      SELECT
        TS_Project_ID,
        COUNT(*) AS po_count,
        SUM(CAST(REGEXP_REPLACE(PO_Amount, '[^0-9.-]', '') AS DOUBLE)) AS total_po_amt
      FROM {FQ}.tetris_purchaseorder
      WHERE udp_delete_flag = 'N'
      GROUP BY TS_Project_ID
    ) po ON p.Project_TS_ID = po.TS_Project_ID
    LEFT JOIN {FQ}.tetris_portfolio pf ON p.Portfolio_ID = pf.Portfolio_ID AND p.Project_TS_ID = pf.Project_ID
    WHERE p.udp_delete_flag = 'N'
    GROUP BY {BAND_CASE}, COALESCE(pf.City, '(not set)')
  ) agg
) ranked
WHERE rn <= 10
ORDER BY po_band, project_count DESC
""", "5. City (from Portfolio) by PO Band - Top 10 per band")


# ─── 6. tetris_Service by PO band ───
run(f"""
SELECT
  po_band,
  tetris_Service,
  project_count,
  pct_of_band,
  avg_po_count,
  avg_total_po_amt,
  avg_area
FROM (
  SELECT
    po_band,
    tetris_Service,
    project_count,
    pct_of_band,
    avg_po_count,
    avg_total_po_amt,
    avg_area,
    ROW_NUMBER() OVER (PARTITION BY po_band ORDER BY project_count DESC) AS rn
  FROM (
    SELECT
      {BAND_CASE} AS po_band,
      COALESCE(p.tetris_Service, '(not set)') AS tetris_Service,
      COUNT(*) AS project_count,
      ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY {BAND_CASE}), 1) AS pct_of_band,
      ROUND(AVG(COALESCE(po.po_count, 0)), 1) AS avg_po_count,
      ROUND(AVG(po.total_po_amt), 0) AS avg_total_po_amt,
      ROUND(AVG(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN CAST(p.Area AS DOUBLE) END), 0) AS avg_area
    {BASE_JOIN}
    GROUP BY {BAND_CASE}, COALESCE(p.tetris_Service, '(not set)')
  ) agg
) ranked
WHERE rn <= 6
ORDER BY po_band, project_count DESC
""", "6. Tetris Service Type by PO Band - Top 6 per band")


print("\n\n✓ PO Band v2 analysis complete!")
