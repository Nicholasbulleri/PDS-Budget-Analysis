#!/usr/bin/env python3
from __future__ import annotations

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
Compare work_dynamics.curated.project (sources clarizen, ingenious) to
id_resolution_project + dim_project — coverage, gaps, and name consistency.

Join keys (dim_project notebook):
  Clarizen: id_resolution.source_id = dim_project_clarizen.sys_id (via curated -> dim row)
  Ingenious: id_resolution.source_id = dim_project_ingenious.id (= curated.id when present in dim)

Requires Databricks auth (.env). Run from project root:
  cd "Cursor Project" && python3 Python/analysis/analyze_dim_project_vs_curated_clarizen_ingenious.py

Outputs under data/:
  dim_project_vs_curated_summary.csv
  dim_project_vs_curated_missing_from_ir.csv
  dim_project_vs_curated_orphan_masters.csv
  dim_project_vs_curated_ir_duplicates.csv
  dim_project_vs_curated_name_vs_unified.csv
  dim_project_vs_curated_name_vs_source_dim.csv
"""

import csv
import os
import sys


if str(PROJECT_ROOT / "Python") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "Python"))

from edp_connection import execute_query  # noqa: E402

_DATA = os.path.join(PROJECT_ROOT, "data", "dim")

# Shared CTEs: curated + dim_project_clarizen/sys_id lookup + ir_lookup_source_id
_CTE_CURATED_AND_KEYS = """
WITH curated_src AS (
  SELECT
    LOWER(TRIM(COALESCE(CAST(sourcesystem AS STRING), ''))) AS src_sys,
    CAST(id AS STRING) AS curated_id,
    workitemidentifier,
    projectname,
    phasetext,
    state
  FROM work_dynamics.curated.project
  WHERE LOWER(TRIM(COALESCE(CAST(sourcesystem AS STRING), ''))) IN ('clarizen', 'ingenious')
),
dpc AS (
  SELECT
    CAST(curated_project_id AS STRING) AS curated_project_id,
    CAST(id AS STRING) AS clarizen_dim_id,
    CAST(sys_id AS STRING) AS sys_id,
    name AS dim_clz_name
  FROM work_dynamics.ds_pds_global.dim_project_clarizen
),
dpi AS (
  SELECT
    CAST(id AS STRING) AS ingenious_dim_id,
    CAST(curated_project_id AS STRING) AS ingenious_curated_project_id,
    name AS dim_ing_name
  FROM work_dynamics.ds_pds_global.dim_project_ingenious
),
curated_enriched AS (
  SELECT
    c.*,
    dpc.sys_id AS clarizen_sys_id,
    dpc.dim_clz_name,
    dpi.ingenious_dim_id,
    dpi.dim_ing_name,
    CAST(
      CASE
        WHEN c.src_sys = 'clarizen' THEN dpc.sys_id
        WHEN c.src_sys = 'ingenious' THEN dpi.ingenious_dim_id
      END AS STRING
    ) AS ir_lookup_source_id
  FROM curated_src c
  LEFT JOIN dpc
    ON c.src_sys = 'clarizen'
   AND (
     dpc.curated_project_id = c.curated_id
     OR dpc.clarizen_dim_id = c.curated_id
   )
  LEFT JOIN dpi
    ON c.src_sys = 'ingenious'
   AND (
     dpi.ingenious_dim_id = c.curated_id
     OR dpi.ingenious_curated_project_id = c.curated_id
   )
)
"""

Q_SUMMARY = (
    _CTE_CURATED_AND_KEYS
    + """
