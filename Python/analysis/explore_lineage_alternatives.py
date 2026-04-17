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
Explore alternative methods to get lineage information
Since it's visible in Databricks UI, there must be another way to query it
"""

from edp_connection import connect_to_edp
import json

def explore_lineage_alternatives():
    """Try different methods to get lineage"""
    print("=" * 80)
    print("Exploring Alternative Lineage Access Methods")
    print("=" * 80)
    
    conn = connect_to_edp()
    
    try:
        # Method 1: Check DESCRIBE EXTENDED for lineage info
        print("\n1. Checking DESCRIBE EXTENDED for lineage...")
        print("-" * 80)
        try:
            cursor = conn.cursor()
            cursor.execute("DESCRIBE EXTENDED work_dynamics.curated.commitment")
            results = cursor.fetchall()
            cursor.close()
            
            print(f"   Found {len(results)} rows in DESCRIBE EXTENDED")
            # Look for lineage-related keys
            lineage_keys = []
            for row in results[:20]:  # First 20 rows
                if hasattr(row, '__getitem__') and len(row) >= 2:
                    key = row[0] if len(row) > 0 else None
                    value = row[1] if len(row) > 1 else None
                    if key and ('lineage' in str(key).lower() or 'source' in str(key).lower() or 'dependency' in str(key).lower()):
                        lineage_keys.append((key, value))
                        print(f"   Found: {key} = {value}")
            
            if not lineage_keys:
                print("   No lineage keys found in DESCRIBE EXTENDED")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 2: Check DESCRIBE DETAIL
        print("\n2. Checking DESCRIBE DETAIL for lineage...")
        print("-" * 80)
        try:
            cursor = conn.cursor()
            cursor.execute("DESCRIBE DETAIL work_dynamics.curated.commitment")
            results = cursor.fetchall()
            cursor.close()
            
            print(f"   Found {len(results)} rows in DESCRIBE DETAIL")
            for row in results:
                if hasattr(row, '__getitem__') and len(row) >= 2:
                    key = row[0] if len(row) > 0 else None
                    value = row[1] if len(row) > 1 else None
                    print(f"   {key} = {value}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 3: Check information_schema for lineage columns
        print("\n3. Checking information_schema for lineage-related columns...")
        print("-" * 80)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT column_name, data_type
                FROM system.information_schema.columns
                WHERE table_schema = 'information_schema'
                AND (column_name LIKE '%lineage%' OR column_name LIKE '%dependency%' OR column_name LIKE '%source%')
                LIMIT 20
            """)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                print(f"   Found {len(results)} lineage-related columns:")
                for row in results:
                    print(f"   - {row[0]} ({row[1]})")
            else:
                print("   No lineage columns found in information_schema")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 4: Try different system schema names
        print("\n4. Checking for alternative system schemas...")
        print("-" * 80)
        system_schemas = ['system', 'information_schema', 'sys', 'catalog']
        for schema in system_schemas:
            try:
                cursor = conn.cursor()
                cursor.execute(f"SHOW TABLES IN {schema}")
                results = cursor.fetchall()
                cursor.close()
                
                # Look for lineage-related tables
                lineage_tables = [r for r in results if 'lineage' in str(r).lower() or 'dependency' in str(r).lower()]
                if lineage_tables:
                    print(f"   Found in {schema}:")
                    for table in lineage_tables[:5]:
                        print(f"     - {table}")
            except Exception as e:
                pass
        
        # Method 5: Try Unity Catalog REST API approach (check if there's a SQL interface)
        print("\n5. Checking for Unity Catalog lineage views...")
        print("-" * 80)
        try:
            # Try different possible table names
            possible_tables = [
                'system.information_schema.table_lineage',
                'system.information_schema.dependencies',
                'information_schema.table_lineage',
                'information_schema.dependencies',
                'sys.lineage',
                'catalog.lineage'
            ]
            
            for table_name in possible_tables:
                try:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    results = cursor.fetchall()
                    cursor.close()
                    print(f"   ✓ Found accessible table: {table_name}")
                    print(f"     Columns: {[desc[0] for desc in cursor.description] if cursor.description else 'N/A'}")
                except Exception as e:
                    if 'not found' not in str(e).lower() and 'does not exist' not in str(e).lower():
                        print(f"   {table_name}: {str(e)[:100]}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 6: Check SHOW TABLE EXTENDED for lineage
        print("\n6. Checking SHOW TABLE EXTENDED...")
        print("-" * 80)
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLE EXTENDED IN work_dynamics.curated LIKE 'commitment'")
            results = cursor.fetchall()
            cursor.close()
            
            print(f"   Found {len(results)} rows")
            for row in results[:10]:
                print(f"   {row}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 7: Try querying the actual Unity Catalog metadata
        print("\n7. Trying Unity Catalog metadata queries...")
        print("-" * 80)
        try:
            # Unity Catalog might expose lineage through different views
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name
                FROM system.information_schema.tables
                WHERE table_schema IN ('system', 'information_schema')
                AND (table_name LIKE '%lineage%' OR table_name LIKE '%dependency%')
            """)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                print(f"   Found {len(results)} lineage-related tables:")
                for row in results:
                    print(f"   - {row[0]}")
            else:
                print("   No lineage tables found")
        except Exception as e:
            print(f"   Error: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    explore_lineage_alternatives()

