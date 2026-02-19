#!/usr/bin/env python3
"""
Enhance profiling summary with source system counts and country/region data
"""

from edp_connection import execute_query
import json

# Accessible tables from profiling
ACCESSIBLE_TABLES = [
    'commitment',
    'budgetdetail',
    'budgetchange',
    'budgetforecast',
    'directorycontactprojectlnk',
    'companysourcesystemrelationship',
    'customvalue',
    'costsave'
]

def get_table_columns(table_name):
    """Get all columns for a table"""
    try:
        cols, results = execute_query(f"DESCRIBE TABLE work_dynamics.curated.{table_name}")
        columns = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 2:
                col_name = row[0] if len(row) > 0 else None
                if col_name:
                    columns.append(col_name.lower())
        return columns
    except Exception as e:
        print(f"  Error getting columns: {e}")
        return []

def get_source_system_counts(table_name, source_system_col):
    """Get distinct source system counts"""
    try:
        cols, results = execute_query(f"""
            SELECT 
                {source_system_col} as source_system,
                COUNT(*) as row_count
            FROM work_dynamics.curated.{table_name}
            WHERE {source_system_col} IS NOT NULL
            GROUP BY {source_system_col}
            ORDER BY row_count DESC
        """)
        
        systems = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 2:
                system_name = row[0] if len(row) > 0 else None
                count = row[1] if len(row) > 1 else 0
                if system_name:
                    systems.append({
                        'name': system_name,
                        'row_count': count
                    })
        return systems
    except Exception as e:
        print(f"  Error getting source systems: {e}")
        return []

def get_country_region_counts(table_name, country_col, region_col=None):
    """Get distinct country and region counts"""
    result = {
        'countries': [],
        'regions': []
    }
    
    # Get country counts
    if country_col:
        try:
            cols, results = execute_query(f"""
                SELECT 
                    {country_col} as country,
                    COUNT(*) as row_count
                FROM work_dynamics.curated.{table_name}
                WHERE {country_col} IS NOT NULL
                GROUP BY {country_col}
                ORDER BY row_count DESC
                LIMIT 20
            """)
            
            countries = []
            for row in results:
                if hasattr(row, '__getitem__') and len(row) >= 2:
                    country = row[0] if len(row) > 0 else None
                    count = row[1] if len(row) > 1 else 0
                    if country:
                        countries.append({
                            'name': country,
                            'row_count': count
                        })
            result['countries'] = countries
        except Exception as e:
            print(f"  Error getting countries: {e}")
    
    # Get region counts
    if region_col:
        try:
            cols, results = execute_query(f"""
                SELECT 
                    {region_col} as region,
                    COUNT(*) as row_count
                FROM work_dynamics.curated.{table_name}
                WHERE {region_col} IS NOT NULL
                GROUP BY {region_col}
                ORDER BY row_count DESC
                LIMIT 20
            """)
            
            regions = []
            for row in results:
                if hasattr(row, '__getitem__') and len(row) >= 2:
                    region = row[0] if len(row) > 0 else None
                    count = row[1] if len(row) > 1 else 0
                    if region:
                        regions.append({
                            'name': region,
                            'row_count': count
                        })
            result['regions'] = regions
        except Exception as e:
            print(f"  Error getting regions: {e}")
    
    return result

def find_source_system_column(columns):
    """Find the source system column name"""
    possible_names = [
        'sourcesystemname',
        'source_system_name',
        'sourcesystem',
        'source_system',
        'systemname',
        'system_name'
    ]
    
    for col in columns:
        if col in possible_names:
            return col
    
    # Check for partial matches
    for col in columns:
        if 'source' in col and 'system' in col:
            return col
        if 'system' in col and 'name' in col:
            return col
    
    return None

def find_country_column(columns):
    """Find the country column name"""
    possible_names = [
        'country',
        'countrycode',
        'country_code',
        'countryname',
        'country_name',
        'countrytypecode',
        'country_type_code'
    ]
    
    for col in columns:
        if col in possible_names:
            return col
    
    # Check for partial matches
    for col in columns:
        if 'country' in col:
            return col
    
    return None

def find_region_column(columns):
    """Find the region column name"""
    possible_names = [
        'region',
        'regioncode',
        'region_code',
        'regionname',
        'region_name',
        'regiontypecode',
        'region_type_code'
    ]
    
    for col in columns:
        if col in possible_names:
            return col
    
    # Check for partial matches
    for col in columns:
        if 'region' in col:
            return col
    
    return None

