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
Comprehensive data profiling and analysis of budgetdetail table
Analyzing sources, types, relationships to projects, and patterns
"""

from edp_connection import connect_to_edp
import json
from collections import defaultdict, Counter

def get_table_schema(conn, table_name, schema='curated'):
    """Get schema information for a table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                comment
            FROM system.information_schema.columns
            WHERE table_schema = '{schema}'
            AND table_catalog = 'work_dynamics'
            AND table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        results = cursor.fetchall()
        cursor.close()
        
        columns = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 3:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2],
                    'comment': row[3] if len(row) > 3 else None
                })
        return columns
    except Exception as e:
        print(f"Error getting schema for {table_name}: {e}")
        return []

def get_row_count(conn, table_name, schema='curated'):
    """Get row count for a table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM work_dynamics.{schema}.{table_name}")
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result and hasattr(result, '__getitem__') else 0
    except Exception as e:
        print(f"Error getting row count for {table_name}: {e}")
        return 0

def analyze_column_distinct_values(conn, table_name, column_name, schema='curated', limit=100):
    """Get distinct values and counts for a column"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT {column_name}, COUNT(*) as cnt
            FROM work_dynamics.{schema}.{table_name}
            WHERE {column_name} IS NOT NULL
            GROUP BY {column_name}
            ORDER BY cnt DESC
            LIMIT {limit}
        """)
        results = cursor.fetchall()
        cursor.close()
        
        values = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 2:
                values.append({
                    'value': row[0],
                    'count': row[1]
                })
        return values
    except Exception as e:
        print(f"Error analyzing column {column_name}: {e}")
        return []

def analyze_budgetdetail_sources(conn):
    """Analyze source systems in budgetdetail"""
    print("\n" + "=" * 80)
    print("SOURCE SYSTEM ANALYSIS")
    print("=" * 80)
    
    # Check for source system columns
    source_columns = ['sourcesystem', 'source_system', 'system', 'systemname', 'sourcesystemname']
    source_data = {}
    
    for col in source_columns:
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT {col}, COUNT(*) as cnt
                FROM work_dynamics.curated.budgetdetail
                WHERE {col} IS NOT NULL
                GROUP BY {col}
                ORDER BY cnt DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                source_data[col] = []
                for row in results:
                    if hasattr(row, '__getitem__') and len(row) >= 2:
                        source_data[col].append({
                            'source': row[0],
                            'count': row[1]
                        })
                print(f"\nFound source data in column: {col}")
                for item in source_data[col]:
                    print(f"  {item['source']}: {item['count']:,} records")
        except:
            pass
    
    return source_data

def analyze_budget_types(conn):
    """Analyze budget types"""
    print("\n" + "=" * 80)
    print("BUDGET TYPE ANALYSIS")
    print("=" * 80)
    
    type_columns = ['budgettype', 'type', 'budget_type', 'typecode', 'budgettypecode']
    type_data = {}
    
    for col in type_columns:
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT {col}, COUNT(*) as cnt
                FROM work_dynamics.curated.budgetdetail
                WHERE {col} IS NOT NULL
                GROUP BY {col}
                ORDER BY cnt DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                type_data[col] = []
                for row in results:
                    if hasattr(row, '__getitem__') and len(row) >= 2:
                        type_data[col].append({
                            'type': row[0],
                            'count': row[1]
                        })
                print(f"\nFound type data in column: {col}")
                for item in type_data[col]:
                    print(f"  {item['type']}: {item['count']:,} records")
        except:
            pass
    
    return type_data

def analyze_approval_status(conn):
    """Analyze approval status"""
    print("\n" + "=" * 80)
    print("APPROVAL STATUS ANALYSIS")
    print("=" * 80)
    
    approval_columns = ['approved', 'isapproved', 'approvalstatus', 'status', 'approval_status', 'is_approved']
    approval_data = {}
    
    for col in approval_columns:
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT {col}, COUNT(*) as cnt
                FROM work_dynamics.curated.budgetdetail
                GROUP BY {col}
                ORDER BY cnt DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            
            if results:
                approval_data[col] = []
                total = 0
                for row in results:
                    if hasattr(row, '__getitem__') and len(row) >= 2:
                        count = row[1]
                        total += count
                        approval_data[col].append({
                            'status': row[0],
                            'count': count
                        })
                
                print(f"\nFound approval data in column: {col}")
                for item in approval_data[col]:
                    pct = (item['count'] / total * 100) if total > 0 else 0
                    print(f"  {item['status']}: {item['count']:,} records ({pct:.1f}%)")
        except:
            pass
    
    return approval_data

def analyze_project_relationships(conn):
    """Analyze relationship between budgetdetail and projects"""
    print("\n" + "=" * 80)
    print("PROJECT RELATIONSHIP ANALYSIS")
    print("=" * 80)
    
    # First, find the project identifier column in budgetdetail
    project_cols = ['projectidentifier', 'projectid', 'project_id', 'project', 'projectidentifierid']
    project_col = None
    
    for col in project_cols:
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM system.information_schema.columns
                WHERE table_schema = 'curated'
                AND table_catalog = 'work_dynamics'
                AND table_name = 'budgetdetail'
                AND column_name = '{col}'
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0] > 0:
                project_col = col
                print(f"Found project identifier column: {col}")
                break
        except:
            pass
    
    if not project_col:
        print("Could not find project identifier column")
        return None
    
    # Get total projects with budgets
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT COUNT(DISTINCT {project_col}) as project_count
            FROM work_dynamics.curated.budgetdetail
            WHERE {project_col} IS NOT NULL
        """)
        result = cursor.fetchone()
        projects_with_budget = result[0] if result and hasattr(result, '__getitem__') else 0
        cursor.close()
        print(f"\nProjects with budget data: {projects_with_budget:,}")
    except Exception as e:
        print(f"Error counting projects: {e}")
        projects_with_budget = 0
    
    # Get total projects (try different project table names)
    project_tables = ['project', 'projects', 'vw_ingenious_project']
    total_projects = 0
    
    for table_name in project_tables:
        try:
            # Try curated first
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM work_dynamics.curated.{table_name}")
            result = cursor.fetchone()
            total_projects = result[0] if result and hasattr(result, '__getitem__') else 0
            cursor.close()
            if total_projects > 0:
                print(f"Total projects in {table_name}: {total_projects:,}")
                break
        except:
            try:
                # Try curated_consumption
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM work_dynamics.curated_consumption.{table_name}")
                result = cursor.fetchone()
                total_projects = result[0] if result and hasattr(result, '__getitem__') else 0
                cursor.close()
                if total_projects > 0:
                    print(f"Total projects in curated_consumption.{table_name}: {total_projects:,}")
                    break
            except:
                pass
    
    if total_projects > 0:
        coverage = (projects_with_budget / total_projects * 100) if total_projects > 0 else 0
        print(f"\nBudget coverage: {coverage:.1f}% of projects have budget data")
        print(f"Projects without budget: {total_projects - projects_with_budget:,}")
    
    # Analyze budgets per project
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                {project_col},
                COUNT(*) as budget_count
            FROM work_dynamics.curated.budgetdetail
            WHERE {project_col} IS NOT NULL
            GROUP BY {project_col}
            ORDER BY budget_count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        budget_counts = [row[1] for row in results if hasattr(row, '__getitem__') and len(row) >= 2]
        
        if budget_counts:
            import statistics
            print(f"\nBudgets per project statistics:")
            print(f"  Total projects with budgets: {len(budget_counts):,}")
            print(f"  Average budgets per project: {statistics.mean(budget_counts):.2f}")
            print(f"  Median budgets per project: {statistics.median(budget_counts):.2f}")
            print(f"  Min budgets per project: {min(budget_counts)}")
            print(f"  Max budgets per project: {max(budget_counts)}")
            
            # Distribution
            print(f"\nDistribution of budgets per project:")
            ranges = [(1, 1), (2, 5), (6, 10), (11, 20), (21, 50), (51, 100), (101, float('inf'))]
            for start, end in ranges:
                if end == float('inf'):
                    count = sum(1 for c in budget_counts if c >= start)
                    print(f"  {start}+ budgets: {count:,} projects")
                else:
                    count = sum(1 for c in budget_counts if start <= c <= end)
                    print(f"  {start}-{end} budgets: {count:,} projects")
    except Exception as e:
        print(f"Error analyzing budgets per project: {e}")
    
    return {
        'project_column': project_col,
        'projects_with_budget': projects_with_budget,
        'total_projects': total_projects
    }

