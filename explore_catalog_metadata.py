#!/usr/bin/env python3
"""
Explore Databricks catalog metadata for inaccessible tables
"""

from edp_connection import execute_query
import json

def get_all_tables_from_catalog():
    """Get all tables from information_schema"""
    try:
        # First try to get basic table info
        cols, results = execute_query("""
            SELECT 
                table_catalog,
                table_schema,
                table_name,
                table_type
            FROM system.information_schema.tables
            WHERE table_schema = 'curated'
            ORDER BY table_name
        """)
        
        tables = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 3:
                tables.append({
                    'catalog': row[0] if len(row) > 0 else None,
                    'schema': row[1] if len(row) > 1 else None,
                    'table_name': row[2] if len(row) > 2 else None,
                    'table_type': row[3] if len(row) > 3 else None
                })
        return tables
    except Exception as e:
        print(f"Error querying information_schema: {e}")
        return []

def get_table_columns_from_catalog(table_name):
    """Get column information from information_schema"""
    try:
        cols, results = execute_query(f"""
            SELECT 
                column_name,
                ordinal_position,
                data_type,
                is_nullable,
                column_default,
                comment
            FROM system.information_schema.columns
            WHERE table_schema = 'curated'
            AND table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        
        columns = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 3:
                columns.append({
                    'name': row[0] if len(row) > 0 else None,
                    'position': row[1] if len(row) > 1 else None,
                    'data_type': row[2] if len(row) > 2 else None,
                    'nullable': row[3] if len(row) > 3 else None,
                    'default': row[4] if len(row) > 4 else None,
                    'comment': row[5] if len(row) > 5 else None
                })
        return columns
    except Exception as e:
        print(f"  Error getting columns: {e}")
        return []

def try_describe_table(table_name):
    """Try to describe table - sometimes works even without SELECT"""
    try:
        cols, results = execute_query(f"DESCRIBE TABLE EXTENDED work_dynamics.curated.{table_name}")
        return True, results
    except Exception as e:
        return False, str(e)

def get_table_statistics(table_name):
    """Try to get table statistics from DESCRIBE DETAIL"""
    try:
        cols, results = execute_query(f"DESCRIBE DETAIL work_dynamics.curated.{table_name}")
        stats = {}
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 2:
                key = row[0] if len(row) > 0 else None
                value = row[1] if len(row) > 1 else None
                if key:
                    stats[key.lower()] = value
        return stats
    except Exception as e:
        return None

def analyze_catalog_access():
    """Analyze what catalog metadata is accessible"""
    print("=" * 80)
    print("Databricks Catalog Metadata Access Analysis")
    print("=" * 80)
    
    # Get all tables from catalog
    print("\n1. Fetching table list from system.information_schema.tables...")
    all_tables = get_all_tables_from_catalog()
    print(f"   Found {len(all_tables)} tables in catalog")
    
    # Known accessible tables
    accessible_tables = [
        'commitment', 'budgetdetail', 'budgetchange', 'budgetforecast',
        'directorycontactprojectlnk', 'companysourcesystemrelationship',
        'customvalue', 'costsave'
    ]
    
    # Sample some inaccessible tables
    inaccessible_tables = [t for t in all_tables if t['table_name'] not in accessible_tables][:20]
    
    print(f"\n2. Testing catalog metadata access for {len(inaccessible_tables)} inaccessible tables...")
    print("-" * 80)
    
    results = {
        'total_tables_in_catalog': len(all_tables),
        'accessible_tables': len(accessible_tables),
        'inaccessible_tables': len(all_tables) - len(accessible_tables),
        'catalog_metadata_tests': []
    }
    
    for table_info in inaccessible_tables[:10]:  # Test first 10
        table_name = table_info['table_name']
        print(f"\nTesting: {table_name}")
        
        test_result = {
            'table_name': table_name,
            'catalog_info': table_info,
            'columns_from_catalog': [],
            'describe_table_works': False,
            'describe_detail_works': False,
            'statistics': None
        }
        
        # Try to get columns from catalog
        columns = get_table_columns_from_catalog(table_name)
        test_result['columns_from_catalog'] = columns
        print(f"  Columns from catalog: {len(columns)}")
        
        # Try DESCRIBE TABLE
        works, result = try_describe_table(table_name)
        test_result['describe_table_works'] = works
        if works:
            print(f"  DESCRIBE TABLE: ✓ Works")
        else:
            print(f"  DESCRIBE TABLE: ✗ Failed ({result[:100]})")
        
        # Try DESCRIBE DETAIL
        stats = get_table_statistics(table_name)
        if stats:
            test_result['describe_detail_works'] = True
            test_result['statistics'] = stats
            print(f"  DESCRIBE DETAIL: ✓ Works")
            if 'numrows' in stats:
                print(f"    Rows: {stats.get('numrows', 'N/A')}")
        else:
            print(f"  DESCRIBE DETAIL: ✗ Failed")
        
        results['catalog_metadata_tests'].append(test_result)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total tables in catalog: {results['total_tables_in_catalog']}")
    print(f"Accessible tables: {results['accessible_tables']}")
    print(f"Inaccessible tables: {results['inaccessible_tables']}")
    
    # Count what works
    columns_accessible = sum(1 for t in results['catalog_metadata_tests'] if t['columns_from_catalog'])
    describe_works = sum(1 for t in results['catalog_metadata_tests'] if t['describe_table_works'])
    detail_works = sum(1 for t in results['catalog_metadata_tests'] if t['describe_detail_works'])
    
    print(f"\nCatalog Metadata Access:")
    print(f"  Columns from information_schema: {columns_accessible}/{len(results['catalog_metadata_tests'])}")
    print(f"  DESCRIBE TABLE works: {describe_works}/{len(results['catalog_metadata_tests'])}")
    print(f"  DESCRIBE DETAIL works: {detail_works}/{len(results['catalog_metadata_tests'])}")
    
    # Get full column list for all inaccessible tables
    print(f"\n3. Getting column metadata for all inaccessible tables...")
    all_inaccessible = [t['table_name'] for t in all_tables if t['table_name'] not in accessible_tables]
    
    catalog_metadata = {}
    for i, table_name in enumerate(all_inaccessible):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(all_inaccessible)}")
        columns = get_table_columns_from_catalog(table_name)
        if columns:
            catalog_metadata[table_name] = {
                'column_count': len(columns),
                'columns': [{'name': c['name'], 'data_type': c['data_type'], 'nullable': c['nullable']} 
                           for c in columns[:20]]  # First 20 columns
            }
    
    results['full_catalog_metadata'] = catalog_metadata
    results['tables_with_catalog_metadata'] = len(catalog_metadata)
    
    print(f"\n✓ Retrieved catalog metadata for {len(catalog_metadata)} tables")
    
    # Save results
    with open('CATALOG_METADATA_ACCESS.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Results saved to: CATALOG_METADATA_ACCESS.json")
    
    return results

if __name__ == "__main__":
    analyze_catalog_access()

