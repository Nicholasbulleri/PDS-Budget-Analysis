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
Comprehensive data profiling exercise for work_dynamics.curated schema
"""

from edp_connection import execute_query
import json
from collections import defaultdict
import statistics

def get_all_curated_tables():
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
        
        print(f"Found {len(tables)} tables")
        return sorted(tables)
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

def get_table_row_count(table_name):
    """Get row count for a table"""
    try:
        cols, results = execute_query(f"SELECT COUNT(*) FROM work_dynamics.curated.{table_name}")
        if results and len(results) > 0:
            return results[0][0] if hasattr(results[0], '__getitem__') else None
    except Exception as e:
        # Permission denied or table doesn't exist
        return None
    return None

def get_table_schema(table_name):
    """Get table schema/columns"""
    try:
        cols, results = execute_query(f"DESCRIBE TABLE work_dynamics.curated.{table_name}")
        
        columns = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 2:
                col_name = row[0] if len(row) > 0 else None
                col_type = row[1] if len(row) > 1 else None
                col_nullable = row[2] if len(row) > 2 else None
                col_comment = row[3] if len(row) > 3 else None
                
                if col_name and col_type:
                    columns.append({
                        'name': col_name,
                        'type': col_type,
                        'nullable': col_nullable,
                        'comment': col_comment
                    })
        
        return columns
    except Exception as e:
        return []

def profile_column(table_name, column_name, column_type):
    """Profile a single column"""
    profile = {
        'column_name': column_name,
        'data_type': column_type,
        'null_count': None,
        'null_percentage': None,
        'distinct_count': None,
        'sample_values': []
    }
    
    try:
        # Get null count
        cols, results = execute_query(f"""
            SELECT 
                COUNT(*) as total_rows,
                COUNT({column_name}) as non_null_count,
                COUNT(*) - COUNT({column_name}) as null_count
            FROM work_dynamics.curated.{table_name}
        """)
        
        if results and len(results) > 0:
            row = results[0]
            if hasattr(row, '__getitem__') and len(row) >= 3:
                total = row[0] if row[0] else 0
                non_null = row[1] if row[1] else 0
                null_count = row[2] if row[2] else 0
                
                profile['null_count'] = null_count
                if total > 0:
                    profile['null_percentage'] = (null_count / total) * 100
        
        # Get distinct count (for smaller tables or sample)
        try:
            cols, results = execute_query(f"""
                SELECT COUNT(DISTINCT {column_name}) as distinct_count
                FROM work_dynamics.curated.{table_name}
            """)
            if results and len(results) > 0:
                distinct = results[0][0] if hasattr(results[0], '__getitem__') else None
                if distinct is not None:
                    profile['distinct_count'] = distinct
        except:
            pass
        
        # Get sample values (top 5)
        try:
            cols, results = execute_query(f"""
                SELECT {column_name}
                FROM work_dynamics.curated.{table_name}
                WHERE {column_name} IS NOT NULL
                LIMIT 5
            """)
            if results:
                profile['sample_values'] = [str(row[0]) if hasattr(row, '__getitem__') else str(row) 
                                          for row in results[:5]]
        except:
            pass
            
    except Exception as e:
        # Column might not be accessible
        pass
    
    return profile

def profile_table(table_name, sample_columns=True):
    """Profile a single table"""
    print(f"  Profiling: {table_name}")
    
    profile = {
        'table_name': table_name,
        'row_count': None,
        'column_count': 0,
        'columns': [],
        'column_profiles': [],
        'accessible': False
    }
    
    # Get row count
    row_count = get_table_row_count(table_name)
    profile['row_count'] = row_count
    
    if row_count is None:
        print(f"    ⚠ Cannot access table (permission denied or doesn't exist)")
        return profile
    
    profile['accessible'] = True
    
    # Get schema
    columns = get_table_schema(table_name)
    profile['column_count'] = len(columns)
    profile['columns'] = columns
    
    print(f"    Rows: {row_count:,}")
    print(f"    Columns: {len(columns)}")
    
    # Profile columns (sample first 10 for performance)
    if sample_columns and columns:
        columns_to_profile = columns[:10]  # Profile first 10 columns
        print(f"    Profiling {len(columns_to_profile)} columns (sample)...")
        
        for col in columns_to_profile:
            col_profile = profile_column(table_name, col['name'], col['type'])
            profile['column_profiles'].append(col_profile)
    
    return profile

def generate_profiling_report(profiles):
    """Generate comprehensive profiling report"""
    print("\n" + "=" * 80)
    print("Generating Data Profiling Report...")
    print("=" * 80)
    
    # Calculate statistics
    accessible_tables = [p for p in profiles if p['accessible']]
    total_rows = sum(p['row_count'] or 0 for p in accessible_tables)
    total_columns = sum(p['column_count'] for p in accessible_tables)
    
    # Group by row count ranges
    row_count_ranges = {
        '0': 0,
        '1-100': 0,
        '101-1K': 0,
        '1K-10K': 0,
        '10K-100K': 0,
        '100K-1M': 0,
        '1M+': 0
    }
    
    for profile in accessible_tables:
        row_count = profile['row_count'] or 0
        if row_count == 0:
            row_count_ranges['0'] += 1
        elif row_count <= 100:
            row_count_ranges['1-100'] += 1
        elif row_count <= 1000:
            row_count_ranges['101-1K'] += 1
        elif row_count <= 10000:
            row_count_ranges['1K-10K'] += 1
        elif row_count <= 100000:
            row_count_ranges['10K-100K'] += 1
        elif row_count <= 1000000:
            row_count_ranges['100K-1M'] += 1
        else:
            row_count_ranges['1M+'] += 1
    
    # Create markdown report
    md_content = "# Curated Schema Data Profiling Report\n\n"
    md_content += f"**Schema:** `work_dynamics.curated`\n\n"
    md_content += f"**Total Tables:** {len(profiles)}\n\n"
    md_content += f"**Accessible Tables:** {len(accessible_tables)}\n\n"
    md_content += f"**Total Rows:** {total_rows:,}\n\n"
    md_content += f"**Total Columns:** {total_columns:,}\n\n"
    md_content += "---\n\n"
    
    # Summary statistics
    md_content += "## Summary Statistics\n\n"
    md_content += "### Tables by Row Count Range\n\n"
    md_content += "| Range | Count |\n"
    md_content += "|-------|-------|\n"
    for range_name, count in row_count_ranges.items():
        md_content += f"| {range_name} | {count} |\n"
    md_content += "\n"
    
    # Top tables by row count
    md_content += "### Top 20 Tables by Row Count\n\n"
    md_content += "| Table Name | Row Count | Column Count |\n"
    md_content += "|------------|-----------|--------------|\n"
    
    sorted_tables = sorted(accessible_tables, key=lambda x: x['row_count'] or 0, reverse=True)
    for profile in sorted_tables[:20]:
        row_count = profile['row_count'] or 0
        col_count = profile['column_count']
        md_content += f"| {profile['table_name']} | {row_count:,} | {col_count} |\n"
    md_content += "\n"
    
    # Detailed table profiles
    md_content += "---\n\n"
    md_content += "## Detailed Table Profiles\n\n"
    
    for profile in sorted(profiles, key=lambda x: x['table_name']):
        md_content += f"### {profile['table_name']}\n\n"
        
        if profile['accessible']:
            md_content += f"**Row Count:** {profile['row_count']:,}\n\n"
            md_content += f"**Column Count:** {profile['column_count']}\n\n"
            
            if profile['columns']:
                md_content += "**Columns:**\n\n"
                md_content += "| Column Name | Data Type | Nullable |\n"
                md_content += "|-------------|-----------|----------|\n"
                
                for col in profile['columns'][:20]:  # Show first 20 columns
                    col_name = col['name']
                    col_type = col['type']
                    nullable = col.get('nullable', '')
                    md_content += f"| {col_name} | {col_type} | {nullable} |\n"
                
                if len(profile['columns']) > 20:
                    md_content += f"\n*... and {len(profile['columns']) - 20} more columns*\n"
            
            # Column profiles
            if profile['column_profiles']:
                md_content += "\n**Column Statistics (Sample):**\n\n"
                md_content += "| Column | Data Type | Null % | Distinct | Sample Values |\n"
                md_content += "|--------|-----------|--------|----------|---------------|\n"
                
                for col_prof in profile['column_profiles']:
                    col_name = col_prof['column_name']
                    col_type = col_prof['data_type']
                    null_pct = f"{col_prof['null_percentage']:.1f}%" if col_prof['null_percentage'] is not None else 'N/A'
                    distinct = col_prof['distinct_count'] if col_prof['distinct_count'] is not None else 'N/A'
                    samples = ', '.join(col_prof['sample_values'][:3]) if col_prof['sample_values'] else 'N/A'
                    
                    md_content += f"| {col_name} | {col_type} | {null_pct} | {distinct} | {samples} |\n"
        else:
            md_content += "*Table not accessible (permission denied or doesn't exist)*\n"
        
        md_content += "\n---\n\n"
    
    # Save report
    with open('CURATED_SCHEMA_PROFILING_REPORT.md', 'w') as f:
        f.write(md_content)
    print(f"✓ Markdown report saved to: CURATED_SCHEMA_PROFILING_REPORT.md")
    
    # Save JSON export
    output = {
        'schema': 'work_dynamics.curated',
        'total_tables': len(profiles),
        'accessible_tables': len(accessible_tables),
        'total_rows': total_rows,
        'total_columns': total_columns,
        'profiles': profiles,
        'statistics': {
            'row_count_ranges': row_count_ranges,
            'top_tables': [{'table': p['table_name'], 'rows': p['row_count'], 'columns': p['column_count']} 
                          for p in sorted_tables[:50]]
        }
    }
    
    with open('CURATED_SCHEMA_PROFILING_REPORT.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"✓ JSON export saved to: CURATED_SCHEMA_PROFILING_REPORT.json")
    
    return output

def main():
    print("=" * 80)
    print("Curated Schema Data Profiling Exercise")
    print("=" * 80)
    print()
    
    # Get all tables
    tables = get_all_curated_tables()
    
    if not tables:
        print("No tables found in work_dynamics.curated")
        return
    
    print(f"\nAnalyzing {len(tables)} tables...")
    print("Note: This may take some time due to permission checks and data profiling\n")
    
    # Profile tables (sample first 100 for performance)
    profiles = []
    tables_to_profile = tables[:100] if len(tables) > 100 else tables
    
    print(f"Profiling {len(tables_to_profile)} tables (sampling first 100)...")
    print("-" * 80)
    
    for i, table in enumerate(tables_to_profile, 1):
        print(f"\n[{i}/{len(tables_to_profile)}] {table}")
        profile = profile_table(table, sample_columns=(i <= 50))  # Profile columns for first 50
        profiles.append(profile)
    
    # Generate report
    report = generate_profiling_report(profiles)
    
    # Print summary
    print("\n" + "=" * 80)
    print("Profiling Complete")
    print("=" * 80)
    print(f"\nTables Analyzed: {len(profiles)}")
    print(f"Accessible Tables: {len([p for p in profiles if p['accessible']])}")
    print(f"Total Rows: {sum(p['row_count'] or 0 for p in profiles):,}")
    print(f"Total Columns: {sum(p['column_count'] for p in profiles):,}")
    print(f"\nReport files created:")
    print(f"  - CURATED_SCHEMA_PROFILING_REPORT.md")
    print(f"  - CURATED_SCHEMA_PROFILING_REPORT.json")

if __name__ == "__main__":
    main()