def analyze_source_system_comparison(conn, project_col):
    """Compare budget data by source system"""
    print("\n" + "=" * 80)
    print("SOURCE SYSTEM COMPARISON (Clarizen vs Ingenious)")
    print("=" * 80)
    
    # Try to find source system column
    source_col = None
    source_columns = ['sourcesystem', 'source_system', 'system', 'systemname', 'sourcesystemname']
    
    for col in source_columns:
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM system.information_schema.columns
                WHERE table_schema = 'curated'
                AND table_catalog = 'work_dynamics'
                AND table_name = 'budgetdetail'
                AND column_name = '{col}'
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0] > 0:
                source_col = col
                break
        except:
            pass
    
    if not source_col:
        print("Could not find source system column")
        return None
    
    # Compare by source system
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                {source_col} as source_system,
                COUNT(*) as budget_count,
                COUNT(DISTINCT {project_col}) as project_count,
                AVG(CAST(amount AS DOUBLE)) as avg_amount,
                SUM(CAST(amount AS DOUBLE)) as total_amount
            FROM work_dynamics.curated.budgetdetail
            WHERE {source_col} IS NOT NULL
            AND {project_col} IS NOT NULL
            GROUP BY {source_col}
            ORDER BY budget_count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        print(f"\nBudget data by source system:")
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 5:
                source = row[0]
                budget_count = row[1]
                project_count = row[2]
                avg_amount = row[3] if row[3] else 0
                total_amount = row[4] if row[4] else 0
                
                print(f"\n  {source}:")
                print(f"    Budget records: {budget_count:,}")
                print(f"    Projects: {project_count:,}")
                print(f"    Avg budget per record: ${avg_amount:,.2f}")
                print(f"    Total budget amount: ${total_amount:,.2f}")
                if project_count > 0:
                    print(f"    Avg budgets per project: {budget_count / project_count:.2f}")
        
        return results
    except Exception as e:
        print(f"Error comparing source systems: {e}")
        # Try without amount column
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT 
                    {source_col} as source_system,
                    COUNT(*) as budget_count,
                    COUNT(DISTINCT {project_col}) as project_count
                FROM work_dynamics.curated.budgetdetail
                WHERE {source_col} IS NOT NULL
                AND {project_col} IS NOT NULL
                GROUP BY {source_col}
                ORDER BY budget_count DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            
            print(f"\nBudget data by source system (without amounts):")
            for row in results:
                if hasattr(row, '__getitem__') and len(row) >= 3:
                    source = row[0]
                    budget_count = row[1]
                    project_count = row[2]
                    
                    print(f"\n  {source}:")
                    print(f"    Budget records: {budget_count:,}")
                    print(f"    Projects: {project_count:,}")
                    if project_count > 0:
                        print(f"    Avg budgets per project: {budget_count / project_count:.2f}")
            
            return results
        except Exception as e2:
            print(f"Error in fallback query: {e2}")
            return None

