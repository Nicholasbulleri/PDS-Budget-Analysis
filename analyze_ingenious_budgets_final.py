#!/usr/bin/env python3
"""
Final analysis of Ingenious projects with budgets by status
Using cost amounts (since approved amounts are all zero)
With category/code breakdown
"""

from edp_connection import connect_to_edp
import json

def analyze_ingenious_budgets_final():
    """Final comprehensive analysis"""
    print("=" * 80)
    print("INGENIOUS PROJECTS WITH BUDGETS - FINAL ANALYSIS")
    print("=" * 80)
    
    conn = connect_to_edp()
    
    try:
        # Main analysis by status using cost amounts
        print("\n1. Analyzing by project status (excluding requested, cancelled, draft)...")
        print("-" * 80)
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.phasetext as project_status,
                COUNT(DISTINCT bd.projectidentifier) as project_count,
                COUNT(*) as budget_record_count,
                AVG(bd.totalbudgetcostamount) as avg_cost_per_record,
                SUM(bd.totalbudgetcostamount) as total_cost_amount,
                MIN(bd.totalbudgetcostamount) as min_cost,
                MAX(bd.totalbudgetcostamount) as max_cost,
                PERCENTILE(bd.totalbudgetcostamount, 0.5) as median_cost
            FROM work_dynamics.curated.budgetdetail bd
            INNER JOIN work_dynamics.curated.project p 
                ON bd.projectidentifier = p.id
            WHERE bd.sourcesystem = 'ingenious'
            AND bd.projectidentifier IS NOT NULL
            AND p.phasetext IS NOT NULL
            AND LOWER(p.phasetext) NOT IN ('requested', 'cancelled', 'draft')
            AND bd.totalbudgetcostamount IS NOT NULL
            AND bd.totalbudgetcostamount > 0
            GROUP BY p.phasetext
            ORDER BY project_count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        print(f"\n{'Status':<25} {'Projects':>10} {'Records':>12} {'Avg/Record':>18} {'Total Cost':>20} {'Avg/Project':>18}")
        print("-" * 110)
        
        status_data = []
        total_projects = 0
        total_records = 0
        total_cost = 0
        
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 8:
                status = row[0] if row[0] else 'NULL'
                project_count = row[1]
                record_count = row[2]
                avg_per_record = row[3] if row[3] else 0
                total = row[4] if row[4] else 0
                min_cost = row[5] if row[5] else 0
                max_cost = row[6] if row[6] else 0
                median_cost = row[7] if row[7] else 0
                
                avg_per_project = total / project_count if project_count > 0 else 0
                
                status_data.append({
                    'status': status,
                    'project_count': project_count,
                    'budget_record_count': record_count,
                    'avg_cost_per_record': avg_per_record,
                    'total_cost_amount': total,
                    'avg_cost_per_project': avg_per_project,
                    'min_cost': min_cost,
                    'max_cost': max_cost,
                    'median_cost': median_cost
                })
                
                total_projects += project_count
                total_records += record_count
                total_cost += total
                
                print(f"{status:<25} {project_count:>10,} {record_count:>12,} ${avg_per_record:>17,.2f} ${total:>19,.2f} ${avg_per_project:>17,.2f}")
        
        print("-" * 110)
        overall_avg_per_project = total_cost / total_projects if total_projects > 0 else 0
        overall_avg_per_record = total_cost / total_records if total_records > 0 else 0
        print(f"{'TOTAL':<25} {total_projects:>10,} {total_records:>12,} ${overall_avg_per_record:>17,.2f} ${total_cost:>19,.2f} ${overall_avg_per_project:>17,.2f}")
        
        print(f"\nOverall Statistics:")
        print(f"  Total Projects with Budgets: {total_projects:,}")
        print(f"  Total Budget Records: {total_records:,}")
        print(f"  Total Budget Amount: ${total_cost:,.2f}")
        print(f"  Average Budget per Project: ${overall_avg_per_project:,.2f}")
        print(f"  Average Budget per Record: ${overall_avg_per_record:,.2f}")
        
        # Category breakdown
        print(f"\n{'=' * 80}")
        print("BUDGET BREAKDOWN BY CATEGORY")
        print(f"{'=' * 80}\n")
        
        category_data = get_category_breakdown_final(conn)
        
        # Code breakdown
        print(f"\n{'=' * 80}")
        print("BUDGET BREAKDOWN BY CODE")
        print(f"{'=' * 80}\n")
        
        code_data = get_code_breakdown_final(conn)
        
        # Compile final results
        final_results = {
            'analysis_date': 'current',
            'source_system': 'ingenious',
            'excluded_statuses': ['requested', 'cancelled', 'draft'],
            'amount_field_used': 'totalbudgetcostamount',
            'summary': {
                'total_projects': total_projects,
                'total_budget_records': total_records,
                'total_budget_amount': total_cost,
                'avg_budget_per_project': overall_avg_per_project,
                'avg_budget_per_record': overall_avg_per_record
            },
            'by_status': status_data,
            'by_category': category_data,
            'by_code': code_data
        }
        
        # Save results
        with open('INGENIOUS_BUDGETS_FINAL.json', 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        print(f"\n✓ Results saved to: INGENIOUS_BUDGETS_FINAL.json")
        
        # Create markdown report
        create_markdown_report(final_results)
        
        return final_results
    
    finally:
        conn.close()

def get_category_breakdown_final(conn):
    """Get budget breakdown by category"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                bd.categoryname,
                COUNT(DISTINCT bd.projectidentifier) as project_count,
                COUNT(*) as record_count,
                AVG(bd.totalbudgetcostamount) as avg_cost,
                SUM(bd.totalbudgetcostamount) as total_cost,
                MIN(bd.totalbudgetcostamount) as min_cost,
                MAX(bd.totalbudgetcostamount) as max_cost
            FROM work_dynamics.curated.budgetdetail bd
            INNER JOIN work_dynamics.curated.project p 
                ON bd.projectidentifier = p.id
            WHERE bd.sourcesystem = 'ingenious'
            AND bd.projectidentifier IS NOT NULL
            AND p.phasetext IS NOT NULL
            AND LOWER(p.phasetext) NOT IN ('requested', 'cancelled', 'draft')
            AND bd.categoryname IS NOT NULL
            AND bd.totalbudgetcostamount IS NOT NULL
            AND bd.totalbudgetcostamount > 0
            GROUP BY bd.categoryname
            ORDER BY total_cost DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        if results and len(results) > 0:
            print(f"{'Category':<40} {'Projects':>10} {'Records':>12} {'Total Cost':>20} {'Avg Cost':>18}")
            print("-" * 105)
            
            category_list = []
            for row in results:
                if hasattr(row, '__getitem__') and len(row) >= 7:
                    category = row[0] if row[0] else 'NULL'
                    project_count = row[1]
                    record_count = row[2]
                    avg_cost = row[3] if row[3] else 0
                    total_cost = row[4] if row[4] else 0
                    min_cost = row[5] if row[5] else 0
                    max_cost = row[6] if row[6] else 0
                    
                    category_list.append({
                        'category': category,
                        'project_count': project_count,
                        'record_count': record_count,
                        'total_cost': total_cost,
                        'avg_cost': avg_cost,
                        'min_cost': min_cost,
                        'max_cost': max_cost
                    })
                    
                    print(f"{category:<40} {project_count:>10,} {record_count:>12,} ${total_cost:>19,.2f} ${avg_cost:>17,.2f}")
            
            return category_list
        else:
            print("  No category data found")
            return []
    except Exception as e:
        print(f"  Error getting category breakdown: {e}")
        return []

def get_code_breakdown_final(conn):
    """Get budget breakdown by code"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                bd.code,
                bd.codename,
                COUNT(DISTINCT bd.projectidentifier) as project_count,
                COUNT(*) as record_count,
                AVG(bd.totalbudgetcostamount) as avg_cost,
                SUM(bd.totalbudgetcostamount) as total_cost,
                MIN(bd.totalbudgetcostamount) as min_cost,
                MAX(bd.totalbudgetcostamount) as max_cost
            FROM work_dynamics.curated.budgetdetail bd
            INNER JOIN work_dynamics.curated.project p 
                ON bd.projectidentifier = p.id
            WHERE bd.sourcesystem = 'ingenious'
            AND bd.projectidentifier IS NOT NULL
            AND p.phasetext IS NOT NULL
            AND LOWER(p.phasetext) NOT IN ('requested', 'cancelled', 'draft')
            AND bd.code IS NOT NULL
            AND bd.totalbudgetcostamount IS NOT NULL
            AND bd.totalbudgetcostamount > 0
            GROUP BY bd.code, bd.codename
            ORDER BY total_cost DESC
            LIMIT 50
        """)
        results = cursor.fetchall()
        cursor.close()
        
        if results and len(results) > 0:
            print(f"{'Code':<20} {'Code Name':<40} {'Projects':>10} {'Records':>12} {'Total Cost':>20}")
            print("-" * 110)
            
            code_list = []
            for row in results:
                if hasattr(row, '__getitem__') and len(row) >= 8:
                    code = row[0] if row[0] else 'NULL'
                    code_name = row[1] if row[1] else 'NULL'
                    project_count = row[2]
                    record_count = row[3]
                    avg_cost = row[4] if row[4] else 0
                    total_cost = row[5] if row[5] else 0
                    min_cost = row[6] if row[6] else 0
                    max_cost = row[7] if row[7] else 0
                    
                    code_list.append({
                        'code': code,
                        'code_name': code_name,
                        'project_count': project_count,
                        'record_count': record_count,
                        'total_cost': total_cost,
                        'avg_cost': avg_cost,
                        'min_cost': min_cost,
                        'max_cost': max_cost
                    })
                    
                    code_display = code[:18] if len(code) <= 18 else code[:15] + '...'
                    name_display = code_name[:38] if code_name and len(code_name) <= 38 else (code_name[:35] + '...' if code_name else 'NULL')
                    print(f"{code_display:<20} {name_display:<40} {project_count:>10,} {record_count:>12,} ${total_cost:>19,.2f}")
            
            return code_list
        else:
            print("  No code data found")
            return []
    except Exception as e:
        print(f"  Error getting code breakdown: {e}")
        return []

def create_markdown_report(results):
    """Create a markdown report"""
    report = f"""# Ingenious Projects with Budgets - Analysis Report

## Summary

**Analysis Date**: {results['analysis_date']}  
**Source System**: {results['source_system']}  
**Excluded Statuses**: {', '.join(results['excluded_statuses'])}  
**Amount Field Used**: {results['amount_field_used']}

### Overall Statistics

- **Total Projects with Budgets**: {results['summary']['total_projects']:,}
- **Total Budget Records**: {results['summary']['total_budget_records']:,}
- **Total Budget Amount**: ${results['summary']['total_budget_amount']:,.2f}
- **Average Budget per Project**: ${results['summary']['avg_budget_per_project']:,.2f}
- **Average Budget per Record**: ${results['summary']['avg_budget_per_record']:,.2f}

---

## Budget Analysis by Project Status

| Status | Projects | Budget Records | Avg per Record | Total Cost | Avg per Project |
|--------|----------|---------------|----------------|------------|-----------------|
"""
    
    for status in results['by_status']:
        report += f"| {status['status']} | {status['project_count']:,} | {status['budget_record_count']:,} | ${status['avg_cost_per_record']:,.2f} | ${status['total_cost_amount']:,.2f} | ${status['avg_cost_per_project']:,.2f} |\n"
    
    report += "\n---\n\n## Budget Breakdown by Category\n\n"
    report += "| Category | Projects | Records | Total Cost | Avg Cost |\n"
    report += "|----------|----------|---------|------------|----------|\n"
    
    for cat in results['by_category'][:20]:  # Top 20
        report += f"| {cat['category']} | {cat['project_count']:,} | {cat['record_count']:,} | ${cat['total_cost']:,.2f} | ${cat['avg_cost']:,.2f} |\n"
    
    report += "\n---\n\n## Budget Breakdown by Code (Top 20)\n\n"
    report += "| Code | Code Name | Projects | Records | Total Cost |\n"
    report += "|------|-----------|----------|---------|------------|\n"
    
    for code in results['by_code'][:20]:  # Top 20
        code_name = code['code_name'] if code['code_name'] else 'NULL'
        report += f"| {code['code']} | {code_name} | {code['project_count']:,} | {code['record_count']:,} | ${code['total_cost']:,.2f} |\n"
    
    report += "\n---\n\n*Report generated from INGENIOUS_BUDGETS_FINAL.json*\n"
    
    with open('INGENIOUS_BUDGETS_REPORT.md', 'w') as f:
        f.write(report)
    
    print(f"✓ Markdown report saved to: INGENIOUS_BUDGETS_REPORT.md")

if __name__ == "__main__":
    analyze_ingenious_budgets_final()
