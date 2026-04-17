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
Find the projects table and get buildings distinct counts.
"""

import sys, os

from edp_connection import execute_query

SCHEMA = "edp_sourcesystem.ingenious"

# Find the projects table
print("--- Searching for 'projects' table in ingenious schema ---")
cols, rows = execute_query(f"SHOW TABLES IN {SCHEMA}")
for r in rows:
    print(f"  {r}")

print("\n\n--- ingenious_buildings DISTINCT COUNTS ---")
cols_desc, rows_desc = execute_query(f"DESCRIBE TABLE {SCHEMA}.ingenious_buildings")
col_names = [r[0] for r in rows_desc if r[0] and not r[0].startswith('#')]

distinct_exprs = ", ".join([f"COUNT(DISTINCT `{c}`) AS `{c}`" for c in col_names])
null_exprs = ", ".join([f"SUM(CASE WHEN `{c}` IS NULL THEN 1 ELSE 0 END) AS `{c}`" for c in col_names])

cols, rows = execute_query(f"SELECT {distinct_exprs} FROM {SCHEMA}.ingenious_buildings")
total_cols, total_rows = execute_query(f"SELECT COUNT(*) FROM {SCHEMA}.ingenious_buildings")
total = total_rows[0][0]
cols_null, rows_null = execute_query(f"SELECT {null_exprs} FROM {SCHEMA}.ingenious_buildings")

print(f"  {'Column':40s}  {'Distinct':>10s}  {'Nulls':>10s}  {'Fill%':>8s}")
print(f"  {'-'*40}  {'-'*10}  {'-'*10}  {'-'*8}")
for c, d, n in zip(col_names, rows[0], rows_null[0]):
    fill = ((total - n) / total * 100) if total > 0 else 0
    print(f"  {c:40s}  {str(d):>10s}  {str(n):>10s}  {fill:>7.1f}%")
