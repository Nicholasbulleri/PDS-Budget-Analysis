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
Get lineage by parsing view definitions (alternative to system.access.table_lineage)
Uses a single connection to avoid multiple authentication prompts
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
                        'type': table_type
                    })
        return tables
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

def get_view_definition(conn, table_name):
    """Get view definition using SHOW CREATE TABLE"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SHOW CREATE TABLE work_dynamics.curated.{table_name}")
        results = cursor.fetchall()
        cursor.close()
        
        if results and len(results) > 0:
            # The CREATE statement is usually in the first column of the first row
            create_stmt = results[0][0] if hasattr(results[0], '__getitem__') and len(results[0]) > 0 else None
            return create_stmt
        return None
    except Exception as e:
        # Not a view, or permission denied, or doesn't exist
        return None

def extract_table_references(sql_text):
    """Extract table references from SQL text"""
    if not sql_text:
        return []
    
    # Pattern to match table references like:
    # - work_dynamics.curated.table_name
    # - curated.table_name
    # - table_name (if in same schema)
    # - FROM table_name
    # - JOIN table_name
    # - INSERT INTO table_name
    # - UPDATE table_name
    
    references = set()
    
    # Pattern for fully qualified names: catalog.schema.table
    pattern1 = r'\b(?:work_dynamics|edp_sourcesystem|hive_metastore)\.(?:curated|ingenious|default)\.(\w+)'
    matches = re.findall(pattern1, sql_text, re.IGNORECASE)
    references.update(matches)
    
    # Pattern for schema.table
    pattern2 = r'\b(?:curated|ingenious|default)\.(\w+)'
    matches = re.findall(pattern2, sql_text, re.IGNORECASE)
    references.update(matches)
    
    # Pattern for FROM/JOIN clauses (simple table names)
    # This is less reliable but can catch some references
    pattern3 = r'\b(?:FROM|JOIN|INTO|UPDATE)\s+(\w+)'
    matches = re.findall(pattern3, sql_text, re.IGNORECASE)
    references.update(matches)
    
    # Filter out common SQL keywords
    sql_keywords = {'select', 'from', 'where', 'join', 'inner', 'left', 'right', 
                   'outer', 'on', 'and', 'or', 'group', 'order', 'by', 'having',
                   'union', 'insert', 'update', 'delete', 'into', 'set', 'values',
                   'as', 'case', 'when', 'then', 'else', 'end', 'if', 'null',
                   'is', 'not', 'in', 'exists', 'like', 'between', 'distinct'}
    
    filtered = [ref for ref in references if ref.lower() not in sql_keywords and len(ref) > 1]
    
    return sorted(list(set(filtered)))

def get_lineage_from_views():
    """Get lineage by parsing view definitions"""
    print("=" * 80)
    print("Table Lineage Analysis - Using View Definitions")
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
        
        # Separate views from tables
        views = [t for t in all_tables if t['type'] and 'VIEW' in t['type'].upper()]
        tables = [t for t in all_tables if not t['type'] or 'VIEW' not in t['type'].upper()]
        
        print(f"   Views: {len(views)}")
        print(f"   Tables: {len(tables)}")
        
        # Get lineage from views
        print(f"\n2. Extracting lineage from view definitions...")
        print("-" * 80)
        
        all_lineage = {}
        views_processed = 0
        views_with_lineage = 0
        
        for table_info in all_tables:
            table_name = table_info['name']
            lineage = {
                'table_name': table_name,
                'table_type': table_info['type'],
                'upstream': [],
                'downstream': [],
                'has_definition': False
            }
            
            # Try to get view definition
            definition = get_view_definition(conn, table_name)
            if definition:
                lineage['has_definition'] = True
                views_processed += 1
                
                # Extract table references
                references = extract_table_references(definition)
                lineage['upstream'] = [{'table': ref} for ref in references]
                
                if references:
                    views_with_lineage += 1
                    print(f"   {table_name}: {len(references)} upstream references")
            
            all_lineage[table_name] = lineage
        
        # Build downstream relationships (reverse lookup)
        print(f"\n3. Building downstream relationships...")
        for table_name, lineage in all_lineage.items():
            if lineage['upstream']:
                # For each upstream table, add this table to its downstream
                for upstream_ref in lineage['upstream']:
                    upstream_table = upstream_ref['table']
                    if upstream_table in all_lineage:
                        if 'downstream' not in all_lineage[upstream_table]:
                            all_lineage[upstream_table]['downstream'] = []
                        all_lineage[upstream_table]['downstream'].append({
                            'table': table_name
                        })
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total tables: {len(all_tables)}")
        print(f"Views processed: {views_processed}")
        print(f"Views with lineage: {views_with_lineage}")
        
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
            'views_processed': views_processed,
            'views_with_lineage': views_with_lineage,
            'tables_with_upstream': tables_with_upstream,
            'tables_with_downstream': tables_with_downstream,
            'tables_with_any_lineage': tables_with_any_lineage,
            'lineage': all_lineage
        }
        
        with open('CURATED_TABLE_LINEAGE_FROM_VIEWS.json', 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n✓ Lineage data saved to: CURATED_TABLE_LINEAGE_FROM_VIEWS.json")
        
        return output
    
    finally:
        # Always close the connection
        print("\n4. Closing connection...")
        conn.close()
        print("   ✓ Connection closed")

if __name__ == "__main__":
    get_lineage_from_views()

