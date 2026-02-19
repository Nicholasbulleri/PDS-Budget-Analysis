#!/usr/bin/env python3
"""
Comprehensive upstream lineage analysis for all curated tables
Tries multiple methods to get lineage information
"""

from edp_connection import connect_to_edp
import json
import re

def get_all_curated_tables(conn):
    """Get all table names and types from curated schema"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name, table_type
            FROM system.information_schema.tables 
            WHERE table_schema = 'curated' 
            AND table_catalog = 'work_dynamics'
            ORDER BY table_name
        """)
        
        results = cursor.fetchall()
        cursor.close()
        
        tables = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 2:
                table_name = row[0] if len(row) > 0 else None
                table_type = row[1] if len(row) > 1 else None
                if table_name:
                    tables.append({
                        'name': table_name,
                        'type': table_type or 'BASE TABLE'
                    })
        return tables
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

def try_system_lineage_variations(conn):
    """Try different variations of system lineage table queries"""
    variations = [
        # Standard Unity Catalog format
        """
        SELECT 
            target_catalog_name,
            target_schema_name,
            target_table_name,
            source_catalog_name,
            source_schema_name,
            source_table_name
        FROM system.access.table_lineage
        WHERE target_catalog_name = 'work_dynamics'
        AND target_schema_name = 'curated'
        """,
        # Alternative column names
        """
        SELECT 
            destination_catalog_name,
            destination_schema_name,
            destination_table_name,
            source_catalog_name,
            source_schema_name,
            source_table_name
        FROM system.access.table_lineage
        WHERE destination_catalog_name = 'work_dynamics'
        AND destination_schema_name = 'curated'
        """,
        # Try without schema restriction
        """
        SELECT 
            target_catalog,
            target_schema,
            target_table,
            source_catalog,
            source_schema,
            source_table
        FROM system.access.table_lineage
        WHERE target_catalog = 'work_dynamics'
        AND target_schema = 'curated'
        """
    ]
    
    for i, query in enumerate(variations, 1):
        try:
            print(f"   Trying variation {i}...")
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                print(f"   ✓ Success with variation {i}! Found {len(results)} lineage records")
                return results, True
        except Exception as e:
            error_msg = str(e)
            if 'PERMISSION' not in error_msg and 'INSUFFICIENT' not in error_msg:
                print(f"   Variation {i} error (not permission): {error_msg[:100]}")
            continue
    
    return [], False

def extract_table_references(sql_text):
    """Extract table references from SQL text"""
    if not sql_text:
        return []
    
    references = set()
    
    # Pattern for fully qualified: catalog.schema.table
    pattern1 = r'\b(?:work_dynamics|edp_sourcesystem|hive_metastore)\.(?:curated|ingenious|default|curated_consumption)\.(\w+)'
    matches1 = re.findall(pattern1, sql_text, re.IGNORECASE)
    references.update(matches1)
    
    # Pattern for schema.table
    pattern2 = r'\b(?:curated|ingenious|default|curated_consumption)\.(\w+)'
    matches2 = re.findall(pattern2, sql_text, re.IGNORECASE)
    references.update(matches2)
    
    # Filter out SQL keywords
    sql_keywords = {'select', 'from', 'where', 'join', 'inner', 'left', 'right', 
                   'outer', 'on', 'and', 'or', 'group', 'order', 'by', 'having',
                   'union', 'insert', 'update', 'delete', 'into', 'set', 'values',
                   'as', 'case', 'when', 'then', 'else', 'end', 'if', 'null',
                   'is', 'not', 'in', 'exists', 'like', 'between', 'distinct'}
    
    filtered = [ref for ref in references if ref.lower() not in sql_keywords and len(ref) > 1]
    
    return sorted(list(set(filtered)))

