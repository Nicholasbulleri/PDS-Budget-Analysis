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
Tetris PO Band Analysis
Groups projects by total PO amount bands, then analyzes:
- Project count and avg POs per band
- Avg area per band
- Top 5 supplier categories per band
"""
import sys
import os


from edp_connection import execute_query

FQ = "edp_sourcesystem.tetris"


def run(query, label):
    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"{'='*80}")
    cols, rows = execute_query(query)
    print(f"  Columns: {cols}")
    print(f"  Rows: {len(rows)}")
    for r in rows:
        print(f"  {dict(zip(cols, r))}")
    return cols, rows


# ─── 1. Project-level PO summary with bands ───
run(f"""
SELECT
  po_band,
  project_count,
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
    po_band,
    COUNT(*) AS project_count,
    ROUND(AVG(po_count), 1) AS avg_po_count,
    ROUND(PERCENTILE_APPROX(po_count, 0.5), 1) AS median_po_count,
    ROUND(AVG(total_po_amt), 0) AS avg_total_po_amt,
    ROUND(AVG(CASE WHEN area > 0 THEN area END), 0) AS avg_area,
    ROUND(PERCENTILE_APPROX(CASE WHEN area > 0 THEN area END, 0.5), 0) AS median_area,
    ROUND(100.0 * SUM(CASE WHEN area > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_with_area,
    ROUND(AVG(forecast_rev), 0) AS avg_forecast_rev,
    ROUND(AVG(forecast_cost), 0) AS avg_forecast_cost,
    ROUND(AVG(actual_cost), 0) AS avg_actual_cost
  FROM (
    SELECT
      p.Project_TS_ID,
      po.po_count,
      po.total_po_amt,
      CAST(p.Area AS DOUBLE) AS area,
      CAST(p.Project_forecast_revenue AS DOUBLE) AS forecast_rev,
      CAST(p.Project_forecast_costs AS DOUBLE) AS forecast_cost,
      CAST(p.Project_actual_costs AS DOUBLE) AS actual_cost,
      CASE
        WHEN po.total_po_amt < 50000 THEN '1. <50K'
        WHEN po.total_po_amt < 250000 THEN '2. 50K-250K'
        WHEN po.total_po_amt < 1000000 THEN '3. 250K-1M'
        WHEN po.total_po_amt < 5000000 THEN '4. 1M-5M'
        WHEN po.total_po_amt < 10000000 THEN '5. 5M-10M'
        ELSE '6. 10M+'
      END AS po_band
    FROM {FQ}.tetris_project p
    INNER JOIN (
      SELECT
        TS_Project_ID,
        COUNT(*) AS po_count,
        SUM(CAST(REGEXP_REPLACE(PO_Amount, '[^0-9.-]', '') AS DOUBLE)) AS total_po_amt
      FROM {FQ}.tetris_purchaseorder
      WHERE udp_delete_flag = 'N'
      GROUP BY TS_Project_ID
    ) po ON p.Project_TS_ID = po.TS_Project_ID
    WHERE p.udp_delete_flag = 'N'
  ) sub
  GROUP BY po_band
) t
ORDER BY po_band
""", "1. Project Bands by Total PO Amount")


# ─── 2. Top 5 supplier categories per PO band ───
run(f"""
SELECT
  po_band,
  supplier_category,
  cat_rank,
  po_count,
  project_count,
  total_po_amt,
  avg_po_amt
FROM (
  SELECT
    po_band,
    supplier_category,
    po_count,
    project_count,
    total_po_amt,
    avg_po_amt,
    ROW_NUMBER() OVER (PARTITION BY po_band ORDER BY po_count DESC) AS cat_rank
  FROM (
    SELECT
      CASE
        WHEN proj_po.total_po_amt < 50000 THEN '1. <50K'
        WHEN proj_po.total_po_amt < 250000 THEN '2. 50K-250K'
        WHEN proj_po.total_po_amt < 1000000 THEN '3. 250K-1M'
        WHEN proj_po.total_po_amt < 5000000 THEN '4. 1M-5M'
        WHEN proj_po.total_po_amt < 10000000 THEN '5. 5M-10M'
        ELSE '6. 10M+'
      END AS po_band,
      COALESCE(s.Category, '(unknown)') AS supplier_category,
      COUNT(*) AS po_count,
      COUNT(DISTINCT po.TS_Project_ID) AS project_count,
      ROUND(SUM(CAST(REGEXP_REPLACE(po.PO_Amount, '[^0-9.-]', '') AS DOUBLE)), 0) AS total_po_amt,
      ROUND(AVG(CAST(REGEXP_REPLACE(po.PO_Amount, '[^0-9.-]', '') AS DOUBLE)), 0) AS avg_po_amt
    FROM {FQ}.tetris_purchaseorder po
    INNER JOIN (
      SELECT
        TS_Project_ID,
        SUM(CAST(REGEXP_REPLACE(PO_Amount, '[^0-9.-]', '') AS DOUBLE)) AS total_po_amt
      FROM {FQ}.tetris_purchaseorder
      WHERE udp_delete_flag = 'N'
      GROUP BY TS_Project_ID
    ) proj_po ON po.TS_Project_ID = proj_po.TS_Project_ID
    LEFT JOIN {FQ}.tetris_supplier s ON po.Supplier_TS_ID = s.sup_id
    WHERE po.udp_delete_flag = 'N'
    GROUP BY
      CASE
        WHEN proj_po.total_po_amt < 50000 THEN '1. <50K'
        WHEN proj_po.total_po_amt < 250000 THEN '2. 50K-250K'
        WHEN proj_po.total_po_amt < 1000000 THEN '3. 250K-1M'
        WHEN proj_po.total_po_amt < 5000000 THEN '4. 1M-5M'
        WHEN proj_po.total_po_amt < 10000000 THEN '5. 5M-10M'
        ELSE '6. 10M+'
      END,
      COALESCE(s.Category, '(unknown)')
  ) agg
) ranked
WHERE cat_rank <= 5
ORDER BY po_band, cat_rank
""", "2. Top 5 Supplier Categories per PO Band")


# ─── 3. Bonus: PO status distribution per band ───
run(f"""
SELECT
  po_band,
  PO_Status,
  cnt
FROM (
  SELECT
    po_band,
    po.PO_Status,
    COUNT(*) AS cnt,
    ROW_NUMBER() OVER (PARTITION BY po_band ORDER BY COUNT(*) DESC) AS rn
  FROM {FQ}.tetris_purchaseorder po
  INNER JOIN (
    SELECT
      TS_Project_ID,
      SUM(CAST(REGEXP_REPLACE(PO_Amount, '[^0-9.-]', '') AS DOUBLE)) AS total_po_amt
    FROM {FQ}.tetris_purchaseorder
    WHERE udp_delete_flag = 'N'
    GROUP BY TS_Project_ID
  ) proj_po ON po.TS_Project_ID = proj_po.TS_Project_ID
  CROSS JOIN LATERAL (
    SELECT CASE
      WHEN proj_po.total_po_amt < 50000 THEN '1. <50K'
      WHEN proj_po.total_po_amt < 250000 THEN '2. 50K-250K'
      WHEN proj_po.total_po_amt < 1000000 THEN '3. 250K-1M'
      WHEN proj_po.total_po_amt < 5000000 THEN '4. 1M-5M'
      WHEN proj_po.total_po_amt < 10000000 THEN '5. 5M-10M'
      ELSE '6. 10M+'
    END AS po_band
  ) bands
  WHERE po.udp_delete_flag = 'N'
  GROUP BY po_band, po.PO_Status
) t
WHERE rn <= 5
ORDER BY po_band, cnt DESC
""", "3. Top PO Statuses per Band")


# ─── 4. Country breakdown per PO band ───
run(f"""
SELECT
  po_band,
  Country,
  project_count,
  avg_po_count,
  avg_total_po_amt
FROM (
  SELECT
    po_band,
    Country,
    project_count,
    avg_po_count,
    avg_total_po_amt,
    ROW_NUMBER() OVER (PARTITION BY po_band ORDER BY project_count DESC) AS rn
  FROM (
    SELECT
      CASE
        WHEN po.total_po_amt < 50000 THEN '1. <50K'
        WHEN po.total_po_amt < 250000 THEN '2. 50K-250K'
        WHEN po.total_po_amt < 1000000 THEN '3. 250K-1M'
        WHEN po.total_po_amt < 5000000 THEN '4. 1M-5M'
        WHEN po.total_po_amt < 10000000 THEN '5. 5M-10M'
        ELSE '6. 10M+'
      END AS po_band,
      p.Country,
      COUNT(*) AS project_count,
      ROUND(AVG(po.po_count), 1) AS avg_po_count,
      ROUND(AVG(po.total_po_amt), 0) AS avg_total_po_amt
    FROM {FQ}.tetris_project p
    INNER JOIN (
      SELECT
        TS_Project_ID,
        COUNT(*) AS po_count,
        SUM(CAST(REGEXP_REPLACE(PO_Amount, '[^0-9.-]', '') AS DOUBLE)) AS total_po_amt
      FROM {FQ}.tetris_purchaseorder
      WHERE udp_delete_flag = 'N'
      GROUP BY TS_Project_ID
    ) po ON p.Project_TS_ID = po.TS_Project_ID
    WHERE p.udp_delete_flag = 'N'
    GROUP BY
      CASE
        WHEN po.total_po_amt < 50000 THEN '1. <50K'
        WHEN po.total_po_amt < 250000 THEN '2. 50K-250K'
        WHEN po.total_po_amt < 1000000 THEN '3. 250K-1M'
        WHEN po.total_po_amt < 5000000 THEN '4. 1M-5M'
        WHEN po.total_po_amt < 10000000 THEN '5. 5M-10M'
        ELSE '6. 10M+'
      END,
      p.Country
  ) agg
) ranked
WHERE rn <= 5
ORDER BY po_band, project_count DESC
""", "4. Top 5 Countries per PO Band")


print("\n\n✓ PO Band analysis complete!")
