#!/usr/bin/env python3
"""
Analyze project type fields: jllprojecttypetext vs projecttypename.

Compares coverage, distinct values, and distribution for closed USD projects
with budget in generictask (same population as the budget dashboard).
Outputs a recommendation on which field is more reliable.
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
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "analysis")
OUT_CSV = os.path.join(DATA_DIR, "project_type_analysis.csv")

# Population: same as budget query (closed USD, budget in gt, positive area)
BASE_CTE = """
WITH budget_projects AS (
    SELECT DISTINCT p.id AS project_id, p.sourcesystem
    FROM work_dynamics.curated.generictask gt
    INNER JOIN work_dynamics.curated.project p
        ON gt.projectidentifier = p.workitemidentifier
    WHERE p.currencytype = 'USD'
      AND p.phasetext = 'Closed'
      AND gt.internaltasktypetext IN ('budget', 'Cost Code Item')
      AND gt.originalbudgetamount IS NOT NULL
      AND gt.originalbudgetamount <> 0
      AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) IS NOT NULL
      AND COALESCE(NULLIF(p.grossarea, 0), p.usablearea) > 0
)
"""


def run_query(conn, sql, title):
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    return cols, rows


def main():
    try:
        from edp_connection import connect_databricks
    except ImportError:
        print("Run from project root with edp_connection available.")
        return 1

    conn = connect_databricks()
    if not conn:
        print("Failed to connect to Databricks.")
        return 1

    print("=" * 70)
    print("Project Type Field Analysis: jllprojecttypetext vs projecttypename")
    print("Population: Closed USD projects with budget in generictask, positive area")
    print("=" * 70)

    # 1) Total project count
    q_total = BASE_CTE + "SELECT COUNT(*) AS cnt FROM budget_projects"
    _, rows = run_query(conn, q_total, "Total")
    total = rows[0][0] if rows else 0
    print(f"\nTotal projects in population: {total:,}")

    # 2) Coverage: non-null, non-blank for each field
    q_coverage = BASE_CTE + """
SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN p.jllprojecttypetext IS NOT NULL AND TRIM(p.jllprojecttypetext) <> '' THEN 1 ELSE 0 END) AS jll_filled,
    SUM(CASE WHEN p.projecttypename IS NOT NULL AND TRIM(CAST(p.projecttypename AS STRING)) <> '' THEN 1 ELSE 0 END) AS ptn_filled
FROM budget_projects bp
INNER JOIN work_dynamics.curated.project p ON p.id = bp.project_id
"""
    _, rows = run_query(conn, q_coverage, "Coverage")
    if rows:
        r = rows[0]
        total, jll_filled, ptn_filled = r[0], r[1], r[2]
        jll_pct = 100 * jll_filled / total if total else 0
        ptn_pct = 100 * ptn_filled / total if total else 0
        print(f"\n--- Coverage (non-null, non-blank) ---")
        print(f"  jllprojecttypetext:  {jll_filled:>8,} / {total:,}  ({jll_pct:.1f}%)")
        print(f"  projecttypename:     {ptn_filled:>8,} / {total:,}  ({ptn_pct:.1f}%)")

    # 3) Distinct value counts
    q_distinct = BASE_CTE + """
SELECT
    COUNT(DISTINCT TRIM(p.jllprojecttypetext)) AS jll_distinct,
    COUNT(DISTINCT TRIM(CAST(p.projecttypename AS STRING))) AS ptn_distinct
FROM budget_projects bp
INNER JOIN work_dynamics.curated.project p ON p.id = bp.project_id
WHERE (p.jllprojecttypetext IS NOT NULL AND TRIM(p.jllprojecttypetext) <> '')
   OR (p.projecttypename IS NOT NULL AND TRIM(CAST(p.projecttypename AS STRING)) <> '')
"""
    _, rows = run_query(conn, q_distinct, "Distinct")
    if rows:
        r = rows[0]
        print(f"\n--- Distinct values (when filled) ---")
        print(f"  jllprojecttypetext:  {r[0]:,}")
        print(f"  projecttypename:     {r[1]:,}")

    # 4) Top values for jllprojecttypetext
    q_jll_top = BASE_CTE + """
SELECT COALESCE(NULLIF(TRIM(p.jllprojecttypetext), ''), '(blank)') AS val, COUNT(*) AS cnt
FROM budget_projects bp
INNER JOIN work_dynamics.curated.project p ON p.id = bp.project_id
GROUP BY 1
ORDER BY cnt DESC
LIMIT 20
"""
    _, rows = run_query(conn, q_jll_top, "jll top")
    print(f"\n--- jllprojecttypetext: Top 20 values ---")
    for r in rows:
        print(f"  {str(r[0]):45s}  {r[1]:>8,}")

    # 5) Top values for projecttypename
    q_ptn_top = BASE_CTE + """