,
ir_agg AS (
  SELECT
    LOWER(TRIM(CAST(source AS STRING))) AS src_sys,
    CAST(source_id AS STRING) AS source_id,
    MIN(CAST(master_project_id AS STRING)) AS master_project_id_any,
    COUNT(*) AS ir_row_count,
    COUNT(DISTINCT CAST(master_project_id AS STRING)) AS distinct_master_count
  FROM work_dynamics.ds_pds_global.id_resolution_project
  WHERE LOWER(TRIM(CAST(source AS STRING))) IN ('clarizen', 'ingenious')
  GROUP BY LOWER(TRIM(CAST(source AS STRING))), CAST(source_id AS STRING)
),
joined AS (
  SELECT
    c.*,
    ir.master_project_id_any,
    ir.ir_row_count,
    ir.distinct_master_count
  FROM curated_enriched c
  LEFT JOIN ir_agg ir
    ON ir.source_id = c.ir_lookup_source_id
   AND ir.src_sys = c.src_sys
),
dp AS (
  SELECT CAST(id AS STRING) AS id FROM work_dynamics.ds_pds_global.dim_project
)
SELECT
  j.src_sys,
  COUNT(*) AS curated_rows,
  COUNT(DISTINCT j.curated_id) AS distinct_curated_ids,
  SUM(CASE WHEN j.src_sys = 'clarizen' AND j.clarizen_sys_id IS NULL THEN 1 ELSE 0 END)
    AS clarizen_rows_no_dim_project_clarizen_row,
  SUM(CASE WHEN j.src_sys = 'ingenious' AND j.ingenious_dim_id IS NULL THEN 1 ELSE 0 END)
    AS ingenious_rows_no_dim_project_ingenious_row,
  COUNT(DISTINCT CASE WHEN j.master_project_id_any IS NOT NULL THEN j.curated_id END)
    AS curated_ids_with_resolution,
  ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN j.master_project_id_any IS NOT NULL THEN j.curated_id END)
    / NULLIF(COUNT(DISTINCT j.curated_id), 0),
    2
  ) AS pct_curated_in_id_resolution,
  COUNT(DISTINCT CASE WHEN j.master_project_id_any IS NOT NULL AND dp.id IS NOT NULL THEN j.curated_id END)
    AS curated_ids_with_dim_project,
  ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN j.master_project_id_any IS NOT NULL AND dp.id IS NOT NULL THEN j.curated_id END)
    / NULLIF(COUNT(DISTINCT j.curated_id), 0),
    2
  ) AS pct_curated_in_dim_project,
  SUM(CASE WHEN j.distinct_master_count > 1 THEN 1 ELSE 0 END)
    AS curated_ids_with_multiple_distinct_masters_in_ir
FROM joined j
LEFT JOIN dp ON dp.id = j.master_project_id_any
GROUP BY j.src_sys
ORDER BY j.src_sys
"""
)

Q_MISSING_IR = (
    _CTE_CURATED_AND_KEYS
    + """
,
ir_agg AS (
  SELECT
    LOWER(TRIM(CAST(source AS STRING))) AS src_sys,
    CAST(source_id AS STRING) AS source_id,
    MIN(CAST(master_project_id AS STRING)) AS master_project_id_any,
    COUNT(DISTINCT CAST(master_project_id AS STRING)) AS distinct_master_count
  FROM work_dynamics.ds_pds_global.id_resolution_project
  WHERE LOWER(TRIM(CAST(source AS STRING))) IN ('clarizen', 'ingenious')
  GROUP BY LOWER(TRIM(CAST(source AS STRING))), CAST(source_id AS STRING)
),
joined AS (
  SELECT
    c.*,
    ir.master_project_id_any
  FROM curated_enriched c
  LEFT JOIN ir_agg ir
    ON ir.source_id = c.ir_lookup_source_id
   AND ir.src_sys = c.src_sys
)
SELECT
  j.src_sys,
  j.curated_id,
  j.workitemidentifier,
  j.projectname,
  j.clarizen_sys_id,
  j.ir_lookup_source_id
FROM joined j
WHERE j.master_project_id_any IS NULL
ORDER BY j.src_sys, j.curated_id
LIMIT 50000
"""
)

Q_ORPHAN_MASTERS = """
SELECT
  ir.source,
  CAST(ir.source_id AS STRING) AS source_id,
  CAST(ir.master_project_id AS STRING) AS master_project_id
