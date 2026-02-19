#!/usr/bin/env python3
"""
Get table names and lineage (upstream/downstream) from Databricks catalog
Uses a single connection to avoid multiple authentication prompts
"""

from edp_connection import connect_to_edp
import json

def get_all_curated_tables(conn):
    """Get all table names from curated schema using existing connection"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM system.information_schema.tables 
            WHERE table_schema = 'curated' 
            AND table_catalog = 'work_dynamics'
            ORDER BY table_name
        """)
        
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        cursor.close()
        
        tables = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) > 0:
                table_name = row[0] if len(row) > 0 else None
                if table_name:
                    tables.append(table_name)
        return sorted(tables)
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

def get_all_lineage_data(conn):
    """Get all lineage data using existing connection - try system table first, then view definitions"""
    print("   Attempting to fetch lineage data...")
    
    upstream_map = {}
    downstream_map = {}
    lineage_from_system = False
    
    # Method 1: Try system.access.table_lineage (now that permissions may be available)
    try:
        print("   Trying system.access.table_lineage...")
        cursor = conn.cursor()
        
        cursor.execute("""
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
        """)
        upstream_results = cursor.fetchall()
        cursor.close()
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                source_catalog,
                source_schema,
                source_table,
                target_catalog,
                target_schema,
                target_table
            FROM system.access.table_lineage
            WHERE source_catalog = 'work_dynamics'
            AND source_schema = 'curated'
        """)
        downstream_results = cursor.fetchall()
        cursor.close()
        
        # Process upstream results
        for row in upstream_results:
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
        
        # Process downstream results
        for row in downstream_results:
            if hasattr(row, '__getitem__') and len(row) >= 6:
                source_table = row[2] if len(row) > 2 else None
                if source_table:
                    if source_table not in downstream_map:
                        downstream_map[source_table] = []
                    downstream_map[source_table].append({
                        'catalog': row[3] if len(row) > 3 else None,
                        'schema': row[4] if len(row) > 4 else None,
                        'table': row[5] if len(row) > 5 else None,
                        'source': 'system_lineage'
                    })
        
        lineage_from_system = True
        print(f"   ✓ Found lineage from system table: {len(upstream_map)} tables with upstream, {len(downstream_map)} with downstream")
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ⚠ system.access.table_lineage not accessible: {error_msg[:100]}")
        print("   Will try view definitions as fallback...")
    
    # Method 2: Also get lineage from view definitions (complementary)
    print("   Extracting lineage from view definitions...")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name, table_type
            FROM system.information_schema.tables 
            WHERE table_schema = 'curated' 
            AND table_catalog = 'work_dynamics'
            AND table_type LIKE '%VIEW%'
        """)
        view_results = cursor.fetchall()
        cursor.close()
        
        views_processed = 0
        for row in view_results:
            if hasattr(row, '__getitem__') and len(row) >= 1:
                view_name = row[0] if len(row) > 0 else None
                if view_name:
                    # Get view definition
                    try:
                        cursor = conn.cursor()
                        cursor.execute(f"SHOW CREATE TABLE work_dynamics.curated.{view_name}")
                        def_results = cursor.fetchall()
                        cursor.close()
                        
                        if def_results and len(def_results) > 0:
                            definition = def_results[0][0] if hasattr(def_results[0], '__getitem__') and len(def_results[0]) > 0 else None
                            if definition:
                                # Extract table references
                                import re
                                # Pattern for fully qualified: catalog.schema.table
                                pattern1 = r'\b(?:work_dynamics|edp_sourcesystem|hive_metastore)\.(?:curated|ingenious|default)\.(\w+)'
                                matches1 = re.findall(pattern1, definition, re.IGNORECASE)
                                # Pattern for schema.table
                                pattern2 = r'\b(?:curated|ingenious|default)\.(\w+)'
                                matches2 = re.findall(pattern2, definition, re.IGNORECASE)
                                
                                all_refs = set(matches1 + matches2)
                                
                                # Add to upstream_map
                                if view_name not in upstream_map:
                                    upstream_map[view_name] = []
                                
                                for ref in all_refs:
                                    # Check if already exists
                                    exists = any(r.get('table') == ref for r in upstream_map[view_name])
                                    if not exists:
                                        upstream_map[view_name].append({
                                            'catalog': 'work_dynamics',
                                            'schema': 'curated',
                                            'table': ref,
                                            'source': 'view_definition'
                                        })
                                
                                views_processed += 1
                    except Exception as e:
                        # Skip if can't get definition
                        pass
        
        if views_processed > 0:
            print(f"   ✓ Extracted lineage from {views_processed} view definitions")
    
    except Exception as e:
        print(f"   ⚠ Could not extract from view definitions: {e}")
    
    return upstream_map, downstream_map, lineage_from_system