SELECT COALESCE(NULLIF(TRIM(CAST(p.projecttypename AS STRING)), ''), '(blank)') AS val, COUNT(*) AS cnt
FROM budget_projects bp
INNER JOIN work_dynamics.curated.project p ON p.id = bp.project_id
GROUP BY 1
ORDER BY cnt DESC
LIMIT 20
"""
    _, rows = run_query(conn, q_ptn_top, "ptn top")
    print(f"\n--- projecttypename: Top 20 values ---")
    for r in rows:
        print(f"  {str(r[0]):45s}  {r[1]:>8,}")

    # 6) Coverage by source system
    q_by_source = BASE_CTE + """
SELECT
    bp.sourcesystem,
    COUNT(*) AS total,
    SUM(CASE WHEN p.jllprojecttypetext IS NOT NULL AND TRIM(p.jllprojecttypetext) <> '' THEN 1 ELSE 0 END) AS jll_filled,
    SUM(CASE WHEN p.projecttypename IS NOT NULL AND TRIM(CAST(p.projecttypename AS STRING)) <> '' THEN 1 ELSE 0 END) AS ptn_filled
FROM budget_projects bp
INNER JOIN work_dynamics.curated.project p ON p.id = bp.project_id
GROUP BY bp.sourcesystem
ORDER BY total DESC
"""
    _, rows = run_query(conn, q_by_source, "By source")
    print(f"\n--- Coverage by source system ---")
    for r in rows:
        src, tot, jll, ptn = r[0], r[1], r[2], r[3]
        jll_p = 100 * jll / tot if tot else 0
        ptn_p = 100 * ptn / tot if tot else 0
        print(f"  {str(src):20s}  total={tot:>6,}  jll={jll:>6,} ({jll_p:5.1f}%)  ptn={ptn:>6,} ({ptn_p:5.1f}%)")

    # 7) Agreement: where both filled, do they match?
    q_agreement = BASE_CTE + """
SELECT
    COUNT(*) AS both_filled,
    SUM(CASE WHEN TRIM(p.jllprojecttypetext) = TRIM(CAST(p.projecttypename AS STRING)) THEN 1 ELSE 0 END) AS match
FROM budget_projects bp
INNER JOIN work_dynamics.curated.project p ON p.id = bp.project_id
WHERE p.jllprojecttypetext IS NOT NULL AND TRIM(p.jllprojecttypetext) <> ''
  AND p.projecttypename IS NOT NULL AND TRIM(CAST(p.projecttypename AS STRING)) <> ''
"""
    _, rows = run_query(conn, q_agreement, "Agreement")
    if rows and rows[0][0] and rows[0][0] > 0:
        both, match = rows[0][0], rows[0][1]
        agree_pct = 100 * match / both
        print(f"\n--- Agreement (where both filled) ---")
        print(f"  Both filled: {both:,}  |  Match: {match:,}  ({agree_pct:.1f}%)")

    # 8) Where one is filled and the other is not
    q_mismatch = BASE_CTE + """
SELECT
    SUM(CASE WHEN (p.jllprojecttypetext IS NULL OR TRIM(p.jllprojecttypetext) = '') AND (p.projecttypename IS NOT NULL AND TRIM(CAST(p.projecttypename AS STRING)) <> '') THEN 1 ELSE 0 END) AS only_ptn,
    SUM(CASE WHEN (p.projecttypename IS NULL OR TRIM(CAST(p.projecttypename AS STRING)) = '') AND (p.jllprojecttypetext IS NOT NULL AND TRIM(p.jllprojecttypetext) <> '') THEN 1 ELSE 0 END) AS only_jll
FROM budget_projects bp
INNER JOIN work_dynamics.curated.project p ON p.id = bp.project_id
"""
    _, rows = run_query(conn, q_mismatch, "Mismatch")
    if rows:
        only_ptn, only_jll = rows[0][0], rows[0][1]
        print(f"\n--- Fill asymmetry ---")
        print(f"  Only projecttypename filled:  {only_ptn:,}")
        print(f"  Only jllprojecttypetext filled: {only_jll:,}")

    # Recommendation
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    if rows and total:
        _, cov_rows = run_query(conn, q_coverage, "")
        jll_filled = cov_rows[0][1] if cov_rows else 0
        ptn_filled = cov_rows[0][2] if cov_rows else 0
        if jll_filled >= ptn_filled and jll_filled > 0:
            print("Use jllprojecttypetext: higher or equal coverage in the budget population.")
        elif ptn_filled > jll_filled:
            print("Use projecttypename: higher coverage in the budget population.")
        else:
            print("Both fields have low coverage. Prefer jllprojecttypetext if values look cleaner.")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
