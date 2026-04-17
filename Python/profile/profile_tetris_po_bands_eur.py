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
Tetris PO Band Analysis - EUR Normalized, Closed Projects Only
"""
import sys, os

from edp_connection import execute_query

FQ = "edp_sourcesystem.tetris"

# Approximate multi-year average FX rates to EUR
# PO_currency uses ISO codes; project Currency uses full names for some
FX_CTE = """
fx_po AS (
  SELECT 'EUR' AS curr, 1.0 AS rate UNION ALL
  SELECT 'PLN', 0.22 UNION ALL
  SELECT 'ZAR', 0.055 UNION ALL
  SELECT 'GBP', 1.16 UNION ALL
  SELECT 'MAD', 0.092 UNION ALL
  SELECT 'CZK', 0.041 UNION ALL
  SELECT 'CHF', 0.94 UNION ALL
  SELECT 'HUF', 0.0027 UNION ALL
  SELECT 'USD', 0.91
),
fx_proj AS (
  SELECT 'EURO' AS curr, 1.0 AS rate UNION ALL
  SELECT 'PLN', 0.22 UNION ALL
  SELECT 'ZAR', 0.055 UNION ALL
  SELECT 'GBP', 1.16 UNION ALL
  SELECT 'MAD', 0.092 UNION ALL
  SELECT 'CZK', 0.041 UNION ALL
  SELECT 'CHF', 0.94 UNION ALL
  SELECT 'FORINT', 0.0027 UNION ALL
  SELECT 'USD', 0.91
)
"""

BAND_CASE = """
  CASE
    WHEN po_eur.total_po_eur IS NULL THEN '0. No POs'
    WHEN po_eur.total_po_eur < 50000 THEN '1. <50K'
    WHEN po_eur.total_po_eur < 250000 THEN '2. 50K-250K'
    WHEN po_eur.total_po_eur < 1000000 THEN '3. 250K-1M'
    WHEN po_eur.total_po_eur < 5000000 THEN '4. 1M-5M'
    WHEN po_eur.total_po_eur < 10000000 THEN '5. 5M-10M'
    ELSE '6. 10M+'
  END
"""


def run(query, label):
    print(f"\n{'='*100}")
    print(f"  {label}")
    print(f"{'='*100}")
    cols, rows = execute_query(query)
    print(f"  Columns: {cols}")
    print(f"  Rows: {len(rows)}")
    for r in rows:
        print(f"  {dict(zip(cols, r))}")
    return cols, rows


# ─── 1. PO Band Summary (EUR normalized) ───
run(f"""
WITH {FX_CTE},
po_eur AS (
  SELECT
    po.TS_Project_ID,
    COUNT(*) AS po_count,
    SUM(CAST(REGEXP_REPLACE(po.PO_Amount, '[^0-9.-]', '') AS DOUBLE)
        * COALESCE(fx.rate, 1.0)) AS total_po_eur
  FROM {FQ}.tetris_purchaseorder po
  LEFT JOIN fx_po fx ON po.PO_currency = fx.curr
  WHERE po.udp_delete_flag = 'N'
  GROUP BY po.TS_Project_ID
)
SELECT
  po_band,
  project_count,
  ROUND(100.0 * project_count / SUM(project_count) OVER (), 1) AS pct_of_total,
  avg_po_count,
  median_po_count,
  avg_total_po_eur,
  avg_area,
  median_area,
  pct_with_area,
  avg_forecast_rev_eur,
  avg_forecast_cost_eur,
  avg_gross_margin_eur,
  avg_margin_pct
