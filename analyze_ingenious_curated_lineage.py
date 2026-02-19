#!/usr/bin/env python3
"""
Analyze lineage from source system (edp_sourcesystem.ingenious) to curated schema (work_dynamics.curated)
Focusing on ingenious-related tables in curated schema
"""

from edp_connection import execute_query
import json
import re
from collections import defaultdict

def get_ingenious_curated_tables():
    """Get ingenious-related tables in work_dynamics.curated schema"""
    print("Fetching ingenious-related tables in work_dynamics.curated...")
    
    try:
        # First, get all tables
        cols, results = execute_query("""
            SELECT table_name 
            FROM system.information_schema.tables 
            WHERE table_schema = 'curated' 
            AND table_catalog = 'work_dynamics'
            ORDER BY table_name
        """)
        
        all_tables = []
        for row in results:
            if hasattr(row, '__getitem__'):
                table_name = row[0] if len(row) > 0 else None
                if table_name:
                    all_tables.append(table_name)
        
        # Filter to ingenious-related tables (match the view names we found)
        ingenious_view_names = [
            'answer', 'budgetchange', 'budgetdetail', 'businessunit', 'commitment',
            'commitmentchanges', 'directorycontactprojectlnk', 'generictask', 'inspection',
            'inspectionmembers', 'inspectiontemplates', 'locations', 'milestone', 'program',
            'project', 'projectadditionalcustomfield', 'projectsites', 'projectstatsindicator',
            'punchitemmember', 'punchlistitem', 'risk', 'riskcontact', 'riskmembers',
            'users', 'workitem'
        ]
        
        # Find matching tables (exact match or contains the name)
        ingenious_tables = []
        for table in all_tables:
            table_lower = table.lower()
            for view_name in ingenious_view_names:
                if table_lower == view_name or table_lower.startswith(view_name) or view_name in table_lower:
                    ingenious_tables.append(table)
                    break
        
        print(f"Found {len(ingenious_tables)} ingenious-related tables in curated schema")
        return sorted(list(set(ingenious_tables)))
    except Exception as e:
        print(f"Error fetching curated tables: {e}")
        return []

def get_table_definition(table_name):
    """Get the CREATE TABLE or CREATE VIEW definition"""
    try:
        cols, results = execute_query(f"SHOW CREATE TABLE work_dynamics.curated.{table_name}")
        if results:
            definition = ' '.join([str(row) for row in results])
            return definition
    except Exception as e:
        # Might not have permission or might be a different object type
        pass
    return None

def extract_source_tables_from_sql(sql_text):
    """Extract table references from SQL, focusing on edp_sourcesystem.ingenious"""
    if not sql_text:
        return []
    
    sources = set()
    
    # Pattern 1: FROM edp_sourcesystem.ingenious.table_name
    patterns = [
        r'FROM\s+edp_sourcesystem\.ingenious\.([a-zA-Z0-9_`]+)',
        r'FROM\s+`edp_sourcesystem`\.`ingenious`\.`([a-zA-Z0-9_]+)`',
        r'JOIN\s+edp_sourcesystem\.ingenious\.([a-zA-Z0-9_`]+)',
        r'JOIN\s+`edp_sourcesystem`\.`ingenious`\.`([a-zA-Z0-9_]+)`',
        r'(edp_sourcesystem\.ingenious\.[a-zA-Z0-9_`]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, sql_text, re.IGNORECASE)
        for match in matches:
            clean_match = match.strip('`').strip()
            if clean_match and not clean_match.upper() in ['SELECT', 'FROM', 'WHERE', 'JOIN']:
                sources.add(f"edp_sourcesystem.ingenious.{clean_match}")
    
    return sorted(list(sources))

def analyze_ingenious_curated_lineage():
    """Analyze lineage from source system to curated schema for ingenious tables"""
    print("=" * 80)
    print("Analyzing Lineage: edp_sourcesystem.ingenious -> work_dynamics.curated (Ingenious Tables)")
    print("=" * 80)
    print()
    
    # Get ingenious-related curated tables
    curated_tables = get_ingenious_curated_tables()
    if not curated_tables:
        print("No ingenious-related curated tables found")
        return
    
    print(f"\nAnalyzing {len(curated_tables)} curated tables...\n")
    
    # Analyze each curated table
    lineage_map = {}
    
    for i, table_name in enumerate(curated_tables, 1):
        print(f"[{i}/{len(curated_tables)}] Analyzing: {table_name}")
        
        sources = {
            'curated_table': table_name,
            'upstream_source_tables': [],
            'source_method': []
        }
        
        # Try to get table definition
        table_def = get_table_definition(table_name)
        if table_def:
            sql_sources = extract_source_tables_from_sql(table_def)
            if sql_sources:
                sources['upstream_source_tables'].extend(sql_sources)
                sources['source_method'].append('definition_parsing')
                print(f"  Found {len(sql_sources)} source(s) via definition parsing")
                for src in sql_sources:
                    print(f"    - {src}")
        
        if not sources['upstream_source_tables']:
            print(f"  No upstream sources identified")
        
        lineage_map[table_name] = sources
        print()
    
    # Generate report
    print("=" * 80)
    print("Generating Lineage Report...")
    print("=" * 80)
    
    # Create markdown report
    md_content = "# Source System to Curated Schema Lineage (Ingenious)\n\n"
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
        md_content += "*No source system lineage identified from view definitions*\n\n"
        md_content += "**Note:** This may indicate that:\n"
        md_content += "- Tables are created via ETL processes rather than views\n"
        md_content += "- View definitions are not accessible\n"
        md_content += "- Lineage information is stored in metadata systems\n\n"
    
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
            md_content += "*No upstream source system tables identified from view definition*\n\n"
        
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
    
    return output

if __name__ == "__main__":
    analyze_ingenious_curated_lineage()