def analyze_budget_amounts(conn):
    """Analyze budget amounts"""
    print("\n" + "=" * 80)
    print("BUDGET AMOUNT ANALYSIS")
    print("=" * 80)
    
    amount_columns = ['amount', 'budgetamount', 'totalamount', 'value', 'budget_value']
    
    for col in amount_columns:
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT({col}) as non_null_records,
                    MIN(CAST({col} AS DOUBLE)) as min_amount,
                    MAX(CAST({col} AS DOUBLE)) as max_amount,
                    AVG(CAST({col} AS DOUBLE)) as avg_amount,
                    SUM(CAST({col} AS DOUBLE)) as total_amount,
                    PERCENTILE(CAST({col} AS DOUBLE), 0.5) as median_amount,
                    PERCENTILE(CAST({col} AS DOUBLE), 0.25) as p25_amount,
                    PERCENTILE(CAST({col} AS DOUBLE), 0.75) as p75_amount
                FROM work_dynamics.curated.budgetdetail
                WHERE {col} IS NOT NULL
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result and hasattr(result, '__getitem__') and len(result) >= 9:
                if result[1] and result[1] > 0:  # non_null_records > 0
                    print(f"\nFound amount data in column: {col}")
                    print(f"  Total records: {result[0]:,}")
                    print(f"  Records with amount: {result[1]:,}")
                    print(f"  Min amount: ${result[2]:,.2f}")
                    print(f"  Max amount: ${result[3]:,.2f}")
                    print(f"  Average amount: ${result[4]:,.2f}")
                    print(f"  Total amount: ${result[5]:,.2f}")
                    print(f"  Median amount: ${result[6]:,.2f}")
                    print(f"  25th percentile: ${result[7]:,.2f}")
                    print(f"  75th percentile: ${result[8]:,.2f}")
                    return col
        except Exception as e:
            pass
    
    print("Could not find amount column")
    return None