def get_comprehensive_lineage():
    """Get comprehensive upstream lineage for all curated tables"""
    print("=" * 80)
    print("Comprehensive Upstream Lineage Analysis - Curated Schema")
    print("=" * 80)
    
    # Create a single connection
    print("\n0. Establishing connection (single authentication)...")
    try:
        conn = connect_to_edp()
        print("   ✓ Connection established")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return None
    
    try:
        # Get all tables
        print("\n1. Fetching all tables from catalog...")
        all_tables = get_all_curated_tables(conn)
        print(f"   Found {len(all_tables)} tables")
        
        # Try system lineage first
        print(f"\n2. Attempting to get lineage from system tables...")
        print("-" * 80)
        
        system_lineage_results, system_success = try_system_lineage_variations(conn)
        
        # Build upstream map from system lineage
        upstream_map = {}
        if system_success:
            print("   Processing system lineage results...")
            for row in system_lineage_results:
                if hasattr(row, '__getitem__') and len(row) >= 6:
                    target_table = row[2] if len(row) > 2 else None
                    if target_table:
                        if target_table not in upstream_map:
                            upstream_map[target_table] = []
                        upstream_map[target_table].append({
                            'catalog': row[3] if len(row) > 3 else None,
                            'schema': row[4] if len(row) > 4 else None,
                            'table': row[5] if len(row) > 5 else None,
                            'source': 'system_lineage'
                        })
        
        # Also get lineage from view definitions
        print(f"\n3. Extracting lineage from view definitions...")
        print("-" * 80)
        
        views_processed = 0
        for table_info in all_tables:
            table_name = table_info['name']
            table_type = table_info['type']
            
            # Try to get definition for views
            if 'VIEW' in table_type.upper():
                try:
                    cursor = conn.cursor()
                    cursor.execute(f"SHOW CREATE TABLE work_dynamics.curated.{table_name}")
                    def_results = cursor.fetchall()
                    cursor.close()
                    
                    if def_results and len(def_results) > 0:
                        definition = def_results[0][0] if hasattr(def_results[0], '__getitem__') and len(def_results[0]) > 0 else None
                        if definition:
                            references = extract_table_references(definition)
                            
                            if table_name not in upstream_map:
                                upstream_map[table_name] = []
                            
                            for ref in references:
                                # Check if already exists
                                exists = any(r.get('table') == ref for r in upstream_map[table_name])
                                if not exists:
                                    upstream_map[table_name].append({
                                        'catalog': 'work_dynamics',
                                        'schema': 'curated',
                                        'table': ref,
                                        'source': 'view_definition'
                                    })
                            
                            views_processed += 1
                            if views_processed % 10 == 0:
                                print(f"   Processed {views_processed} views...")
                except Exception as e:
                    # Skip if can't get definition
                    pass
        
        if views_processed > 0:
            print(f"   ✓ Extracted lineage from {views_processed} view definitions")
        
        # Build final lineage structure
        print(f"\n4. Building comprehensive lineage report...")
        print("-" * 80)
        
        all_lineage = {}
        for table_info in all_tables:
            table_name = table_info['name']
            lineage = {
                'table_name': table_name,
                'table_type': table_info['type'],
                'upstream': upstream_map.get(table_name, []),
                'has_upstream': table_name in upstream_map and len(upstream_map[table_name]) > 0
            }
            all_lineage[table_name] = lineage
        
        # Summary
        tables_with_upstream = sum(1 for l in all_lineage.values() if l.get('has_upstream'))
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total tables: {len(all_tables)}")
        print(f"Tables with upstream lineage: {tables_with_upstream}")
        print(f"System lineage available: {system_success}")
        print(f"View definitions processed: {views_processed}")
        
        # Count by source
        system_count = sum(1 for l in all_lineage.values() 
                          if any(u.get('source') == 'system_lineage' for u in l.get('upstream', [])))
        view_count = sum(1 for l in all_lineage.values() 
                        if any(u.get('source') == 'view_definition' for u in l.get('upstream', [])))
        
        print(f"\nLineage Sources:")
        print(f"  From system tables: {system_count} tables")
        print(f"  From view definitions: {view_count} tables")
        
        # Save results
        output = {
            'total_tables': len(all_tables),
            'tables_with_upstream': tables_with_upstream,
            'system_lineage_available': system_success,
            'views_processed': views_processed,
            'lineage': all_lineage
        }
        
        with open('CURATED_UPSTREAM_LINEAGE_COMPREHENSIVE.json', 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n✓ Comprehensive lineage data saved to: CURATED_UPSTREAM_LINEAGE_COMPREHENSIVE.json")
        
        # Create readable summary
        create_lineage_summary(output)
        
        return output
    
    finally:
        # Always close the connection
        print("\n5. Closing connection...")
        conn.close()
        print("   ✓ Connection closed")

def create_lineage_summary(data):
    """Create a human-readable summary of upstream lineage"""
    report = []
    report.append("# Curated Schema - Upstream Lineage Report\n\n")
    report.append(f"**Total Tables:** {data['total_tables']}\n")
    report.append(f"**Tables with Upstream:** {data['tables_with_upstream']}\n")
    report.append(f"**System Lineage Available:** {data['system_lineage_available']}\n")
    report.append(f"**Views Processed:** {data['views_processed']}\n\n")
    report.append("---\n\n")
    
    # Tables with upstream
    report.append("## Tables with Upstream Dependencies\n\n")
    
    tables_with_upstream = [(name, lineage) for name, lineage in data['lineage'].items() 
                            if lineage.get('has_upstream')]
    tables_with_upstream.sort(key=lambda x: len(x[1]['upstream']), reverse=True)
    
    for table_name, lineage in tables_with_upstream:
        report.append(f"### {table_name}\n")
        report.append(f"**Type:** {lineage.get('table_type', 'N/A')}\n")
        report.append(f"**Upstream Tables:** {len(lineage['upstream'])}\n\n")
        
        # Group by source
        by_source = {}
        for upstream in lineage['upstream']:
            source = upstream.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(upstream)
        
        for source, upstreams in by_source.items():
            report.append(f"**From {source}:**\n")
            for upstream in upstreams[:20]:  # First 20
                catalog = upstream.get('catalog', '')
                schema = upstream.get('schema', '')
                table = upstream.get('table', '')
                if catalog and schema:
                    full_name = f"{catalog}.{schema}.{table}"
                elif schema:
                    full_name = f"{schema}.{table}"
                else:
                    full_name = table
                report.append(f"- {full_name}\n")
            if len(upstreams) > 20:
                report.append(f"- ... and {len(upstreams) - 20} more\n")
            report.append("\n")
        report.append("\n")
    
    # Tables without upstream
    tables_without = [name for name, lineage in data['lineage'].items() 
                      if not lineage.get('has_upstream')]
    report.append(f"## Tables without Upstream Lineage\n\n")
    report.append(f"**Count:** {len(tables_without)}\n\n")
    report.append("These tables either have no upstream dependencies or lineage is not available.\n\n")
    
    with open('CURATED_UPSTREAM_LINEAGE_REPORT.md', 'w') as f:
        f.write(''.join(report))
    print(f"✓ Summary report saved to: CURATED_UPSTREAM_LINEAGE_REPORT.md")

if __name__ == "__main__":
    get_comprehensive_lineage()

