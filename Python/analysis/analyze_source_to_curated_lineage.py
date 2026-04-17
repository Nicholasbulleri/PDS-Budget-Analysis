#!/usr/bin/env python3
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
Analyze lineage from source system (edp_sourcesystem.ingenious) to curated schema (work_dynamics.curated)
"""

from edp_connection import execute_query
import json
import re
from collections import defaultdict

def get_curated_tables():
    """Get all tables in work_dynamics.curated schema"""
    print("Fetching all tables in work_dynamics.curated...")
    
    try:
        cols, results = execute_query("""
            SELECT table_name 
            FROM system.information_schema.tables 
            WHERE table_schema = 'curated' 
            AND table_catalog = 'work_dynamics'
            ORDER BY table_name
        """)
        
        tables = []
        for row in results:
            if hasattr(row, '__getitem__'):
                table_name = row[0] if len(row) > 0 else None
                if table_name:
                    tables.append(table_name)
        
        print(f"Found {len(tables)} tables in curated schema")
        return sorted(tables)
    except Exception as e:
        print(f"Error fetching curated tables: {e}")
        return []

def get_source_system_tables():
    """Get all tables in edp_sourcesystem.ingenious"""
    print("Fetching all tables in edp_sourcesystem.ingenious...")
    
    try:
        cols, results = execute_query("SHOW TABLES IN edp_sourcesystem.ingenious")
        
        tables = []
        for row in results:
            if len(row) >= 2:
                table_name = row[1] if hasattr(row, '__getitem__') else str(row)
                if table_name:
                    tables.append(table_name)
        
        print(f"Found {len(tables)} tables in source system")
        return sorted(tables)
    except Exception as e:
        print(f"Error fetching source tables: {e}")
        return []

def get_table_definition(table_name, schema='curated', catalog='work_dynamics'):
    """Get the CREATE TABLE or CREATE VIEW definition"""
    try:
        cols, results = execute_query(f"SHOW CREATE TABLE {catalog}.{schema}.{table_name}")
        if results:
            definition = ' '.join([str(row) for row in results])
            return definition
    except Exception as e:
        # Might be a view or table
        pass
    return None

def extract_source_tables_from_sql(sql_text):
    """Extract table references from SQL, focusing on edp_sourcesystem.ingenious"""
    if not sql_text:
        return []
    
    sources = set()
    
    # Pattern 1: FROM edp_sourcesystem.ingenious.table_name
    pattern1 = r'FROM\s+edp_sourcesystem\.ingenious\.([a-zA-Z0-9_`]+)'
    matches = re.findall(pattern1, sql_text, re.IGNORECASE)
    for match in matches:
        clean_match = match.strip('`').strip()
        if clean_match:
            sources.add(f"edp_sourcesystem.ingenious.{clean_match}")
    
    # Pattern 2: FROM `edp_sourcesystem`.`ingenious`.`table_name`
    pattern2 = r'FROM\s+`edp_sourcesystem`\.`ingenious`\.`([a-zA-Z0-9_]+)`'
    matches = re.findall(pattern2, sql_text, re.IGNORECASE)
    for match in matches:
        if match:
            sources.add(f"edp_sourcesystem.ingenious.{match}")
    
    # Pattern 3: JOIN edp_sourcesystem.ingenious.table_name
    pattern3 = r'JOIN\s+edp_sourcesystem\.ingenious\.([a-zA-Z0-9_`]+)'
    matches = re.findall(pattern3, sql_text, re.IGNORECASE)
    for match in matches:
        clean_match = match.strip('`').strip()
        if clean_match:
            sources.add(f"edp_sourcesystem.ingenious.{clean_match}")
    
    # Pattern 4: Look for any reference to ingenious schema
    pattern4 = r'(edp_sourcesystem\.ingenious\.[a-zA-Z0-9_`]+)'
    matches = re.findall(pattern4, sql_text, re.IGNORECASE)
    for match in matches:
        clean_match = match.strip('`').strip()
        if clean_match:
            sources.add(clean_match)
    
    return sorted(list(sources))

def get_lineage_from_system_table(table_name):
    """Try to get lineage from Unity Catalog system tables"""
    upstream = []
    
    try:
        query = f"""
            SELECT 
                source_catalog_name,
                source_schema_name,
                source_table_name
            FROM system.access.table_lineage
            WHERE destination_catalog_name = 'work_dynamics' 
              AND destination_schema_name = 'curated'
              AND destination_table_name = '{table_name}'
              AND source_schema_name = 'ingenious'
        """
        cols, results = execute_query(query)
        
        for row in results:
            if hasattr(row, '__getitem__'):
                catalog = row[0] if len(row) > 0 else None
                schema = row[1] if len(row) > 1 else None
                table = row[2] if len(row) > 2 else None
                
                if catalog and schema and table:
                    upstream.append(f"{catalog}.{schema}.{table}")
                elif schema and table:
                    upstream.append(f"{schema}.{table}")
    except Exception as e:
        # Lineage might not be available
        pass
    
    return upstream

def analyze_source_to_curated_lineage():
    """Analyze lineage from source system to curated schema"""
    print("=" * 80)
    print("Analyzing Lineage: edp_sourcesystem.ingenious -> work_dynamics.curated")
    print("=" * 80)
    print()
    
    # Get curated tables
    curated_tables = get_curated_tables()
    if not curated_tables:
        print("No curated tables found")
        return
    
    # Get source system tables for reference
    source_tables = get_source_system_tables()
    print(f"Source system has {len(source_tables)} tables for reference\n")
    
    # Analyze each curated table
    lineage_map = {}
    
    for i, table_name in enumerate(curated_tables, 1):
        print(f"[{i}/{len(curated_tables)}] Analyzing: {table_name}")
        
        sources = {
            'curated_table': table_name,
            'upstream_source_tables': [],
            'source_method': []
        }
        
        # Method 1: Try Unity Catalog lineage
        lineage_sources = get_lineage_from_system_table(table_name)
        if lineage_sources:
            sources['upstream_source_tables'].extend(lineage_sources)
            sources['source_method'].append('unity_catalog_lineage')
            print(f"  Found {len(lineage_sources)} sources via Unity Catalog lineage")
        
        # Method 2: Parse table/view definition
        table_def = get_table_definition(table_name)
        if table_def:
            sql_sources = extract_source_tables_from_sql(table_def)
            if sql_sources:
                sources['upstream_source_tables'].extend(sql_sources)
                sources['source_method'].append('definition_parsing')
                print(f"  Found {len(sql_sources)} sources via definition parsing")
        
        # Remove duplicates
        sources['upstream_source_tables'] = sorted(list(set(sources['upstream_source_tables'])))
        
        lineage_map[table_name] = sources
        
        if sources['upstream_source_tables']:
            print(f"  Total unique sources: {len(sources['upstream_source_tables'])}")
            for src in sources['upstream_source_tables']:
                print(f"    - {src}")
        else:
            print(f"  No upstream sources identified")
        print()
    
    # Generate report
    print("=" * 80)
    print("Generating Lineage Report...")
    print("=" * 80)
    
    # Create markdown report
    md_content = "# Source System to Curated Schema Lineage\n\n"
    md_content += "**Source System:** `edp_sourcesystem.ingenious`\n\n"
    md_content += "**Target Schema:** `work_dynamics.curated`\n\n"
    md_content += f"**Total Curated Tables Analyzed:** {len(curated_tables)}\n\n"
    md_content += "---\n\n"
    
    # Group by source table
    by_source = defaultdict(list)
    for curated_table, sources_info in lineage_map.items():
        for source_table in sources_info['upstream_source_tables']:
            by_source[source_table].append(curated_table)
    
    # Summary by source table
    md_content += "## Lineage by Source Table\n\n"
    if by_source:
        for source_table in sorted(by_source.keys()):
            curated_list = sorted(by_source[source_table])
            md_content += f"### {source_table}\n\n"
            md_content += f"**Feeds into {len(curated_list)} curated table(s):**\n\n"
            for curated_table in curated_list:
                md_content += f"- `{curated_table}`\n"
            md_content += "\n"
    else:
        md_content += "*No source system lineage identified*\n\n"
    
    # Detailed table-by-table breakdown
    md_content += "---\n\n"
    md_content += "## Detailed Table-by-Table Breakdown\n\n"
    
    for curated_table in sorted(curated_tables):
        sources_info = lineage_map[curated_table]
        md_content += f"### {curated_table}\n\n"
        
        if sources_info['upstream_source_tables']:
            md_content += f"**Upstream Source Tables ({len(sources_info['upstream_source_tables'])}):**\n\n"
            for source_table in sources_info['upstream_source_tables']:
                md_content += f"- `{source_table}`\n"
            md_content += "\n"
            md_content += f"**Detection Method:** {', '.join(sources_info['source_method'])}\n\n"
        else:
            md_content += "*No upstream source system tables identified*\n\n"
        
        md_content += "---\n\n"
    
    # Summary statistics
    md_content += "## Summary Statistics\n\n"
    tables_with_sources = len([t for t in lineage_map.values() if t['upstream_source_tables']])
    total_source_links = sum(len(t['upstream_source_tables']) for t in lineage_map.values())
    
    md_content += f"- **Curated tables with identified sources:** {tables_with_sources}/{len(curated_tables)}\n"
    md_content += f"- **Total source-to-curated links:** {total_source_links}\n"
    md_content += f"- **Unique source tables referenced:** {len(by_source)}\n"
    
    # Save markdown report
    with open('INGENIOUS_SOURCE_TO_CURATED_LINEAGE.md', 'w') as f:
        f.write(md_content)
    print(f"✓ Markdown report saved to: INGENIOUS_SOURCE_TO_CURATED_LINEAGE.md")
    
    # Save JSON export
    output = {
        'source_system': 'edp_sourcesystem.ingenious',
        'target_schema': 'work_dynamics.curated',
        'total_curated_tables': len(curated_tables),
        'lineage_map': lineage_map,
        'summary': {
            'tables_with_sources': tables_with_sources,
            'total_source_links': total_source_links,
            'unique_source_tables': len(by_source)
        },
        'lineage_by_source': {k: sorted(v) for k, v in by_source.items()}
    }
    
    with open('INGENIOUS_SOURCE_TO_CURATED_LINEAGE.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"✓ JSON export saved to: INGENIOUS_SOURCE_TO_CURATED_LINEAGE.json")
    
    # Print summary
    print("\n" + "=" * 80)
    print("Analysis Complete")
    print("=" * 80)
    print(f"\nCurated Tables Analyzed: {len(curated_tables)}")
    print(f"Tables with Identified Sources: {tables_with_sources}")
    print(f"Total Source Links: {total_source_links}")
    print(f"Unique Source Tables: {len(by_source)}")
    
    if by_source:
        print("\nSource Tables Used:")
        for source_table in sorted(by_source.keys()):
            curated_count = len(by_source[source_table])
            print(f"  {source_table}: feeds {curated_count} curated table(s)")

if __name__ == "__main__":
    analyze_source_to_curated_lineage()







