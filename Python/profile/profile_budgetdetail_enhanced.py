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
Enhanced comprehensive data profiling and analysis of budgetdetail table
Fixing issues and adding deeper insights
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

def analyze_source_system_comparison(conn):
    """Compare budget data by source system (Clarizen vs Ingenious)"""
    print("\n" + "=" * 80)
    print("SOURCE SYSTEM COMPARISON (Clarizen vs Ingenious)")
    print("=" * 80)
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                sourcesystem,
                COUNT(*) as budget_count,
                COUNT(DISTINCT projectidentifier) as project_count,
                COUNT(DISTINCT budgetidentifier) as budget_count_distinct,
                COUNT(DISTINCT workitemidentifier) as workitem_count
            FROM work_dynamics.curated.budgetdetail
            WHERE sourcesystem IS NOT NULL
            AND projectidentifier IS NOT NULL
            GROUP BY sourcesystem
            ORDER BY budget_count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        print(f"\nBudget data by source system:")
        total_budgets = 0
        total_projects = 0
        
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 5:
                source = row[0]
                budget_count = row[1]
                project_count = row[2]
                budget_distinct = row[3]
                workitem_count = row[4]
                
                total_budgets += budget_count
                total_projects += project_count
                
                print(f"\n  {source.upper()}:")
                print(f"    Total budget records: {budget_count:,}")
                print(f"    Distinct budgets: {budget_distinct:,}")
                print(f"    Projects with budgets: {project_count:,}")
                print(f"    Work items: {workitem_count:,}")
                if project_count > 0:
                    print(f"    Avg budget records per project: {budget_count / project_count:.2f}")
                    print(f"    Avg distinct budgets per project: {budget_distinct / project_count:.2f}")
        
        # Comparison
        if len(results) >= 2:
            clarizen = next((r for r in results if r[0] and 'clarizen' in str(r[0]).lower()), None)
            ingenious = next((r for r in results if r[0] and 'ingenious' in str(r[0]).lower()), None)
            
            if clarizen and ingenious:
                print(f"\n  COMPARISON:")
                clarizen_budgets = clarizen[1]
                ingenious_budgets = ingenious[1]
                ratio = clarizen_budgets / ingenious_budgets if ingenious_budgets > 0 else 0
                print(f"    Clarizen has {ratio:.1f}x more budget records than Ingenious")
                
                clarizen_projects = clarizen[2]
                ingenious_projects = ingenious[2]
                if clarizen_projects > 0 and ingenious_projects > 0:
                    print(f"    Clarizen projects: {clarizen_projects:,}")
                    print(f"    Ingenious projects: {ingenious_projects:,}")
        
        return results
    except Exception as e:
        print(f"Error comparing source systems: {e}")
        return None

def analyze_budget_amounts_detailed(conn):
    """Analyze all budget amount columns"""
    print("\n" + "=" * 80)
    print("BUDGET AMOUNT ANALYSIS (All Amount Columns)")
    print("=" * 80)
    
    amount_columns = [
        'totalbudgetcostamount',
        'totalapprovedbudgetamount',
        'totalpendingamount',
        'totalbudgetoriginalamount',
        'totalbudgetcurrentamount',
        'totalbudgetprojectedamount',
        'variancetothebudgetamount',
        'totalvalue',
        'paidamount',
        'unpaidamount'
    ]
    
    amount_stats = {}
    
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
                    stats = {
                        'total_records': result[0],
                        'non_null_records': result[1],
                        'min': result[2],
                        'max': result[3],
                        'avg': result[4],
                        'total': result[5],
                        'median': result[6],
                        'p25': result[7],
                        'p75': result[8]
                    }
                    amount_stats[col] = stats
                    
                    print(f"\n  {col}:")
                    print(f"    Records with value: {stats['non_null_records']:,} ({stats['non_null_records']/stats['total_records']*100:.1f}%)")
                    print(f"    Min: ${stats['min']:,.2f}")
                    print(f"    Max: ${stats['max']:,.2f}")
                    print(f"    Average: ${stats['avg']:,.2f}")
                    print(f"    Median: ${stats['median']:,.2f}")
                    print(f"    Total: ${stats['total']:,.2f}")
                    print(f"    25th-75th percentile: ${stats['p25']:,.2f} - ${stats['p75']:,.2f}")
        except Exception as e:
            print(f"  Error analyzing {col}: {e}")
    
    return amount_stats