FROM (
  SELECT
    {BAND_CASE} AS po_band,
    COUNT(*) AS project_count,
    ROUND(AVG(COALESCE(po_eur.po_count, 0)), 1) AS avg_po_count,
    ROUND(PERCENTILE_APPROX(COALESCE(po_eur.po_count, 0), 0.5), 0) AS median_po_count,
    ROUND(AVG(po_eur.total_po_eur), 0) AS avg_total_po_eur,
    ROUND(AVG(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN CAST(p.Area AS DOUBLE) END), 0) AS avg_area,
    ROUND(PERCENTILE_APPROX(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN CAST(p.Area AS DOUBLE) END, 0.5), 0) AS median_area,
    ROUND(100.0 * SUM(CASE WHEN CAST(p.Area AS DOUBLE) > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_with_area,
    ROUND(AVG(CAST(p.Project_forecast_revenue AS DOUBLE) * COALESCE(fxp.rate, 1.0)), 0) AS avg_forecast_rev_eur,
    ROUND(AVG(CAST(p.Project_forecast_costs AS DOUBLE) * COALESCE(fxp.rate, 1.0)), 0) AS avg_forecast_cost_eur,
    ROUND(AVG(CAST(p.Project_gross_margin AS DOUBLE) * COALESCE(fxp.rate, 1.0)), 0) AS avg_gross_margin_eur,
    ROUND(AVG(
      CASE WHEN CAST(p.Project_forecast_revenue AS DOUBLE) > 0
        THEN 100.0 * CAST(p.Project_gross_margin AS DOUBLE) / CAST(p.Project_forecast_revenue AS DOUBLE)
      END
    ), 1) AS avg_margin_pct
  FROM {FQ}.tetris_project p
  LEFT JOIN po_eur ON p.Project_TS_ID = po_eur.TS_Project_ID
  LEFT JOIN fx_proj fxp ON p.Currency = fxp.curr
  WHERE p.udp_delete_flag = 'N' AND p.Project_Status = 'Closed'
  GROUP BY {BAND_CASE}
) t
ORDER BY po_band
""", "1. PO Band Summary - EUR Normalized (Closed Projects)")


# ─── 2. Cost per sqm by PO Band ───
run(f"""
WITH {FX_CTE},
po_eur AS (
  SELECT
    po.TS_Project_ID,
    COUNT(*) AS po_count,
    SUM(CAST(REGEXP_REPLACE(po.PO_Amount, '[^0-9.-]', '') AS DOUBLE)
        * COALESCE(fx.rate, 1.0)) AS total_po_eur
  FROM {FQ}.tetris_purchaseorder po
  LEFT JOIN fx_po fx ON po.PO_currency = fx.curr
  WHERE po.udp_delete_flag = 'N'
  GROUP BY po.TS_Project_ID
),
base AS (
  SELECT
    {BAND_CASE} AS po_band,
    po_eur.total_po_eur / CAST(p.Area AS DOUBLE) AS cost_per_sqm,
    CAST(p.Project_forecast_revenue AS DOUBLE) * COALESCE(fxp.rate, 1.0) / CAST(p.Area AS DOUBLE) AS rev_per_sqm
  FROM {FQ}.tetris_project p
  INNER JOIN po_eur ON p.Project_TS_ID = po_eur.TS_Project_ID
  LEFT JOIN fx_proj fxp ON p.Currency = fxp.curr
  WHERE p.udp_delete_flag = 'N' AND p.Project_Status = 'Closed'
    AND CAST(p.Area AS DOUBLE) > 0 AND po_eur.total_po_eur > 0
)
SELECT
  po_band,
  COUNT(*) AS projects_with_area,
  ROUND(AVG(cost_per_sqm), 0) AS avg_cost_per_sqm_eur,
  ROUND(PERCENTILE_APPROX(cost_per_sqm, 0.5), 0) AS median_cost_per_sqm_eur,
  ROUND(PERCENTILE_APPROX(cost_per_sqm, 0.25), 0) AS p25_cost_per_sqm,
  ROUND(PERCENTILE_APPROX(cost_per_sqm, 0.75), 0) AS p75_cost_per_sqm,
  ROUND(AVG(rev_per_sqm), 0) AS avg_rev_per_sqm_eur,
  ROUND(PERCENTILE_APPROX(rev_per_sqm, 0.5), 0) AS median_rev_per_sqm_eur
FROM base
GROUP BY po_band
ORDER BY po_band
""", "2. Cost & Revenue per sqm by PO Band (EUR)")


# ─── 3. Gross Margin % distribution by PO Band ───
run(f"""
WITH {FX_CTE},
po_eur AS (
  SELECT po.TS_Project_ID,
    SUM(CAST(REGEXP_REPLACE(po.PO_Amount, '[^0-9.-]', '') AS DOUBLE) * COALESCE(fx.rate, 1.0)) AS total_po_eur
  FROM {FQ}.tetris_purchaseorder po
  LEFT JOIN fx_po fx ON po.PO_currency = fx.curr
  WHERE po.udp_delete_flag = 'N'
  GROUP BY po.TS_Project_ID
),
base AS (
  SELECT
    {BAND_CASE} AS po_band,
    100.0 * CAST(p.Project_gross_margin AS DOUBLE) / NULLIF(CAST(p.Project_forecast_revenue AS DOUBLE), 0) AS margin_pct
  FROM {FQ}.tetris_project p
  LEFT JOIN po_eur ON p.Project_TS_ID = po_eur.TS_Project_ID
  WHERE p.udp_delete_flag = 'N' AND p.Project_Status = 'Closed'
    AND CAST(p.Project_forecast_revenue AS DOUBLE) > 0
    AND ABS(100.0 * CAST(p.Project_gross_margin AS DOUBLE) / CAST(p.Project_forecast_revenue AS DOUBLE)) < 200
)
SELECT
  po_band,
  COUNT(*) AS project_count,
  ROUND(AVG(margin_pct), 1) AS avg_margin_pct,
  ROUND(PERCENTILE_APPROX(margin_pct, 0.5), 1) AS median_margin_pct,
  ROUND(PERCENTILE_APPROX(margin_pct, 0.25), 1) AS p25_margin_pct,
  ROUND(PERCENTILE_APPROX(margin_pct, 0.75), 1) AS p75_margin_pct,
  ROUND(100.0 * SUM(CASE WHEN margin_pct < 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_negative_margin
FROM base
GROUP BY po_band
ORDER BY po_band
""", "3. Gross Margin % Distribution by PO Band (capped at +/-200%)")


print("\n\n✓ EUR-normalized PO Band analysis complete!")
