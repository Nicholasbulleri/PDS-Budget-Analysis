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
Get upstream lineage using the correct Unity Catalog column names
Based on what's visible in Databricks UI
"""

from edp_connection import connect_to_edp
import json

def get_all_curated_tables(conn):
    """Get all table names from curated schema"""
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

def get_lineage_with_correct_columns(conn):
    """Try lineage with correct Unity Catalog column names"""
    print("   Trying Unity Catalog lineage with correct column names...")
    
    # Try setting catalog first
    try:
        cursor = conn.cursor()
        cursor.execute("USE CATALOG work_dynamics")
        cursor.close()
    except:
        pass
    
    # Try the correct Unity Catalog column names
    queries = [
        # Standard Unity Catalog format with _name suffix
        """
        SELECT 
            source_catalog_name,
            source_schema_name,
            source_table_name,
            destination_catalog_name,
            destination_schema_name,
            destination_table_name
        FROM system.access.table_lineage
        WHERE destination_catalog_name = 'work_dynamics'
        AND destination_schema_name = 'curated'
        """,
        # Try without USE CATALOG requirement
        """
        SELECT 
            source_catalog_name,
            source_schema_name,
            source_table_name,
            destination_catalog_name,
            destination_schema_name,
            destination_table_name
        FROM system.access.table_lineage
        WHERE destination_catalog_name = 'work_dynamics'
        AND destination_schema_name = 'curated'
        """,
        # Try with just schema name
        """
        SELECT 
            source_catalog_name,
            source_schema_name,
            source_table_name,
            destination_catalog_name,
            destination_schema_name,
            destination_table_name
        FROM system.access.table_lineage
        WHERE destination_schema_name = 'curated'
        """
    ]
    
    for i, query in enumerate(queries, 1):
        try:
            print(f"   Attempt {i}...")
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            cursor.close()
            
            if results:
                print(f"   ✓ SUCCESS! Found {len(results)} lineage records")
                print(f"   Columns: {', '.join(columns)}")
                return results, columns, True
        except Exception as e:
            error_msg = str(e)
            if 'PERMISSION' not in error_msg and 'INSUFFICIENT' not in error_msg:
                print(f"   Attempt {i} error: {error_msg[:150]}")
            else:
                print(f"   Attempt {i}: Permission issue")
    
    return [], [], False

def get_comprehensive_upstream_lineage():
    """Get comprehensive upstream lineage for all curated tables"""
    print("=" * 80)
    print("Upstream Lineage Analysis - Curated Schema")
    print("=" * 80)
    
    conn = connect_to_edp()
    
    try:
        # Get all tables
        print("\n1. Fetching all tables from catalog...")
        all_tables = get_all_curated_tables(conn)
        print(f"   Found {len(all_tables)} tables")
        
        # Get lineage
        print(f"\n2. Getting upstream lineage from system tables...")
        print("-" * 80)
        
        lineage_results, columns, success = get_lineage_with_correct_columns(conn)
        
        if not success:
            print("   ⚠ Could not access system.access.table_lineage")
            print("   Will try alternative methods...")
            return None
        
        # Process lineage results
        print(f"\n3. Processing lineage data...")
        print("-" * 80)
        
        upstream_map = {}
        downstream_map = {}
        
        for row in lineage_results:
            if hasattr(row, '__getitem__') and len(row) >= 6:
                # Extract source and destination
                source_catalog = row[0] if len(row) > 0 else None
                source_schema = row[1] if len(row) > 1 else None
                source_table = row[2] if len(row) > 2 else None
                dest_catalog = row[3] if len(row) > 3 else None
                dest_schema = row[4] if len(row) > 4 else None
                dest_table = row[5] if len(row) > 5 else None
                
                # Build upstream map (what tables does dest_table depend on)
                if dest_table and dest_schema == 'curated':
                    if dest_table not in upstream_map:
                        upstream_map[dest_table] = []
                    upstream_map[dest_table].append({
                        'catalog': source_catalog,
                        'schema': source_schema,
                        'table': source_table
                    })
                
                # Build downstream map (what tables depend on source_table)
                if source_table and source_schema == 'curated':
                    if source_table not in downstream_map:
                        downstream_map[source_table] = []
                    downstream_map[source_table].append({
                        'catalog': dest_catalog,
                        'schema': dest_schema,
                        'table': dest_table
                    })
        
        print(f"   Processed lineage for {len(upstream_map)} tables with upstream")
        print(f"   Processed lineage for {len(downstream_map)} tables with downstream")
        
        # Build final lineage structure for all tables
        print(f"\n4. Building comprehensive lineage report...")
        print("-" * 80)
        
        all_lineage = {}
        for table_name in all_tables:
            lineage = {
                'table_name': table_name,
                'upstream': upstream_map.get(table_name, []),
                'downstream': downstream_map.get(table_name, []),
                'has_upstream': table_name in upstream_map and len(upstream_map[table_name]) > 0,
                'has_downstream': table_name in downstream_map and len(downstream_map[table_name]) > 0
            }
            all_lineage[table_name] = lineage
        
        # Summary
        tables_with_upstream = sum(1 for l in all_lineage.values() if l.get('has_upstream'))
        tables_with_downstream = sum(1 for l in all_lineage.values() if l.get('has_downstream'))
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total tables: {len(all_tables)}")
        print(f"Tables with upstream lineage: {tables_with_upstream}")
        print(f"Tables with downstream lineage: {tables_with_downstream}")
        print(f"Total lineage records: {len(lineage_results)}")
        
        # Show some examples
        print(f"\n=== Sample Tables with Upstream Lineage ===")
        count = 0
        for table_name, lineage in sorted(all_lineage.items()):
            if lineage.get('has_upstream'):
                print(f"\n{table_name}: {len(lineage['upstream'])} upstream")
                for upstream in lineage['upstream'][:3]:
                    cat = upstream.get('catalog', '')
                    sch = upstream.get('schema', '')
                    tbl = upstream.get('table', '')
                    if cat and sch:
                        print(f"  - {cat}.{sch}.{tbl}")
                    elif sch:
                        print(f"  - {sch}.{tbl}")
                    else:
                        print(f"  - {tbl}")
                count += 1
                if count >= 10:
                    break
        
        # Save results
        output = {
            'total_tables': len(all_tables),
            'tables_with_upstream': tables_with_upstream,
            'tables_with_downstream': tables_with_downstream,
            'total_lineage_records': len(lineage_results),
            'lineage': all_lineage
        }
        
        with open('CURATED_UPSTREAM_LINEAGE_FINAL.json', 'w') as f:
            json.dump(output, f, indent=2)
        print(f"\n✓ Lineage data saved to: CURATED_UPSTREAM_LINEAGE_FINAL.json")
        
        return output
    
    finally:
        conn.close()

if __name__ == "__main__":
    get_comprehensive_upstream_lineage()