def analyze_approval_status_detailed(conn):
    """Analyze approval status in detail"""
    print("\n" + "=" * 80)
    print("APPROVAL STATUS ANALYSIS")
    print("=" * 80)
    
    # Check if there's an approval column, or infer from totalapprovedbudgetamount
    try:
        cursor = conn.cursor()
        # Check if totalapprovedbudgetamount has values
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(totalapprovedbudgetamount) as has_approved_amount,
                SUM(CASE WHEN totalapprovedbudgetamount IS NOT NULL AND totalapprovedbudgetamount > 0 THEN 1 ELSE 0 END) as approved_with_amount,
                SUM(CASE WHEN totalapprovedbudgetamount IS NULL OR totalapprovedbudgetamount = 0 THEN 1 ELSE 0 END) as not_approved
            FROM work_dynamics.curated.budgetdetail
        """)
        result = cursor.fetchone()
        cursor.close()
        
        if result and hasattr(result, '__getitem__') and len(result) >= 4:
            total = result[0]
            has_approved = result[1]
            approved_with_amount = result[2]
            not_approved = result[3]
            
            print(f"\nApproval Status (based on totalapprovedbudgetamount):")
            print(f"  Total records: {total:,}")
            print(f"  Records with approved amount: {has_approved:,} ({has_approved/total*100:.1f}%)")
            print(f"  Records with approved amount > 0: {approved_with_amount:,} ({approved_with_amount/total*100:.1f}%)")
            print(f"  Records without approved amount: {not_approved:,} ({not_approved/total*100:.1f}%)")
            
            # Compare approved vs current vs original
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN totalapprovedbudgetamount IS NOT NULL AND totalapprovedbudgetamount > 0 THEN 1 ELSE 0 END) as approved,
                    SUM(CASE WHEN totalbudgetcurrentamount IS NOT NULL AND totalbudgetcurrentamount > 0 THEN 1 ELSE 0 END) as current,
                    SUM(CASE WHEN totalbudgetoriginalamount IS NOT NULL AND totalbudgetoriginalamount > 0 THEN 1 ELSE 0 END) as original,
                    SUM(CASE WHEN totalbudgetprojectedamount IS NOT NULL AND totalbudgetprojectedamount > 0 THEN 1 ELSE 0 END) as projected
                FROM work_dynamics.curated.budgetdetail
            """)
            result2 = cursor.fetchone()
            cursor.close()
            
            if result2 and hasattr(result2, '__getitem__'):
                print(f"\nBudget Status Breakdown:")
                print(f"  Approved budgets: {result2[1]:,} ({result2[1]/result2[0]*100:.1f}%)")
                print(f"  Current budgets: {result2[2]:,} ({result2[2]/result2[0]*100:.1f}%)")
                print(f"  Original budgets: {result2[3]:,} ({result2[3]/result2[0]*100:.1f}%)")
                print(f"  Projected budgets: {result2[4]:,} ({result2[4]/result2[0]*100:.1f}%)")
            
            return {
                'total': total,
                'approved': approved_with_amount,
                'not_approved': not_approved
            }
    except Exception as e:
        print(f"Error analyzing approval status: {e}")
        return None

