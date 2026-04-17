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
Analyze Ingenious projects with budgets by project status
Exclude requested, cancelled, draft statuses
Calculate average budget amounts per project and breakdown by categories/codes
"""

from edp_connection import connect_to_edp
import json
from collections import defaultdict

def get_project_table_structure(conn):
    """Get the structure of the project table to find status field"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type
            FROM system.information_schema.columns
            WHERE table_schema = 'curated'
            AND table_catalog = 'work_dynamics'
            AND table_name = 'project'
            AND (column_name LIKE '%status%' OR column_name LIKE '%phase%' OR column_name LIKE '%state%')
            ORDER BY column_name
        """)
        results = cursor.fetchall()
        cursor.close()
        
        print("Status-related columns in project table:")
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 2:
                print(f"  {row[0]} ({row[1]})")
        return [row[0] for row in results if hasattr(row, '__getitem__')]
    except Exception as e:
        print(f"Error getting project structure: {e}")
        return []

def find_ingenious_projects(conn):
    """Find how to identify Ingenious projects"""
    try:
        cursor = conn.cursor()
        # Check for sourcesystem column in project table
        cursor.execute("""
            SELECT column_name
            FROM system.information_schema.columns
            WHERE table_schema = 'curated'
            AND table_catalog = 'work_dynamics'
            AND table_name = 'project'
            AND (column_name LIKE '%source%' OR column_name LIKE '%system%')
            ORDER BY column_name
        """)
        results = cursor.fetchall()
        cursor.close()
        
        source_columns = [row[0] for row in results if hasattr(row, '__getitem__')]
        print(f"\nSource-related columns in project table: {source_columns}")
        
        # Check distinct values in sourcesystem or sourcesystemname
        if source_columns:
            for col in source_columns[:3]:  # Check first 3
                try:
                    cursor = conn.cursor()
                    cursor.execute(f"""
                        SELECT {col}, COUNT(*) as cnt
                        FROM work_dynamics.curated.project
                        WHERE {col} IS NOT NULL
                        GROUP BY {col}
                        ORDER BY cnt DESC
                        LIMIT 10
                    """)
                    results = cursor.fetchall()
                    cursor.close()
                    
                    if results:
                        print(f"\nDistinct values in {col}:")
                        for row in results:
                            if hasattr(row, '__getitem__') and len(row) >= 2:
                                print(f"  {row[0]}: {row[1]:,}")
                except:
                    pass
        
        return source_columns
    except Exception as e:
        print(f"Error finding Ingenious projects: {e}")
        return []

def analyze_ingenious_budgets_by_status(conn):
    """Analyze Ingenious projects with budgets by status"""
    print("=" * 80)
    print("INGENIOUS PROJECTS WITH BUDGETS - BY STATUS ANALYSIS")
    print("=" * 80)
    
    # First, let's understand the project table structure
    print("\n1. Exploring project table structure...")
    status_columns = get_project_table_structure(conn)
    source_columns = find_ingenious_projects(conn)
    
    # Try to find the right way to join
    # We know budgetdetail has projectidentifier for Ingenious
    # Let's check if project table has projectidentifier or uses id
    
    print("\n2. Checking project identifier linkage...")
    try:
        cursor = conn.cursor()
        # Check if we can join budgetdetail to project via projectidentifier
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT bd.projectidentifier) as budget_projects,
                COUNT(DISTINCT p.id) as total_projects
            FROM work_dynamics.curated.budgetdetail bd
            LEFT JOIN work_dynamics.curated.project p 
                ON bd.projectidentifier = p.id
            WHERE bd.sourcesystem = 'ingenious'
            AND bd.projectidentifier IS NOT NULL
        """)
        result = cursor.fetchone()
        cursor.close()
        
        if result and hasattr(result, '__getitem__'):
            print(f"  Budget projects: {result[0]}")
            print(f"  Projects found via join: {result[1]}")
    except Exception as e:
        print(f"  Error checking join: {e}")
        # Try with sourceprojectidentifier
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT bd.projectidentifier) as budget_projects,
                    COUNT(DISTINCT p.id) as matched_projects
                FROM work_dynamics.curated.budgetdetail bd
                LEFT JOIN work_dynamics.curated.project p 
                    ON bd.projectidentifier = p.sourceprojectidentifier
                WHERE bd.sourcesystem = 'ingenious'
                AND bd.projectidentifier IS NOT NULL
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result and hasattr(result, '__getitem__'):
                print(f"  Budget projects: {result[0]}")
                print(f"  Projects matched via sourceprojectidentifier: {result[1]}")
        except Exception as e2:
            print(f"  Error with sourceprojectidentifier join: {e2}")
    
    # Now let's find status field and get the analysis
    print("\n3. Finding project status field...")
    status_field = None
    status_candidates = ['phasetext', 'status', 'projectstatus', 'statusname', 'phasename']
    
    for field in status_candidates:
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM system.information_schema.columns
                WHERE table_schema = 'curated'
                AND table_catalog = 'work_dynamics'
                AND table_name = 'project'
                AND column_name = '{field}'
            """)
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0] > 0:
                status_field = field
                print(f"  Found status field: {field}")
                break
        except:
            pass
    
    if not status_field:
        print("  Could not find status field, trying phasetext...")
        status_field = 'phasetext'  # Default to phasetext
    
    # Get distinct statuses
    print(f"\n4. Getting distinct project statuses from {status_field}...")
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT {status_field}, COUNT(*) as cnt
            FROM work_dynamics.curated.project
            WHERE {status_field} IS NOT NULL
            GROUP BY {status_field}
            ORDER BY cnt DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        print(f"\n  All project statuses:")
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 2:
                status = row[0] if row[0] else 'NULL'
                print(f"    {status}: {row[1]:,} projects")
    except Exception as e:
        print(f"  Error getting statuses: {e}")
    
    # Now perform the main analysis
    print("\n5. Analyzing Ingenious projects with budgets by status...")
    print("-" * 80)
    
    # Try joining budgetdetail to project
    # We'll try multiple join strategies
    join_queries = [
        # Try 1: projectidentifier = id
        f"""
        SELECT 
            p.{status_field} as project_status,
            COUNT(DISTINCT bd.projectidentifier) as project_count,
            COUNT(*) as budget_record_count,
            AVG(bd.totalapprovedbudgetamount) as avg_approved_amount,
            AVG(bd.totalbudgetcostamount) as avg_cost_amount,
            SUM(bd.totalapprovedbudgetamount) as total_approved_amount,
            SUM(bd.totalbudgetcostamount) as total_cost_amount
        FROM work_dynamics.curated.budgetdetail bd
        INNER JOIN work_dynamics.curated.project p 
            ON bd.projectidentifier = p.id
        WHERE bd.sourcesystem = 'ingenious'
        AND bd.projectidentifier IS NOT NULL
        AND p.{status_field} IS NOT NULL
        AND LOWER(p.{status_field}) NOT IN ('requested', 'cancelled', 'draft')
        GROUP BY p.{status_field}
        ORDER BY project_count DESC
        """,
        # Try 2: projectidentifier = sourceprojectidentifier
        f"""
        SELECT 
            p.{status_field} as project_status,
            COUNT(DISTINCT bd.projectidentifier) as project_count,
            COUNT(*) as budget_record_count,
            AVG(bd.totalapprovedbudgetamount) as avg_approved_amount,
            AVG(bd.totalbudgetcostamount) as avg_cost_amount,
            SUM(bd.totalapprovedbudgetamount) as total_approved_amount,
            SUM(bd.totalbudgetcostamount) as total_cost_amount
        FROM work_dynamics.curated.budgetdetail bd
        INNER JOIN work_dynamics.curated.project p 
            ON bd.projectidentifier = p.sourceprojectidentifier
        WHERE bd.sourcesystem = 'ingenious'
        AND bd.projectidentifier IS NOT NULL
        AND p.{status_field} IS NOT NULL
        AND LOWER(p.{status_field}) NOT IN ('requested', 'cancelled', 'draft')
        GROUP BY p.{status_field}
        ORDER BY project_count DESC
        """
    ]
    
    results_data = None
    for i, query in enumerate(join_queries, 1):
        try:
            print(f"\n  Attempting join strategy {i}...")
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            cursor.close()
            
            if results and len(results) > 0:
                print(f"  ✓ Success! Found {len(results)} status groups")
                results_data = (results, columns)
                break
        except Exception as e:
            print(f"  ✗ Strategy {i} failed: {str(e)[:150]}")
    
    if not results_data:
        print("\n  ⚠ Could not join budgetdetail to project table")
        print("  Will analyze budgetdetail data directly...")
        return analyze_budgetdetail_directly(conn)
    
    results, columns = results_data
    
    # Display results
    print(f"\n{'=' * 80}")
    print("INGENIOUS PROJECTS WITH BUDGETS - BY STATUS")
    print(f"{'=' * 80}\n")
    
    print(f"{'Status':<30} {'Projects':>12} {'Budget Records':>15} {'Avg Approved':>18} {'Total Approved':>20}")
    print("-" * 100)
    
    all_status_data = []
    for row in results:
        if hasattr(row, '__getitem__') and len(row) >= 7:
            status = row[0] if row[0] else 'NULL'
            project_count = row[1]
            budget_count = row[2]
            avg_approved = row[3] if row[3] else 0
            avg_cost = row[4] if row[4] else 0
            total_approved = row[5] if row[5] else 0
            total_cost = row[6] if row[6] else 0
            
            all_status_data.append({
                'status': status,
                'project_count': project_count,
                'budget_record_count': budget_count,
                'avg_approved_per_record': avg_approved,
                'avg_cost_per_record': avg_cost,
                'total_approved': total_approved,
                'total_cost': total_cost,
                'avg_approved_per_project': total_approved / project_count if project_count > 0 else 0,
                'avg_cost_per_project': total_cost / project_count if project_count > 0 else 0
            })
            
            print(f"{status:<30} {project_count:>12,} {budget_count:>15,} ${avg_approved:>17,.2f} ${total_approved:>19,.2f}")
    
    # Calculate overall averages
    total_projects = sum(d['project_count'] for d in all_status_data)
    total_budget_records = sum(d['budget_record_count'] for d in all_status_data)
    total_approved = sum(d['total_approved'] for d in all_status_data)
    total_cost = sum(d['total_cost'] for d in all_status_data)
    
    print("-" * 100)
    print(f"{'TOTAL':<30} {total_projects:>12,} {total_budget_records:>15,} ${total_approved/total_budget_records:>17,.2f} ${total_approved:>19,.2f}")
    print(f"\nOverall Average Budget per Project: ${total_approved/total_projects:,.2f}")
    print(f"Overall Average Budget per Record: ${total_approved/total_budget_records:,.2f}")
    
    # Now get category/code breakdown
    print(f"\n{'=' * 80}")
    print("BUDGET BREAKDOWN BY CATEGORY/CODE")
    print(f"{'=' * 80}\n")
    
    category_analysis = get_category_breakdown(conn, status_field, all_status_data)
    
    # Compile final results
    final_results = {
        'analysis_date': 'current',
        'source_system': 'ingenious',
        'excluded_statuses': ['requested', 'cancelled', 'draft'],
        'summary': {
            'total_projects': total_projects,
            'total_budget_records': total_budget_records,
            'total_approved_amount': total_approved,
            'total_cost_amount': total_cost,
            'avg_approved_per_project': total_approved / total_projects if total_projects > 0 else 0,
            'avg_cost_per_project': total_cost / total_projects if total_projects > 0 else 0
        },
        'by_status': all_status_data,
        'by_category': category_analysis
    }
    
    # Save results
    with open('INGENIOUS_BUDGETS_BY_STATUS.json', 'w') as f:
        json.dump(final_results, f, indent=2, default=str)
    print(f"\n✓ Results saved to: INGENIOUS_BUDGETS_BY_STATUS.json")
    
    return final_results

def get_category_breakdown(conn, status_field, status_data):
    """Get budget breakdown by category/code"""
    print("Analyzing budget amounts by category and code...")
    
    # Try to join and get category breakdown
    category_queries = [
        # Try with categoryname
        f"""
        SELECT 
            p.{status_field} as project_status,
            bd.categoryname,
            COUNT(*) as record_count,
            COUNT(DISTINCT bd.projectidentifier) as project_count,
            AVG(bd.totalapprovedbudgetamount) as avg_approved,
            SUM(bd.totalapprovedbudgetamount) as total_approved,
            AVG(bd.totalbudgetcostamount) as avg_cost,
            SUM(bd.totalbudgetcostamount) as total_cost
        FROM work_dynamics.curated.budgetdetail bd
        INNER JOIN work_dynamics.curated.project p 
            ON bd.projectidentifier = p.id
        WHERE bd.sourcesystem = 'ingenious'
        AND bd.projectidentifier IS NOT NULL
        AND p.{status_field} IS NOT NULL
        AND LOWER(p.{status_field}) NOT IN ('requested', 'cancelled', 'draft')
        AND bd.categoryname IS NOT NULL
        GROUP BY p.{status_field}, bd.categoryname
        ORDER BY total_approved DESC
        """,
        # Try with codename
        f"""
        SELECT 
            p.{status_field} as project_status,
            bd.codename,
            COUNT(*) as record_count,
            COUNT(DISTINCT bd.projectidentifier) as project_count,
            AVG(bd.totalapprovedbudgetamount) as avg_approved,
            SUM(bd.totalapprovedbudgetamount) as total_approved,
            AVG(bd.totalbudgetcostamount) as avg_cost,
            SUM(bd.totalbudgetcostamount) as total_cost
        FROM work_dynamics.curated.budgetdetail bd
        INNER JOIN work_dynamics.curated.project p 
            ON bd.projectidentifier = p.id
        WHERE bd.sourcesystem = 'ingenious'
        AND bd.projectidentifier IS NOT NULL
        AND p.{status_field} IS NOT NULL
        AND LOWER(p.{status_field}) NOT IN ('requested', 'cancelled', 'draft')
        AND bd.codename IS NOT NULL
        GROUP BY p.{status_field}, bd.codename
        ORDER BY total_approved DESC
        """,
        # Try with code
        f"""
        SELECT 
            p.{status_field} as project_status,
            bd.code,
            COUNT(*) as record_count,
            COUNT(DISTINCT bd.projectidentifier) as project_count,
            AVG(bd.totalapprovedbudgetamount) as avg_approved,
            SUM(bd.totalapprovedbudgetamount) as total_approved,
            AVG(bd.totalbudgetcostamount) as avg_cost,
            SUM(bd.totalbudgetcostamount) as total_cost
        FROM work_dynamics.curated.budgetdetail bd
        INNER JOIN work_dynamics.curated.project p 
            ON bd.projectidentifier = p.id
        WHERE bd.sourcesystem = 'ingenious'
        AND bd.projectidentifier IS NOT NULL
        AND p.{status_field} IS NOT NULL
        AND LOWER(p.{status_field}) NOT IN ('requested', 'cancelled', 'draft')
        AND bd.code IS NOT NULL
        GROUP BY p.{status_field}, bd.code
        ORDER BY total_approved DESC
        """
    ]
    
    category_results = []
    for i, query in enumerate(category_queries, 1):
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            if results and len(results) > 0:
                category_type = ['categoryname', 'codename', 'code'][i-1]
                print(f"\n  Found data in {category_type}: {len(results)} categories")
                
                # Group by category
                category_summary = defaultdict(lambda: {
                    'record_count': 0,
                    'project_count': set(),
                    'total_approved': 0,
                    'total_cost': 0
                })
                
                for row in results:
                    if hasattr(row, '__getitem__') and len(row) >= 8:
                        category = row[1] if row[1] else 'NULL'
                        record_count = row[2]
                        project_count = row[3]
                        total_approved = row[5] if row[5] else 0
                        total_cost = row[7] if row[7] else 0
                        
                        category_summary[category]['record_count'] += record_count
                        category_summary[category]['project_count'].add(project_count)
                        category_summary[category]['total_approved'] += total_approved
                        category_summary[category]['total_cost'] += total_cost
                
                # Convert to list
                category_list = []
                for cat, data in sorted(category_summary.items(), key=lambda x: x[1]['total_approved'], reverse=True):
                    category_list.append({
                        'category': cat,
                        'record_count': data['record_count'],
                        'project_count': len(data['project_count']),
                        'total_approved': data['total_approved'],
                        'total_cost': data['total_cost'],
                        'avg_approved': data['total_approved'] / data['record_count'] if data['record_count'] > 0 else 0
                    })
                
                category_results.append({
                    'type': category_type,
                    'categories': category_list
                })
                
                # Display top categories
                print(f"\n  Top 10 Categories by Total Approved Amount:")
                print(f"  {'Category':<40} {'Records':>12} {'Projects':>10} {'Total Approved':>20}")
                print("  " + "-" * 85)
                for cat in category_list[:10]:
                    print(f"  {cat['category']:<40} {cat['record_count']:>12,} {cat['project_count']:>10} ${cat['total_approved']:>19,.2f}")
                
                break
        except Exception as e:
            if i == len(category_queries):
                print(f"  Error getting category breakdown: {e}")
    
    return category_results

def analyze_budgetdetail_directly(conn):
    """Fallback: analyze budgetdetail directly without project join"""
    print("\nAnalyzing budgetdetail directly (without project join)...")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT projectidentifier) as project_count,
                COUNT(*) as budget_count,
                AVG(totalapprovedbudgetamount) as avg_approved,
                SUM(totalapprovedbudgetamount) as total_approved,
                AVG(totalbudgetcostamount) as avg_cost,
                SUM(totalbudgetcostamount) as total_cost
            FROM work_dynamics.curated.budgetdetail
            WHERE sourcesystem = 'ingenious'
            AND projectidentifier IS NOT NULL
        """)
        result = cursor.fetchone()
        cursor.close()
        
        if result and hasattr(result, '__getitem__'):
            print(f"\n  Projects with budgets: {result[0]}")
            print(f"  Budget records: {result[1]}")
            print(f"  Average approved per record: ${result[2]:,.2f}")
            print(f"  Total approved: ${result[4]:,.2f}")
            print(f"  Average approved per project: ${result[4]/result[0]:,.2f}")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    conn = connect_to_edp()
    try:
        analyze_ingenious_budgets_by_status(conn)
    finally:
        conn.close()