FROM work_dynamics.ds_pds_global.id_resolution_project ir
LEFT JOIN work_dynamics.ds_pds_global.dim_project dp
  ON CAST(dp.id AS STRING) = CAST(ir.master_project_id AS STRING)
WHERE LOWER(TRIM(CAST(ir.source AS STRING))) IN ('clarizen', 'ingenious')
  AND ir.master_project_id IS NOT NULL
  AND dp.id IS NULL
LIMIT 50000
"""

Q_IR_DUP_KEYS = """
SELECT
  LOWER(TRIM(CAST(source AS STRING))) AS src_sys,
  CAST(source_id AS STRING) AS source_id,
  COUNT(*) AS row_cnt,
  COUNT(DISTINCT CAST(master_project_id AS STRING)) AS distinct_masters
FROM work_dynamics.ds_pds_global.id_resolution_project
WHERE LOWER(TRIM(CAST(source AS STRING))) IN ('clarizen', 'ingenious')
GROUP BY LOWER(TRIM(CAST(source AS STRING))), CAST(source_id AS STRING)
HAVING COUNT(*) > 1 OR COUNT(DISTINCT CAST(master_project_id AS STRING)) > 1
ORDER BY row_cnt DESC
LIMIT 50000
"""

Q_NAME_UNIFIED = (
    _CTE_CURATED_AND_KEYS
    + """
,
ir_agg AS (
  SELECT
    LOWER(TRIM(CAST(source AS STRING))) AS src_sys,
    CAST(source_id AS STRING) AS source_id,
    MIN(CAST(master_project_id AS STRING)) AS master_project_id_any
  FROM work_dynamics.ds_pds_global.id_resolution_project
  WHERE LOWER(TRIM(CAST(source AS STRING))) IN ('clarizen', 'ingenious')
  GROUP BY LOWER(TRIM(CAST(source AS STRING))), CAST(source_id AS STRING)
),
joined AS (
  SELECT
    c.*,
    ir.master_project_id_any
  FROM curated_enriched c
  INNER JOIN ir_agg ir
    ON ir.source_id = c.ir_lookup_source_id
   AND ir.src_sys = c.src_sys
)
SELECT
  j.src_sys,
  COUNT(*) AS paired_rows,
  SUM(
    CASE
      WHEN LOWER(TRIM(COALESCE(j.projectname, ''))) = LOWER(TRIM(COALESCE(dp.name, '')))
      THEN 1 ELSE 0
    END
  ) AS name_exact_match,
  ROUND(
    100.0 * SUM(
      CASE
        WHEN LOWER(TRIM(COALESCE(j.projectname, ''))) = LOWER(TRIM(COALESCE(dp.name, '')))
        THEN 1 ELSE 0
      END
    ) / NULLIF(COUNT(*), 0),
    2
  ) AS pct_name_exact_match
FROM joined j
INNER JOIN work_dynamics.ds_pds_global.dim_project dp
  ON CAST(dp.id AS STRING) = j.master_project_id_any
