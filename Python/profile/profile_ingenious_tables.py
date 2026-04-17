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
Profile three Ingenious tables to understand their schemas, relationships, and use cases:
  - ingenious_buildings
  - ingenious_projects_sites
  - projects
"""

import sys, os

from edp_connection import execute_query

SCHEMA = "edp_sourcesystem.ingenious"

tables = [
    "ingenious_buildings",
    "ingenious_projects_sites",
    "projects",
]

for table in tables:
    fqn = f"{SCHEMA}.{table}"
    print(f"\n{'='*80}")
    print(f"TABLE: {fqn}")
    print(f"{'='*80}")

    # Schema
    print("\n--- COLUMNS ---")
    cols, rows = execute_query(f"DESCRIBE TABLE {fqn}")
    for r in rows:
        if r[0] and not r[0].startswith('#'):
            print(f"  {r[0]:40s}  {r[1]}")

    # Row count
    cols, rows = execute_query(f"SELECT COUNT(*) AS cnt FROM {fqn}")
    print(f"\n--- ROW COUNT: {rows[0][0]} ---")

    # Sample data (first 3 rows)
    print("\n--- SAMPLE (3 rows) ---")
    cols, rows = execute_query(f"SELECT * FROM {fqn} LIMIT 3")
    for i, row in enumerate(rows):
        print(f"\n  Row {i+1}:")
        for c, v in zip(cols, row):
            val_str = str(v)
            if len(val_str) > 120:
                val_str = val_str[:120] + "..."
            print(f"    {c:40s} = {val_str}")

    # Distinct value counts for key columns (to understand cardinality)
    print("\n--- DISTINCT COUNTS (all columns) ---")
    col_names = []
    cols_desc, rows_desc = execute_query(f"DESCRIBE TABLE {fqn}")
    for r in rows_desc:
        if r[0] and not r[0].startswith('#'):
            col_names.append(r[0])

    distinct_exprs = ", ".join([f"COUNT(DISTINCT `{c}`) AS `{c}`" for c in col_names])
    null_exprs = ", ".join([f"SUM(CASE WHEN `{c}` IS NULL THEN 1 ELSE 0 END) AS `{c}`" for c in col_names])

    cols, rows = execute_query(f"SELECT {distinct_exprs} FROM {fqn}")
    total_cols, total_rows = execute_query(f"SELECT COUNT(*) FROM {fqn}")
    total = total_rows[0][0]

    cols_null, rows_null = execute_query(f"SELECT {null_exprs} FROM {fqn}")

    print(f"  {'Column':40s}  {'Distinct':>10s}  {'Nulls':>10s}  {'Fill%':>8s}")
    print(f"  {'-'*40}  {'-'*10}  {'-'*10}  {'-'*8}")
    for c, d, n in zip(col_names, rows[0], rows_null[0]):
        fill = ((total - n) / total * 100) if total > 0 else 0
        print(f"  {c:40s}  {str(d):>10s}  {str(n):>10s}  {fill:>7.1f}%")

print("\n\n" + "="*80)
print("RELATIONSHIP ANALYSIS")
print("="*80)

# Check overlapping columns
print("\n--- Checking join key candidates ---")

# buildings.project_id vs projects
print("\n1. ingenious_buildings.project_id -> projects overlap:")
cols, rows = execute_query(f"""
    SELECT
        COUNT(DISTINCT b.project_id) AS building_project_ids,
        COUNT(DISTINCT p.id) AS project_ids,
        COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN b.project_id END) AS matched
    FROM {SCHEMA}.ingenious_buildings b
    LEFT JOIN {SCHEMA}.projects p ON b.project_id = p.id
""")
print(f"  Building project_ids: {rows[0][0]}, Projects: {rows[0][1]}, Matched: {rows[0][2]}")

# buildings.projects_ids (JSON array) -> projects
print("\n2. ingenious_buildings.projects_ids (JSON array) -> projects overlap:")
cols, rows = execute_query(f"""
    WITH exploded AS (
        SELECT DISTINCT pid.col AS project_id
        FROM {SCHEMA}.ingenious_buildings b
        LATERAL VIEW explode(from_json(b.projects_ids, 'ARRAY<STRING>')) pid
    )
    SELECT
        COUNT(DISTINCT e.project_id) AS building_project_ids_exploded,
        COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN e.project_id END) AS matched_to_projects
    FROM exploded e
    LEFT JOIN {SCHEMA}.projects p ON e.project_id = p.id
""")
print(f"  Distinct project IDs from buildings.projects_ids: {rows[0][0]}, Matched to projects: {rows[0][1]}")

# projects_sites.project_id -> projects
print("\n3. ingenious_projects_sites.project_id -> projects overlap:")
cols, rows = execute_query(f"""
    SELECT
        COUNT(DISTINCT ps.project_id) AS site_project_ids,
        COUNT(DISTINCT p.id) AS project_ids,
        COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN ps.project_id END) AS matched
    FROM {SCHEMA}.ingenious_projects_sites ps
    LEFT JOIN {SCHEMA}.projects p ON ps.project_id = p.id
""")
print(f"  Site project_ids: {rows[0][0]}, Projects: {rows[0][1]}, Matched: {rows[0][2]}")

# projects_sites.building_id -> buildings
print("\n4. ingenious_projects_sites.building_id -> ingenious_buildings overlap:")
cols, rows = execute_query(f"""
    SELECT
        COUNT(DISTINCT ps.building_id) AS site_building_ids,
        COUNT(DISTINCT b.id) AS building_ids,
        COUNT(DISTINCT CASE WHEN b.id IS NOT NULL THEN ps.building_id END) AS matched
    FROM {SCHEMA}.ingenious_projects_sites ps
    LEFT JOIN {SCHEMA}.ingenious_buildings b ON ps.building_id = b.id
""")
print(f"  Site building_ids: {rows[0][0]}, Buildings: {rows[0][1]}, Matched: {rows[0][2]}")

# Three-way join
print("\n5. Three-way join coverage:")
cols, rows = execute_query(f"""
    SELECT COUNT(DISTINCT ps.project_id) AS projects_with_site_and_building
    FROM {SCHEMA}.ingenious_projects_sites ps
    INNER JOIN {SCHEMA}.projects p ON ps.project_id = p.id
    INNER JOIN {SCHEMA}.ingenious_buildings b ON ps.building_id = b.id
""")
print(f"  Projects linkable through all 3 tables: {rows[0][0]}")

print("\nDone.")
