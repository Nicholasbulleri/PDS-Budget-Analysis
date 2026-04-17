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
Tetris Deep Budget/Cost Analysis
Focuses on project budgets, purchase orders per project,
budget bands, cost completeness, and financial data quality.
"""
import sys
import os
import json


from edp_connection import execute_query

CATALOG = "edp_sourcesystem"
SCHEMA = "tetris"
FQ = f"{CATALOG}.{SCHEMA}"


def run(query, label=""):
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    cols, rows = execute_query(query)
    print(f"  Columns: {cols}")
    print(f"  Rows: {len(rows)}")
    for r in rows[:50]:
        print(f"  {dict(zip(cols, r))}")
    return cols, rows


# ─── 1. Project financial field population ───
run(f"""
SELECT
  COUNT(*) AS total_projects,
  SUM(CASE WHEN udp_delete_flag = 'N' THEN 1 ELSE 0 END) AS active_projects,
  SUM(CASE WHEN Project_Budget_Revenue IS NOT NULL THEN 1 ELSE 0 END) AS has_budget_revenue,
  SUM(CASE WHEN Project_Budget_Costs IS NOT NULL THEN 1 ELSE 0 END) AS has_budget_costs,
  SUM(CASE WHEN Project_forecast_revenue IS NOT NULL THEN 1 ELSE 0 END) AS has_forecast_revenue,
  SUM(CASE WHEN Project_forecast_costs IS NOT NULL THEN 1 ELSE 0 END) AS has_forecast_costs,
  SUM(CASE WHEN Project_actual_revenue IS NOT NULL THEN 1 ELSE 0 END) AS has_actual_revenue,
  SUM(CASE WHEN Project_actual_costs IS NOT NULL THEN 1 ELSE 0 END) AS has_actual_costs,
  SUM(CASE WHEN Project_gross_margin IS NOT NULL THEN 1 ELSE 0 END) AS has_gross_margin,
  SUM(CASE WHEN CAST(Project_forecast_revenue AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS forecast_rev_gt0,
  SUM(CASE WHEN CAST(Project_forecast_costs AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS forecast_cost_gt0,
  SUM(CASE WHEN CAST(Project_actual_revenue AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS actual_rev_gt0,
  SUM(CASE WHEN CAST(Project_actual_costs AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS actual_cost_gt0
FROM {FQ}.tetris_project
""", "1. Project Financial Field Population")


# ─── 2. Project financial stats by Project_Status ───
run(f"""
SELECT
  Project_Status,
  COUNT(*) AS cnt,
  SUM(CASE WHEN CAST(Project_forecast_revenue AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_fcst_rev,
  SUM(CASE WHEN CAST(Project_forecast_costs AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_fcst_cost,
  SUM(CASE WHEN CAST(Project_actual_revenue AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_act_rev,
  SUM(CASE WHEN CAST(Project_actual_costs AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_act_cost,
  ROUND(AVG(CAST(Project_forecast_revenue AS DOUBLE)), 2) AS avg_fcst_rev,
  ROUND(AVG(CAST(Project_forecast_costs AS DOUBLE)), 2) AS avg_fcst_cost
FROM {FQ}.tetris_project
GROUP BY Project_Status
ORDER BY cnt DESC
""", "2. Financial Coverage by Project Status")


# ─── 3. Project financial stats by Country ───
run(f"""
SELECT
  Country,
  COUNT(*) AS cnt,
  SUM(CASE WHEN CAST(Project_forecast_revenue AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_fcst_rev,
  SUM(CASE WHEN CAST(Project_actual_revenue AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_act_rev,
  SUM(CASE WHEN CAST(Project_actual_costs AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_act_cost,
  ROUND(SUM(CAST(Project_forecast_revenue AS DOUBLE)), 2) AS total_fcst_rev,
  ROUND(SUM(CAST(Project_actual_revenue AS DOUBLE)), 2) AS total_act_rev,
  ROUND(SUM(CAST(Project_actual_costs AS DOUBLE)), 2) AS total_act_cost
FROM {FQ}.tetris_project
GROUP BY Country
ORDER BY cnt DESC
""", "3. Financial Coverage by Country")


# ─── 4. Forecast Revenue Budget Bands (like cost code analysis) ───
run(f"""
SELECT
  budget_band,
  COUNT(*) AS project_count,
  ROUND(SUM(forecast_revenue), 2) AS total_forecast_rev,
  ROUND(AVG(forecast_revenue), 2) AS avg_forecast_rev,
  ROUND(AVG(forecast_costs), 2) AS avg_forecast_cost,
  ROUND(AVG(forecast_revenue - forecast_costs), 2) AS avg_margin
FROM (
  SELECT
    CAST(Project_forecast_revenue AS DOUBLE) AS forecast_revenue,
    CAST(Project_forecast_costs AS DOUBLE) AS forecast_costs,
    CASE
      WHEN CAST(Project_forecast_revenue AS DOUBLE) <= 0 THEN '0. Zero/Negative'
      WHEN CAST(Project_forecast_revenue AS DOUBLE) < 50000 THEN '1. Under 50K'
      WHEN CAST(Project_forecast_revenue AS DOUBLE) < 100000 THEN '2. 50K-100K'
      WHEN CAST(Project_forecast_revenue AS DOUBLE) < 500000 THEN '3. 100K-500K'
      WHEN CAST(Project_forecast_revenue AS DOUBLE) < 1000000 THEN '4. 500K-1M'
      WHEN CAST(Project_forecast_revenue AS DOUBLE) < 5000000 THEN '5. 1M-5M'
      WHEN CAST(Project_forecast_revenue AS DOUBLE) < 10000000 THEN '6. 5M-10M'
      ELSE '7. 10M+'
    END AS budget_band
  FROM {FQ}.tetris_project
  WHERE udp_delete_flag = 'N'
) sub
GROUP BY budget_band
ORDER BY budget_band
""", "4. Projects by Forecast Revenue Band")


# ─── 5. PO counts per project (analogous to cost codes per project) ───
run(f"""
SELECT
  po_count_band,
  COUNT(*) AS project_count,
  ROUND(AVG(po_count), 1) AS avg_pos,
  ROUND(AVG(total_po_amount), 2) AS avg_total_po_amt
FROM (
  SELECT
    TS_Project_ID,
    COUNT(*) AS po_count,
    SUM(CAST(REGEXP_REPLACE(PO_Amount, '[^0-9.-]', '') AS DOUBLE)) AS total_po_amount,
    CASE
      WHEN COUNT(*) = 1 THEN '01. 1 PO'
      WHEN COUNT(*) BETWEEN 2 AND 5 THEN '02. 2-5 POs'
      WHEN COUNT(*) BETWEEN 6 AND 10 THEN '03. 6-10 POs'
      WHEN COUNT(*) BETWEEN 11 AND 20 THEN '04. 11-20 POs'
      WHEN COUNT(*) BETWEEN 21 AND 50 THEN '05. 21-50 POs'
      WHEN COUNT(*) BETWEEN 51 AND 100 THEN '06. 51-100 POs'
      ELSE '07. 100+ POs'
    END AS po_count_band
  FROM {FQ}.tetris_purchaseorder
  WHERE udp_delete_flag = 'N'
  GROUP BY TS_Project_ID
) sub
GROUP BY po_count_band
ORDER BY po_count_band
""", "5. Purchase Order Count Bands per Project")


# ─── 6. PO count bands crossed with project budget band ───
run(f"""
SELECT
  budget_band,
  po_band,
  COUNT(*) AS project_count
FROM (
  SELECT
    p.Project_TS_ID,
    CASE
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) <= 0 THEN '0. Zero/Neg'
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) < 100000 THEN '1. Under 100K'
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) < 500000 THEN '2. 100K-500K'
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) < 1000000 THEN '3. 500K-1M'
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) < 5000000 THEN '4. 1M-5M'
      ELSE '5. 5M+'
    END AS budget_band,
    CASE
      WHEN po.po_count IS NULL THEN 'a. No POs'
      WHEN po.po_count BETWEEN 1 AND 5 THEN 'b. 1-5 POs'
      WHEN po.po_count BETWEEN 6 AND 20 THEN 'c. 6-20 POs'
      WHEN po.po_count BETWEEN 21 AND 50 THEN 'd. 21-50 POs'
      ELSE 'e. 50+ POs'
    END AS po_band
  FROM {FQ}.tetris_project p
  LEFT JOIN (
    SELECT TS_Project_ID, COUNT(*) AS po_count
    FROM {FQ}.tetris_purchaseorder
    WHERE udp_delete_flag = 'N'
    GROUP BY TS_Project_ID
  ) po ON p.Project_TS_ID = po.TS_Project_ID
  WHERE p.udp_delete_flag = 'N'
) sub
GROUP BY budget_band, po_band
ORDER BY budget_band, po_band
""", "6. Budget Band x PO Count Cross-Tab")


# ─── 7. Supplier Invoice counts per project ───
run(f"""
SELECT
  inv_count_band,
  COUNT(*) AS project_count,
  ROUND(AVG(inv_count), 1) AS avg_invoices,
  ROUND(AVG(total_inv_amount), 2) AS avg_total_inv_amt
FROM (
  SELECT
    TS_Project_ID,
    COUNT(*) AS inv_count,
    SUM(CAST(SIN_Split_Amount_local_currency AS DOUBLE)) AS total_inv_amount,
    CASE
      WHEN COUNT(*) = 1 THEN '01. 1 invoice'
      WHEN COUNT(*) BETWEEN 2 AND 5 THEN '02. 2-5 invoices'
      WHEN COUNT(*) BETWEEN 6 AND 10 THEN '03. 6-10 invoices'
      WHEN COUNT(*) BETWEEN 11 AND 20 THEN '04. 11-20 invoices'
      WHEN COUNT(*) BETWEEN 21 AND 50 THEN '05. 21-50 invoices'
      WHEN COUNT(*) BETWEEN 51 AND 100 THEN '06. 51-100 invoices'
      ELSE '07. 100+ invoices'
    END AS inv_count_band
  FROM {FQ}.tetris_supplierinvoice
  WHERE udp_delete_flag = 'N'
  GROUP BY TS_Project_ID
) sub
GROUP BY inv_count_band
ORDER BY inv_count_band
""", "7. Supplier Invoice Count Bands per Project")


# ─── 8. Project_stage distribution ───
run(f"""
SELECT
  Project_stage,
  COUNT(*) AS cnt,
  SUM(CASE WHEN CAST(Project_forecast_revenue AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_fcst_rev,
  SUM(CASE WHEN CAST(Project_actual_costs AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_act_cost,
  ROUND(SUM(CAST(Project_forecast_revenue AS DOUBLE)), 0) AS total_fcst_rev
FROM {FQ}.tetris_project
WHERE udp_delete_flag = 'N'
GROUP BY Project_stage
ORDER BY cnt DESC
""", "8. Project Stage Distribution with Financials")


# ─── 9. Project_type distribution ───
run(f"""
SELECT
  Project_type,
  COUNT(*) AS cnt,
  SUM(CASE WHEN CAST(Project_forecast_revenue AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_fcst_rev,
  ROUND(AVG(CAST(Project_forecast_revenue AS DOUBLE)), 2) AS avg_fcst_rev,
  ROUND(AVG(CAST(Project_forecast_costs AS DOUBLE)), 2) AS avg_fcst_cost
FROM {FQ}.tetris_project
WHERE udp_delete_flag = 'N'
GROUP BY Project_type
ORDER BY cnt DESC
""", "9. Project Type Distribution with Financials")


# ─── 10. Asset_Class distribution ───
run(f"""
SELECT
  COALESCE(Asset_Class, '(null)') AS Asset_Class,
  COUNT(*) AS cnt,
  ROUND(SUM(CAST(Project_forecast_revenue AS DOUBLE)), 0) AS total_fcst_rev,
  ROUND(AVG(CAST(Project_forecast_revenue AS DOUBLE)), 0) AS avg_fcst_rev
FROM {FQ}.tetris_project
WHERE udp_delete_flag = 'N'
GROUP BY Asset_Class
ORDER BY cnt DESC
""", "10. Asset Class Distribution")


# ─── 11. Currency distribution ───
run(f"""
SELECT
  Currency,
  COUNT(*) AS project_cnt,
  ROUND(SUM(CAST(Project_forecast_revenue AS DOUBLE)), 0) AS total_fcst_rev,
  ROUND(SUM(CAST(Project_actual_revenue AS DOUBLE)), 0) AS total_act_rev
FROM {FQ}.tetris_project
WHERE udp_delete_flag = 'N'
GROUP BY Currency
ORDER BY project_cnt DESC
""", "11. Currency Distribution")


# ─── 12. Project creation date range / yearly trend ───
run(f"""
SELECT
  YEAR(TO_TIMESTAMP(Project_Creation_date)) AS creation_year,
  COUNT(*) AS cnt,
  SUM(CASE WHEN CAST(Project_forecast_revenue AS DOUBLE) > 0 THEN 1 ELSE 0 END) AS has_fcst_rev,
  ROUND(SUM(CAST(Project_forecast_revenue AS DOUBLE)), 0) AS total_fcst_rev
FROM {FQ}.tetris_project
WHERE udp_delete_flag = 'N'
GROUP BY YEAR(TO_TIMESTAMP(Project_Creation_date))
ORDER BY creation_year
""", "12. Projects by Creation Year")


# ─── 13. Supplier categories on POs (proxy for cost code concept) ───
run(f"""
SELECT
  s.Category AS supplier_category,
  COUNT(DISTINCT po.PO_ID) AS po_count,
  COUNT(DISTINCT po.TS_Project_ID) AS project_count,
  ROUND(SUM(CAST(REGEXP_REPLACE(po.PO_Amount, '[^0-9.-]', '') AS DOUBLE)), 0) AS total_po_amount
FROM {FQ}.tetris_purchaseorder po
JOIN {FQ}.tetris_supplier s ON po.Supplier_TS_ID = s.sup_id
WHERE po.udp_delete_flag = 'N'
GROUP BY s.Category
ORDER BY po_count DESC
LIMIT 30
""", "13. Top 30 Supplier Categories (proxy for cost codes)")


# ─── 14. Supplier categories per project by budget band ───
run(f"""
SELECT
  budget_band,
  COUNT(*) AS project_count,
  ROUND(AVG(cat_count), 1) AS avg_supplier_categories,
  ROUND(AVG(supplier_count), 1) AS avg_distinct_suppliers,
  ROUND(AVG(po_count), 1) AS avg_po_count
FROM (
  SELECT
    p.Project_TS_ID,
    CASE
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) <= 0 THEN '0. Zero/Neg'
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) < 100000 THEN '1. Under 100K'
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) < 500000 THEN '2. 100K-500K'
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) < 1000000 THEN '3. 500K-1M'
      WHEN CAST(p.Project_forecast_revenue AS DOUBLE) < 5000000 THEN '4. 1M-5M'
      ELSE '5. 5M+'
    END AS budget_band,
    COUNT(DISTINCT s.Category) AS cat_count,
    COUNT(DISTINCT po.Supplier_TS_ID) AS supplier_count,
    COUNT(DISTINCT po.PO_ID) AS po_count
  FROM {FQ}.tetris_project p
  LEFT JOIN {FQ}.tetris_purchaseorder po
    ON p.Project_TS_ID = po.TS_Project_ID AND po.udp_delete_flag = 'N'
  LEFT JOIN {FQ}.tetris_supplier s
    ON po.Supplier_TS_ID = s.sup_id
  WHERE p.udp_delete_flag = 'N'
  GROUP BY p.Project_TS_ID, p.Project_forecast_revenue
) sub
GROUP BY budget_band
ORDER BY budget_band
""", "14. Supplier Category Richness by Budget Band")


# ─── 15. Projects with vs without PO/Invoice data ───
run(f"""
SELECT
  CASE WHEN po_cnt > 0 THEN 'Has POs' ELSE 'No POs' END AS has_po,
  CASE WHEN sin_cnt > 0 THEN 'Has Invoices' ELSE 'No Invoices' END AS has_sin,
  CASE WHEN cin_cnt > 0 THEN 'Has Client Invoices' ELSE 'No Client Inv' END AS has_cin,
  COUNT(*) AS project_count,
  ROUND(AVG(fcst_rev), 0) AS avg_fcst_rev
FROM (
  SELECT
    p.Project_TS_ID,
    CAST(p.Project_forecast_revenue AS DOUBLE) AS fcst_rev,
    COALESCE(po.cnt, 0) AS po_cnt,
    COALESCE(sin.cnt, 0) AS sin_cnt,
    COALESCE(cin.cnt, 0) AS cin_cnt
  FROM {FQ}.tetris_project p
  LEFT JOIN (SELECT TS_Project_ID, COUNT(*) AS cnt FROM {FQ}.tetris_purchaseorder WHERE udp_delete_flag='N' GROUP BY TS_Project_ID) po ON p.Project_TS_ID = po.TS_Project_ID
  LEFT JOIN (SELECT TS_Project_ID, COUNT(*) AS cnt FROM {FQ}.tetris_supplierinvoice WHERE udp_delete_flag='N' GROUP BY TS_Project_ID) sin ON p.Project_TS_ID = sin.TS_Project_ID
  LEFT JOIN (SELECT Project_TS_ID, COUNT(*) AS cnt FROM {FQ}.tetris_clientinvoice WHERE udp_delete_flag='N' GROUP BY Project_TS_ID) cin ON p.Project_TS_ID = cin.Project_TS_ID
  WHERE p.udp_delete_flag = 'N'
) sub
GROUP BY 1, 2, 3
ORDER BY project_count DESC
""", "15. Project Coverage: POs vs Supplier Invoices vs Client Invoices")


# ─── 16. tetris_Service distribution ───
run(f"""
SELECT
  COALESCE(tetris_Service, '(null)') AS tetris_Service,
  COUNT(*) AS cnt,
  ROUND(SUM(CAST(Project_forecast_revenue AS DOUBLE)), 0) AS total_fcst_rev,
  ROUND(AVG(CAST(Project_forecast_revenue AS DOUBLE)), 0) AS avg_fcst_rev
FROM {FQ}.tetris_project
WHERE udp_delete_flag = 'N'
GROUP BY tetris_Service
ORDER BY cnt DESC
""", "16. Tetris Service Type Distribution")


print("\n\n✓ Deep analysis complete!")
