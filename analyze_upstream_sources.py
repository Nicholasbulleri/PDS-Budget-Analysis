#!/usr/bin/env python3
"""
Analyze upstream data sources for all vw_ingenious curated consumption views
"""

from edp_connection import execute_query
import json
import re
from collections import defaultdict

def get_view_definition(view_name):
    """Get the CREATE VIEW definition for a view"""
    try:
        cols, results = execute_query(f"SHOW CREATE TABLE work_dynamics.curated_consumption.{view_name}")
        if results:
            # Combine all rows into a single string
            definition = ' '.join([str(row) for row in results])
            return definition
    except Exception as e:
        print(f"  Warning: Could not get view definition for {view_name}: {e}")
    return None

def extract_source_tables_from_sql(sql_text):
    """Extract table references from SQL"""
    if not sql_text:
        return []
    
    sources = set()
    
    # Pattern 1: FROM table_name or FROM schema.table_name
    from_pattern = r'FROM\s+([a-zA-Z0-9_\.`]+)'
    matches = re.findall(from_pattern, sql_text, re.IGNORECASE)
    for match in matches:
        # Clean up backticks and normalize
        clean_match = match.strip('`').strip()
        if clean_match and not clean_match.upper() in ['SELECT', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER']:
            sources.add(clean_match)
    
    # Pattern 2: JOIN table_name
    join_pattern = r'JOIN\s+([a-zA-Z0-9_\.`]+)'
    matches = re.findall(join_pattern, sql_text, re.IGNORECASE)
    for match in matches:
        clean_match = match.strip('`').strip()
        if clean_match:
            sources.add(clean_match)
    
    # Pattern 3: Table references in FROM/JOIN with schema
    schema_table_pattern = r'FROM\s+([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)'
    matches = re.findall(schema_table_pattern, sql_text, re.IGNORECASE)
    for schema, table in matches:
        sources.add(f"{schema}.{table}")
    
    # Filter out common SQL keywords and functions
    filtered_sources = []
    exclude_keywords = {'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 
                       'FULL', 'OUTER', 'ON', 'AND', 'OR', 'GROUP', 'ORDER', 'BY',
                       'HAVING', 'UNION', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
                       'AS', 'IS', 'NULL', 'NOT', 'IN', 'EXISTS', 'LIKE', 'BETWEEN'}
    
    for source in sources:
        parts = source.split('.')
        if len(parts) == 1:
            table_name = parts[0].lower()
        else:
            table_name = parts[-1].lower()
        
        if table_name not in exclude_keywords and len(table_name) > 1:
            filtered_sources.append(source)
    
    return sorted(list(set(filtered_sources)))

def get_lineage_from_system_table(view_name):
    """Try to get lineage from Unity Catalog system tables"""
    upstream = []
    
    try:
        # Try system.access.table_lineage
        query = f"""
            SELECT 
                source_catalog_name,
                source_schema_name,
                source_table_name
            FROM system.access.table_lineage
            WHERE destination_catalog_name = 'work_dynamics' 
              AND destination_schema_name = 'curated_consumption'
              AND destination_table_name = '{view_name}'
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
                elif table:
                    upstream.append(table)
    except Exception as e:
        # Lineage might not be available
        pass
    
    return upstream

def analyze_all_upstream_sources():
    """Analyze upstream sources for all vw_ingenious views"""
    print("=" * 80)
    print("Analyzing Upstream Data Sources for vw_ingenious Views")
    print("=" * 80)
    print()
    
    # Get all views
    print("Fetching all vw_ingenious views...")
    cols, results = execute_query("""
        SELECT table_name 
        FROM system.information_schema.tables 
        WHERE table_schema = 'curated_consumption' 
        AND table_catalog = 'work_dynamics'
        AND table_name LIKE 'vw_ingenious%'
        ORDER BY table_name
    """)
    
    views = []
    for row in results:
        if hasattr(row, '__getitem__'):
            view_name = row[0] if len(row) > 0 else None
            if view_name:
                views.append(view_name)
    
    print(f"Found {len(views)} views to analyze\n")
    
    # Analyze each view
    upstream_sources = {}
    
    for i, view_name in enumerate(views, 1):
        print(f"[{i}/{len(views)}] Analyzing: {view_name}")
        
        sources = {
            'view_name': view_name,
            'upstream_tables': [],
            'upstream_schemas': set(),
            'upstream_catalogs': set(),
            'source_method': []
        }
        
        # Method 1: Try Unity Catalog lineage
        lineage_sources = get_lineage_from_system_table(view_name)
        if lineage_sources:
            sources['upstream_tables'].extend(lineage_sources)
            sources['source_method'].append('unity_catalog_lineage')
            print(f"  Found {len(lineage_sources)} sources via Unity Catalog lineage")
        
        # Method 2: Parse view definition
        view_def = get_view_definition(view_name)
        if view_def:
            sql_sources = extract_source_tables_from_sql(view_def)
            if sql_sources:
                sources['upstream_tables'].extend(sql_sources)
                sources['source_method'].append('view_definition_parsing')
                print(f"  Found {len(sql_sources)} sources via view definition parsing")
        
        # Extract schema and catalog info
        for table_ref in sources['upstream_tables']:
            parts = table_ref.split('.')
            if len(parts) == 3:
                sources['upstream_catalogs'].add(parts[0])
                sources['upstream_schemas'].add(parts[1])
            elif len(parts) == 2:
                sources['upstream_schemas'].add(parts[0])
        
        # Convert sets to lists for JSON
        sources['upstream_schemas'] = sorted(list(sources['upstream_schemas']))
        sources['upstream_catalogs'] = sorted(list(sources['upstream_catalogs']))
        sources['upstream_tables'] = sorted(list(set(sources['upstream_tables'])))
        
        upstream_sources[view_name] = sources
        
        if sources['upstream_tables']:
            print(f"  Total unique sources: {len(sources['upstream_tables'])}")
        else:
            print(f"  No upstream sources identified")
        print()
    
    # Generate summary report
    print("=" * 80)
    print("Generating Upstream Sources Report...")
    print("=" * 80)
    
    # Create markdown report
    md_content = "# Upstream Data Sources for Ingenious Curated Consumption Views\n\n"
    md_content += f"**Total Views Analyzed:** {len(views)}\n\n"
    md_content += "---\n\n"
    
    # Group by upstream schema/catalog
    by_schema = defaultdict(list)
    by_catalog = defaultdict(list)
    all_sources = set()
    
    for view_name, sources_info in upstream_sources.items():
        for table_ref in sources_info['upstream_tables']:
            all_sources.add(table_ref)
            parts = table_ref.split('.')
            if len(parts) >= 2:
                schema = parts[-2] if len(parts) == 3 else parts[0]
                by_schema[schema].append((view_name, table_ref))
            if len(parts) == 3:
                catalog = parts[0]
                by_catalog[catalog].append((view_name, table_ref))
    
    # Summary by schema
    md_content += "## Upstream Sources by Schema\n\n"
    for schema in sorted(by_schema.keys()):
        views_using = set([v for v, t in by_schema[schema]])
        md_content += f"### {schema}\n\n"
        md_content += f"**Used by {len(views_using)} views:** {', '.join(sorted(views_using))}\n\n"
        md_content += "**Source Tables:**\n\n"
        unique_tables = sorted(set([t for v, t in by_schema[schema]]))
        for table in unique_tables:
            md_content += f"- `{table}`\n"
        md_content += "\n"
    
    # Detailed view-by-view breakdown
    md_content += "---\n\n"
    md_content += "## Detailed View-by-View Breakdown\n\n"
    
    for view_name in sorted(views):
        sources_info = upstream_sources[view_name]
        md_content += f"### {view_name}\n\n"
        
        if sources_info['upstream_tables']:
            md_content += f"**Upstream Sources ({len(sources_info['upstream_tables'])}):**\n\n"
            for table in sources_info['upstream_tables']:
                md_content += f"- `{table}`\n"
            md_content += "\n"
            
            if sources_info['upstream_schemas']:
                md_content += f"**Source Schemas:** {', '.join(sources_info['upstream_schemas'])}\n\n"
            if sources_info['upstream_catalogs']:
                md_content += f"**Source Catalogs:** {', '.join(sources_info['upstream_catalogs'])}\n\n"
            md_content += f"**Detection Method:** {', '.join(sources_info['source_method'])}\n\n"
        else:
            md_content += "*No upstream sources identified*\n\n"
        
        md_content += "---\n\n"
    
    # Summary statistics
    md_content += "## Summary Statistics\n\n"
    views_with_sources = len([v for v in upstream_sources.values() if v['upstream_tables']])
    md_content += f"- **Views with identified sources:** {views_with_sources}/{len(views)}\n"
    md_content += f"- **Total unique upstream tables:** {len(all_sources)}\n"
    md_content += f"- **Unique source schemas:** {len(by_schema)}\n"
    md_content += f"- **Unique source catalogs:** {len(by_catalog)}\n"
    
    if by_schema:
        md_content += "\n**Source Schemas:**\n"
        for schema in sorted(by_schema.keys()):
            views_count = len(set([v for v, t in by_schema[schema]]))
            md_content += f"- `{schema}`: used by {views_count} views\n"
    
    if by_catalog:
        md_content += "\n**Source Catalogs:**\n"
        for catalog in sorted(by_catalog.keys()):
            views_count = len(set([v for v, t in by_catalog[catalog]]))
            md_content += f"- `{catalog}`: used by {views_count} views\n"
    
    # Save markdown report
    with open('INGENIOUS_UPSTREAM_SOURCES.md', 'w') as f:
        f.write(md_content)
    print(f"✓ Markdown report saved to: INGENIOUS_UPSTREAM_SOURCES.md")
    
    # Save JSON export
    output = {
        'total_views': len(views),
        'views_analyzed': views,
        'upstream_sources': upstream_sources,
        'summary': {
            'total_unique_sources': len(all_sources),
            'unique_schemas': len(by_schema),
            'unique_catalogs': len(by_catalog),
            'views_with_sources': views_with_sources
        },
        'sources_by_schema': {k: sorted(set([t for v, t in v_list])) for k, v_list in by_schema.items()},
        'sources_by_catalog': {k: sorted(set([t for v, t in v_list])) for k, v_list in by_catalog.items()}
    }
    
    with open('INGENIOUS_UPSTREAM_SOURCES.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"✓ JSON export saved to: INGENIOUS_UPSTREAM_SOURCES.json")
    
    # Print summary
    print("\n" + "=" * 80)
    print("Analysis Complete")
    print("=" * 80)
    print(f"\nViews Analyzed: {len(views)}")
    print(f"Views with Identified Sources: {views_with_sources}")
    print(f"Total Unique Upstream Tables: {len(all_sources)}")
    print(f"Unique Source Schemas: {len(by_schema)}")
    if by_schema:
        print("\nSource Schemas:")
        for schema in sorted(by_schema.keys()):
            views_count = len(set([v for v, t in by_schema[schema]]))
            print(f"  {schema}: {views_count} views")

if __name__ == "__main__":
    analyze_all_upstream_sources()