GROUP BY j.src_sys
ORDER BY j.src_sys
"""
)

Q_NAME_SOURCE_DIM = """
WITH curated_src AS (
  SELECT
    LOWER(TRIM(COALESCE(CAST(sourcesystem AS STRING), ''))) AS src_sys,
    CAST(id AS STRING) AS curated_id,
    projectname AS curated_name
  FROM work_dynamics.curated.project
  WHERE LOWER(TRIM(COALESCE(CAST(sourcesystem AS STRING), ''))) IN ('clarizen', 'ingenious')
),
dpc AS (
  SELECT
    CAST(curated_project_id AS STRING) AS curated_project_id,
    CAST(id AS STRING) AS clarizen_dim_id,
    name AS dim_name
  FROM work_dynamics.ds_pds_global.dim_project_clarizen
),
dpi AS (
  SELECT
    CAST(id AS STRING) AS ingenious_dim_id,
    CAST(curated_project_id AS STRING) AS curated_project_id,
    name AS dim_name
  FROM work_dynamics.ds_pds_global.dim_project_ingenious
)
SELECT
  'clarizen' AS src_sys,
  COUNT(*) AS n,
  SUM(CASE WHEN LOWER(TRIM(COALESCE(c.curated_name,''))) = LOWER(TRIM(COALESCE(dpc.dim_name,''))) THEN 1 ELSE 0 END) AS exact_match,
  ROUND(100.0 * SUM(CASE WHEN LOWER(TRIM(COALESCE(c.curated_name,''))) = LOWER(TRIM(COALESCE(dpc.dim_name,''))) THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 2) AS pct_exact_match
FROM curated_src c
INNER JOIN dpc
  ON c.src_sys = 'clarizen'
 AND (dpc.curated_project_id = c.curated_id OR dpc.clarizen_dim_id = c.curated_id)
WHERE c.src_sys = 'clarizen'
UNION ALL
SELECT
  'ingenious' AS src_sys,
  COUNT(*) AS n,
  SUM(CASE WHEN LOWER(TRIM(COALESCE(c.curated_name,''))) = LOWER(TRIM(COALESCE(dpi.dim_name,''))) THEN 1 ELSE 0 END) AS exact_match,
  ROUND(100.0 * SUM(CASE WHEN LOWER(TRIM(COALESCE(c.curated_name,''))) = LOWER(TRIM(COALESCE(dpi.dim_name,''))) THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 2) AS pct_exact_match
FROM curated_src c
INNER JOIN dpi
  ON c.src_sys = 'ingenious'
 AND (dpi.ingenious_dim_id = c.curated_id OR dpi.curated_project_id = c.curated_id)
WHERE c.src_sys = 'ingenious'
"""


def _write_csv(path: str, columns: list, rows: list) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(rows)


def main() -> None:
    os.makedirs(_DATA, exist_ok=True)
    print("=== 1. Summary (curated vs id_resolution vs dim_project) ===")
    cols, rows = execute_query(Q_SUMMARY.strip())
    for r in rows:
        print(r)
    _write_csv(os.path.join(_DATA, "dim_project_vs_curated_summary.csv"), cols, rows)
    print(f"Wrote {os.path.join(_DATA, 'dim_project_vs_curated_summary.csv')}")

    print("\n=== 2. Missing from id_resolution (lookup via sys_id / ingenious id) ===")
    cols, rows = execute_query(Q_MISSING_IR.strip())
    print(f"Rows: {len(rows)}")
    _write_csv(os.path.join(_DATA, "dim_project_vs_curated_missing_from_ir.csv"), cols, rows)

    print("\n=== 3. Orphan masters (in id_resolution, not in dim_project) ===")
    cols, rows = execute_query(Q_ORPHAN_MASTERS.strip())
    print(f"Rows: {len(rows)}")
    _write_csv(os.path.join(_DATA, "dim_project_vs_curated_orphan_masters.csv"), cols, rows)

    print("\n=== 4. id_resolution duplicate keys ===")
    cols, rows = execute_query(Q_IR_DUP_KEYS.strip())
    print(f"Rows: {len(rows)}")
    _write_csv(os.path.join(_DATA, "dim_project_vs_curated_ir_duplicates.csv"), cols, rows)

    print("\n=== 5. Name: curated vs dim_project (unified) ===")
    cols, rows = execute_query(Q_NAME_UNIFIED.strip())
    for r in rows:
        print(r)
    _write_csv(os.path.join(_DATA, "dim_project_vs_curated_name_vs_unified.csv"), cols, rows)

    print("\n=== 6. Name: curated vs source-specific dim ===")
    cols, rows = execute_query(Q_NAME_SOURCE_DIM.strip())
    for r in rows:
        print(r)
    _write_csv(os.path.join(_DATA, "dim_project_vs_curated_name_vs_source_dim.csv"), cols, rows)

    print("\nDone.")


if __name__ == "__main__":
    main()