def analyze_table(table_name):
    """Analyze a single table for source systems and geography"""
    print(f"\nAnalyzing: {table_name}")
    print("-" * 60)
    
    result = {
        'table_name': table_name,
        'source_systems': [],
        'source_system_count': 0,
        'countries': [],
        'country_count': 0,
        'regions': [],
        'region_count': 0,
        'has_source_system': False,
        'has_country': False,
        'has_region': False
    }
    
    # Get columns
    columns = get_table_columns(table_name)
    print(f"  Columns found: {len(columns)}")
    
    # Find source system column
    source_system_col = find_source_system_column(columns)
    if source_system_col:
        print(f"  Found source system column: {source_system_col}")
        systems = get_source_system_counts(table_name, source_system_col)
        result['source_systems'] = systems
        result['source_system_count'] = len(systems)
        result['has_source_system'] = True
        print(f"  Source systems: {len(systems)}")
        for sys in systems[:5]:  # Show top 5
            print(f"    - {sys['name']}: {sys['row_count']:,} rows")
    else:
        print(f"  No source system column found")
    
    # Find country column
    country_col = find_country_column(columns)
    if country_col:
        print(f"  Found country column: {country_col}")
        geo_data = get_country_region_counts(table_name, country_col)
        result['countries'] = geo_data['countries']
        result['country_count'] = len(geo_data['countries'])
        result['has_country'] = True
        print(f"  Countries: {len(geo_data['countries'])}")
        for country in geo_data['countries'][:5]:  # Show top 5
            print(f"    - {country['name']}: {country['row_count']:,} rows")
    else:
        print(f"  No country column found")
    
    # Find region column
    region_col = find_region_column(columns)
    if region_col:
        print(f"  Found region column: {region_col}")
        geo_data = get_country_region_counts(table_name, country_col, region_col)
        result['regions'] = geo_data['regions']
        result['region_count'] = len(geo_data['regions'])
        result['has_region'] = True
        print(f"  Regions: {len(geo_data['regions'])}")
        for region in geo_data['regions'][:5]:  # Show top 5
            print(f"    - {region['name']}: {region['row_count']:,} rows")
    
    return result

def main():
    print("=" * 80)
    print("Enhanced Profiling: Source Systems & Geography Analysis")
    print("=" * 80)
    
    results = []
    
    for table in ACCESSIBLE_TABLES:
        try:
            result = analyze_table(table)
            results.append(result)
        except Exception as e:
            print(f"Error analyzing {table}: {e}")
            continue
    
    # Generate summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Source system summary
    all_systems = {}
    for result in results:
        if result['has_source_system']:
            for sys in result['source_systems']:
                sys_name = sys['name']
                if sys_name not in all_systems:
                    all_systems[sys_name] = {'tables': [], 'total_rows': 0}
                all_systems[sys_name]['tables'].append(result['table_name'])
                all_systems[sys_name]['total_rows'] += sys['row_count']
    
    print(f"\nSource Systems Found: {len(all_systems)}")
    print("\nSource System Distribution:")
    print("-" * 80)
    for sys_name, data in sorted(all_systems.items(), key=lambda x: x[1]['total_rows'], reverse=True):
        print(f"{sys_name:40} | {data['total_rows']:>12,} rows | {len(data['tables'])} tables")
    
    # Country summary
    all_countries = {}
    for result in results:
        if result['has_country']:
            for country in result['countries']:
                country_name = country['name']
                if country_name not in all_countries:
                    all_countries[country_name] = {'tables': [], 'total_rows': 0}
                all_countries[country_name]['tables'].append(result['table_name'])
                all_countries[country_name]['total_rows'] += country['row_count']
    
    if all_countries:
        print(f"\nCountries Found: {len(all_countries)}")
        print("\nTop Countries by Row Count:")
        print("-" * 80)
        for country_name, data in sorted(all_countries.items(), key=lambda x: x[1]['total_rows'], reverse=True)[:10]:
            print(f"{country_name:40} | {data['total_rows']:>12,} rows | {len(data['tables'])} tables")
    
    # Save results
    output = {
        'tables': results,
        'summary': {
            'total_source_systems': len(all_systems),
            'source_systems': {k: {'total_rows': v['total_rows'], 'tables': v['tables']} 
                             for k, v in all_systems.items()},
            'total_countries': len(all_countries),
            'countries': {k: {'total_rows': v['total_rows'], 'tables': v['tables']} 
                          for k, v in all_countries.items()} if all_countries else {}
        }
    }
    
    with open('CURATED_PROFILING_ENHANCED.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n✓ Enhanced profiling data saved to: CURATED_PROFILING_ENHANCED.json")
    
    return output

if __name__ == "__main__":
    main()




