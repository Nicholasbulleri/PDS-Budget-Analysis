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
Profile ingenious_projects and run relationship analysis across all 3 tables.
"""

import sys, os

from edp_connection import execute_query

SCHEMA = "edp_sourcesystem.ingenious"

# ── Profile ingenious_projects ──
fqn = f"{SCHEMA}.ingenious_projects"
print(f"{'='*80}")
print(f"TABLE: {fqn}")
print(f"{'='*80}")

print("\n--- COLUMNS ---")
cols_desc, rows_desc = execute_query(f"DESCRIBE TABLE {fqn}")
col_names = []
for r in rows_desc:
    if r[0] and not r[0].startswith('#'):
        col_names.append(r[0])
        print(f"  {r[0]:40s}  {r[1]}")

cols, rows = execute_query(f"SELECT COUNT(*) FROM {fqn}")
total = rows[0][0]
print(f"\n--- ROW COUNT: {total} ---")

print("\n--- SAMPLE (3 rows) ---")
cols, rows = execute_query(f"SELECT * FROM {fqn} LIMIT 3")
for i, row in enumerate(rows):
    print(f"\n  Row {i+1}:")
    for c, v in zip(cols, row):
        val_str = str(v)
        if len(val_str) > 150:
            val_str = val_str[:150] + "..."
        print(f"    {c:40s} = {val_str}")

print("\n--- DISTINCT COUNTS ---")
distinct_exprs = ", ".join([f"COUNT(DISTINCT `{c}`) AS `{c}`" for c in col_names])
null_exprs = ", ".join([f"SUM(CASE WHEN `{c}` IS NULL THEN 1 ELSE 0 END) AS `{c}`" for c in col_names])

cols_d, rows_d = execute_query(f"SELECT {distinct_exprs} FROM {fqn}")
cols_n, rows_n = execute_query(f"SELECT {null_exprs} FROM {fqn}")

print(f"  {'Column':40s}  {'Distinct':>10s}  {'Nulls':>10s}  {'Fill%':>8s}")
print(f"  {'-'*40}  {'-'*10}  {'-'*10}  {'-'*8}")
for c, d, n in zip(col_names, rows_d[0], rows_n[0]):
    fill = ((total - n) / total * 100) if total > 0 else 0
    print(f"  {c:40s}  {str(d):>10s}  {str(n):>10s}  {fill:>7.1f}%")


# ── Relationship Analysis ──
print(f"\n\n{'='*80}")
print("RELATIONSHIP ANALYSIS")
print(f"{'='*80}")

print("\n1. ingenious_buildings.project_id (single) -> ingenious_projects:")
cols, rows = execute_query(f"""
    SELECT
        COUNT(DISTINCT b.project_id) AS building_project_ids,
        COUNT(DISTINCT p.id) AS total_projects,
        COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN b.project_id END) AS matched
    FROM {SCHEMA}.ingenious_buildings b
    LEFT JOIN {SCHEMA}.ingenious_projects p ON b.project_id = p.id
""")
print(f"  Building distinct project_id values: {rows[0][0]}")
print(f"  Total projects: {rows[0][1]}")
print(f"  Matched: {rows[0][2]}")

print("\n2. ingenious_buildings.projects_ids (JSON array) -> ingenious_projects:")
cols, rows = execute_query(f"""
    WITH exploded AS (
        SELECT DISTINCT pid.col AS project_id
        FROM {SCHEMA}.ingenious_buildings b
        LATERAL VIEW explode(from_json(b.projects_ids, 'ARRAY<STRING>')) pid
    )
    SELECT
        COUNT(DISTINCT e.project_id) AS building_projects_ids_exploded,
        COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN e.project_id END) AS matched
    FROM exploded e
    LEFT JOIN {SCHEMA}.ingenious_projects p ON e.project_id = p.id
""")
print(f"  Distinct project IDs from buildings.projects_ids array: {rows[0][0]}")
print(f"  Matched to ingenious_projects: {rows[0][1]}")

print("\n3. ingenious_projects_sites.project_id -> ingenious_projects:")
cols, rows = execute_query(f"""
    SELECT
        COUNT(DISTINCT ps.project_id) AS site_project_ids,
        COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN ps.project_id END) AS matched
    FROM {SCHEMA}.ingenious_projects_sites ps
    LEFT JOIN {SCHEMA}.ingenious_projects p ON ps.project_id = p.id
""")
print(f"  Sites distinct project_id values: {rows[0][0]}")
print(f"  Matched to ingenious_projects: {rows[0][1]}")

print("\n4. ingenious_projects_sites.building_id -> ingenious_buildings:")
cols, rows = execute_query(f"""
    SELECT
        COUNT(DISTINCT ps.building_id) AS site_building_ids,
        COUNT(DISTINCT b.id) AS total_buildings,
        COUNT(DISTINCT CASE WHEN b.id IS NOT NULL THEN ps.building_id END) AS matched
    FROM {SCHEMA}.ingenious_projects_sites ps
    LEFT JOIN {SCHEMA}.ingenious_buildings b ON ps.building_id = b.id
