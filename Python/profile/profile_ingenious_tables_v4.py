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
Relationship analysis across ingenious_buildings, ingenious_projects_sites, ingenious_projects.
"""

import sys, os

from edp_connection import execute_query

SCHEMA = "edp_sourcesystem.ingenious"

print("="*80)
print("RELATIONSHIP ANALYSIS")
print("="*80)

print("\n1. ingenious_buildings.projects_ids (JSON array) -> ingenious_projects:")
cols, rows = execute_query(f"""
    WITH exploded AS (
        SELECT b.id AS building_id, pid.col AS project_id
        FROM {SCHEMA}.ingenious_buildings b
        LATERAL VIEW explode(from_json(b.projects_ids, 'ARRAY<STRING>')) pid
    )
    SELECT
        COUNT(DISTINCT e.building_id) AS buildings_with_projects,
        COUNT(DISTINCT e.project_id) AS distinct_project_ids,
        COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN e.project_id END) AS matched_to_projects,
        COUNT(DISTINCT CASE WHEN p.id IS NULL THEN e.project_id END) AS unmatched
    FROM exploded e
    LEFT JOIN {SCHEMA}.ingenious_projects p ON e.project_id = p.id
""")
print(f"  Buildings with at least one project ID: {rows[0][0]}")
print(f"  Distinct project IDs referenced: {rows[0][1]}")
print(f"  Matched to ingenious_projects: {rows[0][2]}")
print(f"  Unmatched (orphan references): {rows[0][3]}")

print("\n2. ingenious_projects_sites.project_id -> ingenious_projects:")
cols, rows = execute_query(f"""
    SELECT
        COUNT(DISTINCT ps.project_id) AS site_project_ids,
        COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN ps.project_id END) AS matched
    FROM {SCHEMA}.ingenious_projects_sites ps
    LEFT JOIN {SCHEMA}.ingenious_projects p ON ps.project_id = p.id
""")
print(f"  Sites distinct project_id values: {rows[0][0]}")
print(f"  Matched to ingenious_projects: {rows[0][1]}")

print("\n3. ingenious_projects_sites.building_id -> ingenious_buildings:")
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

print("\n4. Three-way join (projects_sites as bridge table):")
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

print("\n5. Coverage: what % of projects have a site/building link?")
cols, rows = execute_query(f"""
    SELECT
        COUNT(DISTINCT p.id) AS total_projects,
        COUNT(DISTINCT ps.project_id) AS projects_with_site,
        ROUND(COUNT(DISTINCT ps.project_id) * 100.0 / COUNT(DISTINCT p.id), 1) AS pct_with_site
    FROM {SCHEMA}.ingenious_projects p
    LEFT JOIN {SCHEMA}.ingenious_projects_sites ps ON p.id = ps.project_id
""")
print(f"  Total projects: {rows[0][0]}")
print(f"  Projects with at least one site record: {rows[0][1]}")
print(f"  Coverage: {rows[0][2]}%")

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

print("\n8. Location data quality comparison:")
cols, rows = execute_query(f"""
    SELECT
        'ingenious_buildings' AS tbl,
        COUNT(*) AS total,
        SUM(CASE WHEN address IS NOT NULL AND address != '' AND address != '{{}}' THEN 1 ELSE 0 END) AS has_address,
        SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) AS has_lat_long,
        SUM(CASE WHEN gross_area IS NOT NULL THEN 1 ELSE 0 END) AS has_gross_area,
        SUM(CASE WHEN rentable_area IS NOT NULL THEN 1 ELSE 0 END) AS has_rentable_area,
        SUM(CASE WHEN name IS NOT NULL THEN 1 ELSE 0 END) AS has_name,
        SUM(CASE WHEN classification IS NOT NULL THEN 1 ELSE 0 END) AS has_classification
    FROM {SCHEMA}.ingenious_buildings
    UNION ALL
    SELECT
        'projects_sites' AS tbl,
        COUNT(*) AS total,
        SUM(CASE WHEN address IS NOT NULL AND address != '' AND address != '{{}}' THEN 1 ELSE 0 END) AS has_address,
        CAST(0 AS BIGINT) AS has_lat_long,
        SUM(CASE WHEN gross_area IS NOT NULL THEN 1 ELSE 0 END) AS has_gross_area,
        SUM(CASE WHEN rentable_area IS NOT NULL THEN 1 ELSE 0 END) AS has_rentable_area,
        CAST(0 AS BIGINT) AS has_name,
        CAST(0 AS BIGINT) AS has_classification
    FROM {SCHEMA}.ingenious_projects_sites
""")
print(f"  {'Table':25s}  {'Total':>7s}  {'Addr':>7s}  {'LatLng':>7s}  {'Gross':>7s}  {'Rent':>7s}  {'Name':>7s}  {'Class':>7s}")
print(f"  {'-'*25}  {'-'*7}  {'-'*7}  {'-'*7}  {'-'*7}  {'-'*7}  {'-'*7}  {'-'*7}")
for r in rows:
    print(f"  {r[0]:25s}  {str(r[1]):>7s}  {str(r[2]):>7s}  {str(r[3]):>7s}  {str(r[4]):>7s}  {str(r[5]):>7s}  {str(r[6]):>7s}  {str(r[7]):>7s}")

print("\n9. Do projects_sites and buildings have the same address for the same building_id?")
cols, rows = execute_query(f"""
    SELECT
        COUNT(*) AS total_pairs,
        SUM(CASE WHEN ps.address = b.address THEN 1 ELSE 0 END) AS exact_match,
        SUM(CASE WHEN ps.address != b.address THEN 1 ELSE 0 END) AS different,
        ROUND(SUM(CASE WHEN ps.address = b.address THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_match
    FROM {SCHEMA}.ingenious_projects_sites ps
    INNER JOIN {SCHEMA}.ingenious_buildings b ON ps.building_id = b.id
    WHERE ps.address IS NOT NULL AND b.address IS NOT NULL
""")
print(f"  Total pairs: {rows[0][0]}")
print(f"  Exact address match: {rows[0][1]} ({rows[0][3]}%)")
print(f"  Different address: {rows[0][2]}")

print("\n10. Domain distribution across tables:")
for tbl in ['ingenious_buildings', 'ingenious_projects_sites', 'ingenious_projects']:
    cols, rows = execute_query(f"""
        SELECT domain_name, COUNT(*) AS cnt
        FROM {SCHEMA}.{tbl}
        GROUP BY domain_name
        ORDER BY cnt DESC
    """)
    print(f"\n  {tbl}:")
    for r in rows:
        print(f"    {r[0]:45s}  {r[1]}")

print("\nDone.")