def analyze_project_relationships_enhanced(conn):
    """Enhanced project relationship analysis"""
    print("\n" + "=" * 80)
    print("PROJECT RELATIONSHIP ANALYSIS")
    print("=" * 80)
    
    # Get projects with budgets
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT projectidentifier) as project_count
            FROM work_dynamics.curated.budgetdetail
            WHERE projectidentifier IS NOT NULL
        """)
        result = cursor.fetchone()
        projects_with_budget = result[0] if result and hasattr(result, '__getitem__') else 0
        cursor.close()
        print(f"\nProjects with budget data: {projects_with_budget:,}")
    except Exception as e:
        print(f"Error counting projects: {e}")
        projects_with_budget = 0
    
    # Try to get total projects from project table
    total_projects = None
    project_tables = [
        ('curated', 'project'),
        ('curated', 'projects'),
        ('curated_consumption', 'vw_ingenious_project'),
        ('curated_consumption', 'project')
    ]
    
    for schema, table_name in project_tables:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(DISTINCT projectidentifier) FROM work_dynamics.{schema}.{table_name}")
            result = cursor.fetchone()
            total_projects = result[0] if result and hasattr(result, '__getitem__') else None
            cursor.close()
            if total_projects and total_projects > 0:
                print(f"Total distinct projects in {schema}.{table_name}: {total_projects:,}")
                break
        except:
            try:
                # Try with id column
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(DISTINCT id) FROM work_dynamics.{schema}.{table_name}")
                result = cursor.fetchone()
                total_projects = result[0] if result and hasattr(result, '__getitem__') else None
                cursor.close()
                if total_projects and total_projects > 0:
                    print(f"Total distinct projects in {schema}.{table_name}: {total_projects:,}")
                    break
            except:
                pass
    
    if total_projects and total_projects > 0:
        coverage = (projects_with_budget / total_projects * 100) if total_projects > 0 else 0
        print(f"\nBudget coverage: {coverage:.1f}% of projects have budget data")
        print(f"Projects without budget: {total_projects - projects_with_budget:,}")
    
    # Analyze budgets per project
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                projectidentifier,
                COUNT(*) as budget_count,
                COUNT(DISTINCT budgetidentifier) as distinct_budgets,
                SUM(totalapprovedbudgetamount) as total_approved,
                SUM(totalbudgetcurrentamount) as total_current
            FROM work_dynamics.curated.budgetdetail
            WHERE projectidentifier IS NOT NULL
            GROUP BY projectidentifier
            ORDER BY budget_count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        budget_counts = [row[1] for row in results if hasattr(row, '__getitem__') and len(row) >= 2]
        
        if budget_counts:
            import statistics
            print(f"\nBudgets per project statistics:")
            print(f"  Total projects with budgets: {len(budget_counts):,}")
            print(f"  Average budget records per project: {statistics.mean(budget_counts):.2f}")
            print(f"  Median budget records per project: {statistics.median(budget_counts):.2f}")
            print(f"  Min budget records per project: {min(budget_counts)}")
            print(f"  Max budget records per project: {max(budget_counts)}")
            
            # Distribution
            print(f"\nDistribution of budget records per project:")
            ranges = [(1, 1), (2, 5), (6, 10), (11, 20), (21, 50), (51, 100), (101, float('inf'))]
            for start, end in ranges:
                if end == float('inf'):
                    count = sum(1 for c in budget_counts if c >= start)
                    print(f"  {start}+ records: {count:,} projects")
                else:
                    count = sum(1 for c in budget_counts if start <= c <= end)
                    print(f"  {start}-{end} records: {count:,} projects")
            
            # Top projects by budget count
            print(f"\nTop 10 projects by budget record count:")
            for i, row in enumerate(results[:10], 1):
                if hasattr(row, '__getitem__') and len(row) >= 5:
                    proj_id = row[0]
                    budget_count = row[1]
                    distinct_budgets = row[2]
                    total_approved = row[3] if row[3] else 0
                    total_current = row[4] if row[4] else 0
                    print(f"  {i}. Project {proj_id}: {budget_count} records, {distinct_budgets} distinct budgets, ${total_approved:,.2f} approved, ${total_current:,.2f} current")
    except Exception as e:
        print(f"Error analyzing budgets per project: {e}")
    
    return {
        'projects_with_budget': projects_with_budget,
        'total_projects': total_projects
    }

def analyze_budget_categories(conn):
    """Analyze budget categories"""
    print("\n" + "=" * 80)
    print("BUDGET CATEGORY ANALYSIS")
    print("=" * 80)
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                categoryname,
                COUNT(*) as count,
                COUNT(DISTINCT projectidentifier) as project_count,
                SUM(totalapprovedbudgetamount) as total_approved
            FROM work_dynamics.curated.budgetdetail
            WHERE categoryname IS NOT NULL
            GROUP BY categoryname
            ORDER BY count DESC
            LIMIT 20
        """)
        results = cursor.fetchall()
        cursor.close()
        
        print(f"\nTop budget categories:")
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 4:
                category = row[0]
                count = row[1]
                project_count = row[2]
                total_approved = row[3] if row[3] else 0
                print(f"  {category}: {count:,} records, {project_count:,} projects, ${total_approved:,.2f} total approved")
    except Exception as e:
        print(f"Error analyzing categories: {e}")