""")
print(f"  Sites distinct building_id values: {rows[0][0]}")
print(f"  Total buildings: {rows[0][1]}")
print(f"  Matched: {rows[0][2]}")

print("\n5. Three-way join (projects_sites as bridge):")
cols, rows = execute_query(f"""
    SELECT
        COUNT(DISTINCT ps.project_id) AS projects_linked,
        COUNT(DISTINCT ps.building_id) AS buildings_linked,
        COUNT(*) AS total_site_rows
    FROM {SCHEMA}.ingenious_projects_sites ps
    INNER JOIN {SCHEMA}.ingenious_projects p ON ps.project_id = p.id
    INNER JOIN {SCHEMA}.ingenious_buildings b ON ps.building_id = b.id
""")
print(f"  Projects linked through all 3: {rows[0][0]}")
print(f"  Buildings linked through all 3: {rows[0][1]}")
print(f"  Total site rows in join: {rows[0][2]}")

print("\n6. Buildings with multiple projects (via projects_ids array):")
cols, rows = execute_query(f"""
    SELECT
        num_projects,
        COUNT(*) AS building_count
    FROM (
        SELECT id, size(from_json(projects_ids, 'ARRAY<STRING>')) AS num_projects
        FROM {SCHEMA}.ingenious_buildings
    )
    GROUP BY num_projects
    ORDER BY num_projects
""")
for r in rows:
    print(f"  {r[0]} project(s): {r[1]} buildings")

print("\n7. Projects with multiple sites:")
cols, rows = execute_query(f"""
    SELECT
        num_sites,
        COUNT(*) AS project_count
    FROM (
        SELECT project_id, COUNT(*) AS num_sites
        FROM {SCHEMA}.ingenious_projects_sites
        GROUP BY project_id
    )
    GROUP BY num_sites
    ORDER BY num_sites
""")
for r in rows:
    print(f"  {r[0]} site(s): {r[1]} projects")

print("\n8. Location field overlap — which tables have address data:")
cols, rows = execute_query(f"""
    SELECT
        'ingenious_buildings' AS tbl,
        COUNT(*) AS total,
        SUM(CASE WHEN address IS NOT NULL AND address != '' THEN 1 ELSE 0 END) AS has_address,
        SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) AS has_lat_long,
        SUM(CASE WHEN gross_area IS NOT NULL THEN 1 ELSE 0 END) AS has_gross_area,
        SUM(CASE WHEN rentable_area IS NOT NULL THEN 1 ELSE 0 END) AS has_rentable_area
    FROM {SCHEMA}.ingenious_buildings
    UNION ALL
    SELECT
        'ingenious_projects_sites' AS tbl,
        COUNT(*) AS total,
        SUM(CASE WHEN address IS NOT NULL AND address != '' THEN 1 ELSE 0 END) AS has_address,
        CAST(NULL AS BIGINT) AS has_lat_long,
        SUM(CASE WHEN gross_area IS NOT NULL THEN 1 ELSE 0 END) AS has_gross_area,
        SUM(CASE WHEN rentable_area IS NOT NULL THEN 1 ELSE 0 END) AS has_rentable_area
    FROM {SCHEMA}.ingenious_projects_sites
""")
print(f"  {'Table':30s}  {'Total':>7s}  {'Address':>9s}  {'Lat/Lng':>9s}  {'GrossArea':>10s}  {'RentArea':>10s}")
print(f"  {'-'*30}  {'-'*7}  {'-'*9}  {'-'*9}  {'-'*10}  {'-'*10}")
for r in rows:
    print(f"  {r[0]:30s}  {str(r[1]):>7s}  {str(r[2]):>9s}  {str(r[3]):>9s}  {str(r[4]):>10s}  {str(r[5]):>10s}")

# Check if ingenious_projects has any location-like fields
print("\n9. ingenious_projects location-related fields:")
cols, rows = execute_query(f"""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'ingenious'
      AND table_name = 'ingenious_projects'
      AND (
        lower(column_name) LIKE '%address%'
        OR lower(column_name) LIKE '%city%'
        OR lower(column_name) LIKE '%state%'
        OR lower(column_name) LIKE '%country%'
        OR lower(column_name) LIKE '%location%'
        OR lower(column_name) LIKE '%site%'
        OR lower(column_name) LIKE '%area%'
        OR lower(column_name) LIKE '%lat%'
        OR lower(column_name) LIKE '%lon%'
        OR lower(column_name) LIKE '%building%'
        OR lower(column_name) LIKE '%property%'
      )
""")
for r in rows:
    print(f"  {r[0]:40s}  {r[1]}")

print("\nDone.")