def get_all_lineage():
    """Get lineage for all curated tables using a single connection"""
    print("=" * 80)
    print("Table Lineage Analysis - Curated Schema")
    print("=" * 80)
    
    # Create a single connection that will be reused
    print("\n0. Establishing connection (single authentication)...")
    try:
        conn = connect_to_edp()
        print("   ✓ Connection established")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return None
    
    try:
        # Get all tables
        print("\n1. Fetching all table names from catalog...")
        all_tables = get_all_curated_tables(conn)
        print(f"   Found {len(all_tables)} tables")
        
        # Known accessible tables (for reference)
        accessible_tables = [
            'commitment', 'budgetdetail', 'budgetchange', 'budgetforecast',
            'directorycontactprojectlnk', 'companysourcesystemrelationship',
            'customvalue', 'costsave'
        ]
        
        print(f"\n2. Getting lineage information (using same connection)...")
        print("-" * 80)
        
        # Get all lineage in one go using the same connection
        upstream_map, downstream_map, lineage_accessible = get_all_lineage_data(conn)
        
        # Build lineage structure for all tables
        all_lineage = {}
        lineage_accessible_count = 0
        no_lineage_count = 0
        
        for table_name in all_tables:
            lineage = {
                'table_name': table_name,
                'upstream': upstream_map.get(table_name, []),
                'downstream': downstream_map.get(table_name, []),
                'lineage_accessible': lineage_accessible
            }
            all_lineage[table_name] = lineage
            
            if lineage_accessible:
                lineage_accessible_count += 1
                upstream_count = len(lineage['upstream'])
                downstream_count = len(lineage['downstream'])
                if upstream_count > 0 or downstream_count > 0:
                    print(f"   {table_name}: {upstream_count} upstream, {downstream_count} downstream")
            else:
                no_lineage_count += 1
        
        permission_denied_count = 0 if lineage_accessible else len(all_tables)
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total tables: {len(all_tables)}")
        print(f"Lineage accessible: {lineage_accessible_count}")
        print(f"Permission denied: {permission_denied_count}")
        print(f"No lineage data: {no_lineage_count}")
        
        # Count tables with relationships
        tables_with_upstream = sum(1 for l in all_lineage.values() if l.get('upstream'))
        tables_with_downstream = sum(1 for l in all_lineage.values() if l.get('downstream'))
        tables_with_any_lineage = sum(1 for l in all_lineage.values() 
                                      if l.get('upstream') or l.get('downstream'))
        
        print(f"\nLineage Statistics:")
        print(f"  Tables with upstream: {tables_with_upstream}")
        print(f"  Tables with downstream: {tables_with_downstream}")
        print(f"  Tables with any lineage: {tables_with_any_lineage}")
        
        # Save results
        output = {
            'total_tables': len(all_tables),
            'lineage_accessible': lineage_accessible_count,
            'permission_denied': permission_denied_count,
            'no_lineage': no_lineage_count,
            'tables_with_upstream': tables_with_upstream,
            'tables_with_downstream': tables_with_downstream,
            'tables_with_any_lineage': tables_with_any_lineage,
            'lineage': all_lineage
        }
        
        with open('CURATED_TABLE_LINEAGE.json', 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n✓ Lineage data saved to: CURATED_TABLE_LINEAGE.json")
        
        # Create summary report
        create_summary_report(output)
        
        return output
    
    finally:
        # Always close the connection
        print("\n3. Closing connection...")
        conn.close()
        print("   ✓ Connection closed")

def create_summary_report(data):
    """Create a human-readable summary report"""
    report = []
    report.append("# Curated Schema Table Lineage Report\n")
    report.append(f"**Total Tables:** {data['total_tables']}\n")
    report.append(f"**Lineage Accessible:** {data['lineage_accessible']}\n")
    report.append(f"**Tables with Upstream:** {data['tables_with_upstream']}\n")
    report.append(f"**Tables with Downstream:** {data['tables_with_downstream']}\n")
    report.append(f"**Tables with Any Lineage:** {data['tables_with_any_lineage']}\n\n")
    report.append("---\n\n")
    
    # Tables with upstream
    report.append("## Tables with Upstream Dependencies\n\n")
    tables_with_upstream = [(name, lineage) for name, lineage in data['lineage'].items() 
                           if lineage.get('upstream')]
    tables_with_upstream.sort(key=lambda x: len(x[1]['upstream']), reverse=True)
    
    for table_name, lineage in tables_with_upstream[:50]:  # Top 50
        report.append(f"### {table_name}\n")
        report.append(f"**Upstream Tables:** {len(lineage['upstream'])}\n\n")
        for upstream in lineage['upstream'][:10]:  # First 10
            full_name = f"{upstream['catalog']}.{upstream['schema']}.{upstream['table']}"
            report.append(f"- {full_name}\n")
        if len(lineage['upstream']) > 10:
            report.append(f"- ... and {len(lineage['upstream']) - 10} more\n")
        report.append("\n")
    
    # Tables with downstream
    report.append("## Tables with Downstream Dependencies\n\n")
    tables_with_downstream = [(name, lineage) for name, lineage in data['lineage'].items() 
                             if lineage.get('downstream')]
    tables_with_downstream.sort(key=lambda x: len(x[1]['downstream']), reverse=True)
    
    for table_name, lineage in tables_with_downstream[:50]:  # Top 50
        report.append(f"### {table_name}\n")
        report.append(f"**Downstream Tables:** {len(lineage['downstream'])}\n\n")
        for downstream in lineage['downstream'][:10]:  # First 10
            full_name = f"{downstream['catalog']}.{downstream['schema']}.{downstream['table']}"
            report.append(f"- {full_name}\n")
        if len(lineage['downstream']) > 10:
            report.append(f"- ... and {len(lineage['downstream']) - 10} more\n")
        report.append("\n")
    
    # Tables without lineage
    report.append("## Tables without Lineage Data\n\n")
    tables_without_lineage = [name for name, lineage in data['lineage'].items() 
                              if not lineage.get('upstream') and not lineage.get('downstream')]
    report.append(f"**Count:** {len(tables_without_lineage)}\n\n")
    report.append("These tables either have no lineage tracked or lineage is not accessible.\n\n")
    
    with open('CURATED_TABLE_LINEAGE_REPORT.md', 'w') as f:
        f.write(''.join(report))
    print(f"✓ Summary report saved to: CURATED_TABLE_LINEAGE_REPORT.md")

if __name__ == "__main__":
    get_all_lineage()