def find_interesting_patterns(conn):
    """Look for interesting patterns in the data"""
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS")
    print("=" * 80)
    
    # Get all columns first
    schema = get_table_schema(conn, 'budgetdetail')
    column_names = [col['name'] for col in schema]
    
    print(f"\nAnalyzing {len(column_names)} columns for patterns...")
    
    patterns = {}
    
    # Check for date columns and analyze them
    date_columns = [col for col in column_names if 'date' in col.lower() or 'time' in col.lower()]
    if date_columns:
        print(f"\nDate columns found: {date_columns}")
        for col in date_columns[:3]:  # Limit to first 3
            try:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT 
                        MIN(CAST({col} AS DATE)) as min_date,
                        MAX(CAST({col} AS DATE)) as max_date,
                        COUNT(DISTINCT CAST({col} AS DATE)) as distinct_dates
                    FROM work_dynamics.curated.budgetdetail
                    WHERE {col} IS NOT NULL
                """)
                result = cursor.fetchone()
                cursor.close()
                
                if result and hasattr(result, '__getitem__'):
                    print(f"  {col}:")
                    print(f"    Date range: {result[0]} to {result[1]}")
                    print(f"    Distinct dates: {result[2]:,}")
            except:
                pass
    
    # Check for status columns
    status_columns = [col for col in column_names if 'status' in col.lower()]
    if status_columns:
        print(f"\nStatus columns found: {status_columns}")
        for col in status_columns[:3]:
            values = analyze_column_distinct_values(conn, 'budgetdetail', col, limit=10)
            if values:
                print(f"  {col}:")
                for item in values[:5]:
                    print(f"    {item['value']}: {item['count']:,}")
    
    # Check for null patterns
    print(f"\nNull value analysis (top columns with nulls):")
    null_counts = []
    for col in column_names[:20]:  # Check first 20 columns
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total,
                    COUNT({col}) as non_null,
                    COUNT(*) - COUNT({col}) as null_count
                FROM work_dynamics.curated.budgetdetail
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result and hasattr(result, '__getitem__') and len(result) >= 3:
                total = result[0]
                null_count = result[2]
                if null_count > 0:
                    null_pct = (null_count / total * 100) if total > 0 else 0
                    null_counts.append((col, null_count, null_pct))
        except:
            pass
    
    null_counts.sort(key=lambda x: x[1], reverse=True)
    for col, null_count, null_pct in null_counts[:10]:
        print(f"  {col}: {null_count:,} nulls ({null_pct:.1f}%)")
    
    return patterns

def comprehensive_budgetdetail_analysis():
    """Perform comprehensive analysis of budgetdetail table"""
    print("=" * 80)
    print("COMPREHENSIVE BUDGETDETAIL DATA PROFILING & ANALYSIS")
    print("=" * 80)
    
    conn = connect_to_edp()
    
    try:
        # 1. Get table schema
        print("\n1. TABLE SCHEMA")
        print("-" * 80)
        schema = get_table_schema(conn, 'budgetdetail')
        print(f"Total columns: {len(schema)}")
        for col in schema:
            print(f"  {col['name']:30} {col['type']:20} {'NULL' if col['nullable'] == 'YES' else 'NOT NULL'}")
        
        # 2. Get row count
        print("\n2. ROW COUNT")
        print("-" * 80)
        row_count = get_row_count(conn, 'budgetdetail')
        print(f"Total rows: {row_count:,}")
        
        # 3. Analyze sources
        source_data = analyze_budgetdetail_sources(conn)
        
        # 4. Analyze types
        type_data = analyze_budget_types(conn)
        
        # 5. Analyze approval status
        approval_data = analyze_approval_status(conn)
        
        # 6. Analyze project relationships
        project_rel = analyze_project_relationships(conn)
        project_col = project_rel['project_column'] if project_rel else None
        
        # 7. Source system comparison
        if project_col:
            source_comparison = analyze_source_system_comparison(conn, project_col)
        
        # 8. Analyze amounts
        amount_col = analyze_budget_amounts(conn)
        
        # 9. Find patterns
        patterns = find_interesting_patterns(conn)
        
        # Compile results
        results = {
            'table_name': 'budgetdetail',
            'schema': 'curated',
            'row_count': row_count,
            'column_count': len(schema),
            'columns': schema,
            'source_data': source_data,
            'type_data': type_data,
            'approval_data': approval_data,
            'project_relationship': project_rel,
            'amount_column': amount_col,
            'patterns': patterns
        }
        
        # Save results
        with open('BUDGETDETAIL_ANALYSIS.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n✓ Analysis saved to: BUDGETDETAIL_ANALYSIS.json")
        
        return results
    
    finally:
        conn.close()

if __name__ == "__main__":
    comprehensive_budgetdetail_analysis()