def find_interesting_patterns_enhanced(conn):
    """Enhanced pattern analysis"""
    print("\n" + "=" * 80)
    print("PATTERN & ANOMALY ANALYSIS")
    print("=" * 80)
    
    # Check for projects with budgets but no approved amounts
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT projectidentifier) as projects_without_approved
            FROM work_dynamics.curated.budgetdetail
            WHERE projectidentifier IS NOT NULL
            AND (totalapprovedbudgetamount IS NULL OR totalapprovedbudgetamount = 0)
            AND (totalbudgetcurrentamount IS NOT NULL AND totalbudgetcurrentamount > 0)
        """)
        result = cursor.fetchone()
        projects_without_approved = result[0] if result and hasattr(result, '__getitem__') else 0
        cursor.close()
        print(f"\nProjects with budget amounts but no approved amounts: {projects_without_approved:,}")
    except Exception as e:
        print(f"Error checking approval patterns: {e}")
    
    # Check variance patterns
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN variancetothebudgetamount > 0 THEN 1 ELSE 0 END) as positive_variance,
                SUM(CASE WHEN variancetothebudgetamount < 0 THEN 1 ELSE 0 END) as negative_variance,
                SUM(CASE WHEN variancetothebudgetamount = 0 THEN 1 ELSE 0 END) as no_variance,
                AVG(variancetothebudgetamount) as avg_variance
            FROM work_dynamics.curated.budgetdetail
            WHERE variancetothebudgetamount IS NOT NULL
        """)
        result = cursor.fetchone()
        cursor.close()
        
        if result and hasattr(result, '__getitem__') and len(result) >= 5:
            total = result[0]
            if total > 0:
                print(f"\nBudget Variance Analysis:")
                print(f"  Records with variance data: {total:,}")
                print(f"  Positive variance (over budget): {result[1]:,} ({result[1]/total*100:.1f}%)")
                print(f"  Negative variance (under budget): {result[2]:,} ({result[2]/total*100:.1f}%)")
                print(f"  No variance: {result[3]:,} ({result[3]/total*100:.1f}%)")
                print(f"  Average variance: ${result[4]:,.2f}")
    except Exception as e:
        print(f"Error analyzing variance: {e}")
    
    # Check currency patterns
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                currencytypecode,
                COUNT(*) as count,
                COUNT(DISTINCT projectidentifier) as project_count
            FROM work_dynamics.curated.budgetdetail
            WHERE currencytypecode IS NOT NULL
            GROUP BY currencytypecode
            ORDER BY count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        if results:
            print(f"\nCurrency Distribution:")
            for row in results:
                if hasattr(row, '__getitem__') and len(row) >= 3:
                    currency = row[0]
                    count = row[1]
                    project_count = row[2]
                    print(f"  {currency}: {count:,} records, {project_count:,} projects")
    except Exception as e:
        print(f"Error analyzing currency: {e}")

def comprehensive_budgetdetail_analysis():
    """Perform comprehensive analysis of budgetdetail table"""
    print("=" * 80)
    print("COMPREHENSIVE BUDGETDETAIL DATA PROFILING & ANALYSIS")
    print("=" * 80)
    
    conn = connect_to_edp()
    
    try:
        # Get row count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM work_dynamics.curated.budgetdetail")
        row_count = cursor.fetchone()[0]
        cursor.close()
        print(f"\nTotal rows: {row_count:,}")
        
        # 1. Source system comparison
        source_comparison = analyze_source_system_comparison(conn)
        
        # 2. Project relationships
        project_rel = analyze_project_relationships_enhanced(conn)
        
        # 3. Budget amounts
        amount_stats = analyze_budget_amounts_detailed(conn)
        
        # 4. Approval status
        approval_data = analyze_approval_status_detailed(conn)
        
        # 5. Categories
        analyze_budget_categories(conn)
        
        # 6. Patterns
        find_interesting_patterns_enhanced(conn)
        
        # Compile results
        results = {
            'table_name': 'budgetdetail',
            'schema': 'curated',
            'row_count': row_count,
            'source_comparison': source_comparison,
            'project_relationship': project_rel,
            'amount_statistics': amount_stats,
            'approval_data': approval_data
        }
        
        # Save results
        with open('BUDGETDETAIL_ANALYSIS_ENHANCED.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n✓ Enhanced analysis saved to: BUDGETDETAIL_ANALYSIS_ENHANCED.json")
        
        return results
    
    finally:
        conn.close()

if __name__ == "__main__":
    comprehensive_budgetdetail_analysis()
