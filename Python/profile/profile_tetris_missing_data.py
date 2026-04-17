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
Tetris Missing Data Analysis
Investigates whether project status, stage, country, or other indicators
explain why Asset_Class (sector), POs, and tetris_Service are missing.
"""
import sys, os

from edp_connection import execute_query

FQ = "edp_sourcesystem.tetris"


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


# ═══════════════════════════════════════════════════════════════════
# A. MISSING ASSET CLASS (SECTOR)
# ═══════════════════════════════════════════════════════════════════

run(f"""
WITH base AS (
  SELECT *,
    CASE WHEN Asset_Class IS NULL THEN 'Missing Sector' ELSE 'Has Sector' END AS sector_flag
  FROM {FQ}.tetris_project WHERE udp_delete_flag = 'N'
)
SELECT sector_flag, Project_Status, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY sector_flag), 1) AS pct
FROM base GROUP BY sector_flag, Project_Status ORDER BY sector_flag, cnt DESC
""", "A1. Missing Sector by Project Status")


run(f"""
WITH base AS (
  SELECT *,
    CASE WHEN Asset_Class IS NULL THEN 'Missing Sector' ELSE 'Has Sector' END AS sector_flag
  FROM {FQ}.tetris_project WHERE udp_delete_flag = 'N'
)
SELECT sector_flag, Project_stage, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY sector_flag), 1) AS pct
FROM base GROUP BY sector_flag, Project_stage ORDER BY sector_flag, cnt DESC
""", "A2. Missing Sector by Project Stage")


run(f"""
WITH base AS (
  SELECT *,
    CASE WHEN Asset_Class IS NULL THEN 'Missing Sector' ELSE 'Has Sector' END AS sector_flag
  FROM {FQ}.tetris_project WHERE udp_delete_flag = 'N'
)
SELECT sector_flag, Country, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY sector_flag), 1) AS pct
FROM base GROUP BY sector_flag, Country ORDER BY sector_flag, cnt DESC
""", "A3. Missing Sector by Country")


run(f"""
WITH base AS (
  SELECT *,
    CASE WHEN Asset_Class IS NULL THEN 'Missing Sector' ELSE 'Has Sector' END AS sector_flag
  FROM {FQ}.tetris_project WHERE udp_delete_flag = 'N'
)
SELECT sector_flag, YEAR(TO_TIMESTAMP(Project_Creation_date)) AS yr, COUNT(*) AS cnt
FROM base GROUP BY sector_flag, YEAR(TO_TIMESTAMP(Project_Creation_date))
ORDER BY sector_flag, yr
""", "A4. Missing Sector by Creation Year")


run(f"""
WITH base AS (
  SELECT *,
    CASE WHEN Asset_Class IS NULL THEN 'Missing Sector' ELSE 'Has Sector' END AS sector_flag
  FROM {FQ}.tetris_project WHERE udp_delete_flag = 'N'
)
SELECT sector_flag, Likelihood, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY sector_flag), 1) AS pct
FROM base GROUP BY sector_flag, Likelihood ORDER BY sector_flag, cnt DESC
""", "A5. Missing Sector by Likelihood")


# ═══════════════════════════════════════════════════════════════════
# B. MISSING POs
# ═══════════════════════════════════════════════════════════════════

run(f"""
WITH base AS (
  SELECT p.*,
    CASE WHEN po.TS_Project_ID IS NOT NULL THEN 'Has POs' ELSE 'No POs' END AS po_flag
  FROM {FQ}.tetris_project p
  LEFT JOIN (SELECT DISTINCT TS_Project_ID FROM {FQ}.tetris_purchaseorder WHERE udp_delete_flag = 'N') po
    ON p.Project_TS_ID = po.TS_Project_ID
  WHERE p.udp_delete_flag = 'N'
)
SELECT po_flag, Project_Status, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY po_flag), 1) AS pct
FROM base GROUP BY po_flag, Project_Status ORDER BY po_flag, cnt DESC
""", "B1. Missing POs by Project Status")


run(f"""
WITH base AS (
  SELECT p.*,
    CASE WHEN po.TS_Project_ID IS NOT NULL THEN 'Has POs' ELSE 'No POs' END AS po_flag
  FROM {FQ}.tetris_project p
  LEFT JOIN (SELECT DISTINCT TS_Project_ID FROM {FQ}.tetris_purchaseorder WHERE udp_delete_flag = 'N') po
    ON p.Project_TS_ID = po.TS_Project_ID
  WHERE p.udp_delete_flag = 'N'
)
SELECT po_flag, Project_stage, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY po_flag), 1) AS pct
FROM base GROUP BY po_flag, Project_stage ORDER BY po_flag, cnt DESC
""", "B2. Missing POs by Project Stage")


run(f"""
WITH base AS (
  SELECT p.*,
    CASE WHEN po.TS_Project_ID IS NOT NULL THEN 'Has POs' ELSE 'No POs' END AS po_flag
  FROM {FQ}.tetris_project p
  LEFT JOIN (SELECT DISTINCT TS_Project_ID FROM {FQ}.tetris_purchaseorder WHERE udp_delete_flag = 'N') po
    ON p.Project_TS_ID = po.TS_Project_ID
  WHERE p.udp_delete_flag = 'N'
)
SELECT po_flag, Country, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY po_flag), 1) AS pct
FROM base GROUP BY po_flag, Country ORDER BY po_flag, cnt DESC
""", "B3. Missing POs by Country")


run(f"""
WITH base AS (
  SELECT p.*,
    CASE WHEN po.TS_Project_ID IS NOT NULL THEN 'Has POs' ELSE 'No POs' END AS po_flag
  FROM {FQ}.tetris_project p
  LEFT JOIN (SELECT DISTINCT TS_Project_ID FROM {FQ}.tetris_purchaseorder WHERE udp_delete_flag = 'N') po
    ON p.Project_TS_ID = po.TS_Project_ID
  WHERE p.udp_delete_flag = 'N'
)
SELECT po_flag, Likelihood, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY po_flag), 1) AS pct
FROM base GROUP BY po_flag, Likelihood ORDER BY po_flag, cnt DESC
""", "B4. Missing POs by Likelihood")


run(f"""
WITH base AS (
  SELECT p.*,
    CASE WHEN po.TS_Project_ID IS NOT NULL THEN 'Has POs' ELSE 'No POs' END AS po_flag
  FROM {FQ}.tetris_project p
  LEFT JOIN (SELECT DISTINCT TS_Project_ID FROM {FQ}.tetris_purchaseorder WHERE udp_delete_flag = 'N') po
    ON p.Project_TS_ID = po.TS_Project_ID
  WHERE p.udp_delete_flag = 'N'
)
SELECT po_flag, COALESCE(tetris_Service, '(not set)') AS svc, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY po_flag), 1) AS pct
FROM base GROUP BY po_flag, COALESCE(tetris_Service, '(not set)') ORDER BY po_flag, cnt DESC
""", "B5. Missing POs by Service Type")


run(f"""
WITH base AS (
  SELECT p.*,
    CASE WHEN po.TS_Project_ID IS NOT NULL THEN 'Has POs' ELSE 'No POs' END AS po_flag
  FROM {FQ}.tetris_project p
  LEFT JOIN (SELECT DISTINCT TS_Project_ID FROM {FQ}.tetris_purchaseorder WHERE udp_delete_flag = 'N') po
    ON p.Project_TS_ID = po.TS_Project_ID
  WHERE p.udp_delete_flag = 'N'
)
SELECT po_flag, Project_type, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY po_flag), 1) AS pct
FROM base GROUP BY po_flag, Project_type ORDER BY po_flag, cnt DESC
""", "B6. Missing POs by Project Type")


# ═══════════════════════════════════════════════════════════════════
# C. MISSING SERVICE TYPE
# ═══════════════════════════════════════════════════════════════════

run(f"""
WITH base AS (
  SELECT *,
    CASE WHEN tetris_Service IS NULL THEN 'Missing Service' ELSE 'Has Service' END AS svc_flag
  FROM {FQ}.tetris_project WHERE udp_delete_flag = 'N'
)
SELECT svc_flag, Project_Status, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY svc_flag), 1) AS pct
FROM base GROUP BY svc_flag, Project_Status ORDER BY svc_flag, cnt DESC
""", "C1. Missing Service by Project Status")


run(f"""
WITH base AS (
  SELECT *,
    CASE WHEN tetris_Service IS NULL THEN 'Missing Service' ELSE 'Has Service' END AS svc_flag
  FROM {FQ}.tetris_project WHERE udp_delete_flag = 'N'
)
SELECT svc_flag, Project_stage, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY svc_flag), 1) AS pct
FROM base GROUP BY svc_flag, Project_stage ORDER BY svc_flag, cnt DESC
""", "C2. Missing Service by Project Stage")


run(f"""
WITH base AS (
  SELECT *,
    CASE WHEN tetris_Service IS NULL THEN 'Missing Service' ELSE 'Has Service' END AS svc_flag
  FROM {FQ}.tetris_project WHERE udp_delete_flag = 'N'
)
SELECT svc_flag, Country, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY svc_flag), 1) AS pct
FROM base GROUP BY svc_flag, Country ORDER BY svc_flag, cnt DESC
""", "C3. Missing Service by Country")


run(f"""
WITH base AS (
  SELECT *,
    CASE WHEN tetris_Service IS NULL THEN 'Missing Service' ELSE 'Has Service' END AS svc_flag
  FROM {FQ}.tetris_project WHERE udp_delete_flag = 'N'
)
SELECT svc_flag, YEAR(TO_TIMESTAMP(Project_Creation_date)) AS yr, COUNT(*) AS cnt
FROM base GROUP BY svc_flag, YEAR(TO_TIMESTAMP(Project_Creation_date))
ORDER BY svc_flag, yr
""", "C4. Missing Service by Creation Year")


# ═══════════════════════════════════════════════════════════════════
# D. CROSS-ANALYSIS
# ═══════════════════════════════════════════════════════════════════

run(f"""
WITH base AS (
  SELECT p.*,
    CASE WHEN p.Asset_Class IS NULL THEN 'No Sector' ELSE 'Has Sector' END AS sec,
    CASE WHEN po.TS_Project_ID IS NOT NULL THEN 'Has POs' ELSE 'No POs' END AS pos,
    CASE WHEN p.tetris_Service IS NULL THEN 'No Service' ELSE 'Has Service' END AS svc
  FROM {FQ}.tetris_project p
  LEFT JOIN (SELECT DISTINCT TS_Project_ID FROM {FQ}.tetris_purchaseorder WHERE udp_delete_flag = 'N') po
    ON p.Project_TS_ID = po.TS_Project_ID
  WHERE p.udp_delete_flag = 'N'
)
SELECT sec, pos, svc, COUNT(*) AS cnt,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_total,
  ROUND(AVG(CAST(Project_forecast_revenue AS DOUBLE)), 0) AS avg_fcst_rev
FROM base GROUP BY sec, pos, svc ORDER BY cnt DESC
""", "D1. Cross-Tab: Sector x POs x Service overlap")


print("\n\n✓ Missing data analysis complete!")
