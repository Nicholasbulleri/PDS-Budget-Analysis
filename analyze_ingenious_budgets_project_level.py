#!/usr/bin/env python3
"""
Analyze Ingenious projects with budgets using project-level fields
1. Count budgets per project by status
2. Average budget amounts from project table
3. Breakdown by budgetitemname
"""

from edp_connection import connect_to_edp
import json

def analyze_ingenious_budgets_project_level():
    """Comprehensive analysis using project-level budget fields"""
    print("=" * 80)
    print("INGENIOUS PROJECTS - PROJECT-LEVEL BUDGET ANALYSIS")
    print("=" * 80)
    
    conn = connect_to_edp()
    
    try:
        # 1. Count budgets per project by status
        print("\n1. BUDGET COUNT PER PROJECT BY STATUS")
        print("-" * 80)
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.phasetext as project_status,
                COUNT(DISTINCT p.id) as project_count,
                COUNT(DISTINCT bd.budgetidentifier) as distinct_budget_count,
                COUNT(bd.id) as total_budget_records,
                AVG(budget_counts.budget_count) as avg_budgets_per_project
            FROM work_dynamics.curated.project p
            INNER JOIN work_dynamics.curated.budgetdetail bd
                ON bd.projectidentifier = p.id
            INNER JOIN (
                SELECT 
                    projectidentifier,
                    COUNT(DISTINCT budgetidentifier) as budget_count
                FROM work_dynamics.curated.budgetdetail
                WHERE sourcesystem = 'ingenious'
                AND projectidentifier IS NOT NULL
                GROUP BY projectidentifier
            ) budget_counts
                ON budget_counts.projectidentifier = p.id
            WHERE p.sourcesystem = 'ingenious'
            AND bd.sourcesystem = 'ingenious'
            AND p.phasetext IS NOT NULL
            AND LOWER(p.phasetext) NOT IN ('requested', 'cancelled', 'draft')
            AND p.originalbudgetamount IS NOT NULL
            GROUP BY p.phasetext
            ORDER BY project_count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        print(f"\n{'Status':<25} {'Projects':>10} {'Distinct Budgets':>18} {'Total Records':>15} {'Avg Budgets/Project':>20}")
        print("-" * 95)
        
        budget_count_data = []
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 5:
                status = row[0] if row[0] else 'NULL'
                project_count = row[1]
                distinct_budgets = row[2]
                total_records = row[3]
                avg_budgets = row[4] if row[4] else 0
                
                budget_count_data.append({
                    'status': status,
                    'project_count': project_count,
                    'distinct_budget_count': distinct_budgets,
                    'total_budget_records': total_records,
                    'avg_budgets_per_project': avg_budgets
                })
                
                print(f"{status:<25} {project_count:>10,} {distinct_budgets:>18,} {total_records:>15,} {avg_budgets:>20.2f}")
        
        # 2. Average budget amounts from project table
        print(f"\n{'=' * 80}")
        print("2. AVERAGE BUDGET AMOUNTS PER PROJECT (from project table)")
        print("-" * 80)
        print("Note: Only includes projects with budgets (originalbudgetamount IS NOT NULL)")
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.phasetext as project_status,
                COUNT(DISTINCT p.id) as project_count,
                AVG(p.totalapprovedbudgetamount) as avg_totalapproved,
                AVG(p.originalbudgetamount) as avg_original,
                AVG(p.totalprojectedbudget) as avg_projected,
                SUM(p.totalapprovedbudgetamount) as total_approved,
                SUM(p.originalbudgetamount) as total_original,
                SUM(p.totalprojectedbudget) as total_projected
            FROM work_dynamics.curated.project p
            WHERE p.sourcesystem = 'ingenious'
            AND p.phasetext IS NOT NULL
            AND LOWER(p.phasetext) NOT IN ('requested', 'cancelled', 'draft')
            AND p.originalbudgetamount IS NOT NULL
            GROUP BY p.phasetext
            ORDER BY project_count DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        print(f"\n{'Status':<25} {'Projects':>10} {'Avg Approved':>18} {'Avg Original':>18} {'Avg Projected':>18}")
        print("-" * 95)
        
        project_budget_data = []
        total_projects_all = 0
        total_approved_all = 0
        total_original_all = 0
        total_projected_all = 0
        
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 8:
                status = row[0] if row[0] else 'NULL'
                project_count = row[1]
                avg_approved = row[2] if row[2] else 0
                avg_original = row[3] if row[3] else 0
                avg_projected = row[4] if row[4] else 0
                total_approved = row[5] if row[5] else 0
                total_original = row[6] if row[6] else 0
                total_projected = row[7] if row[7] else 0
                
                project_budget_data.append({
                    'status': status,
                    'project_count': project_count,
                    'avg_totalapprovedbudgetamount': avg_approved,
                    'avg_originalbudgetamount': avg_original,
                    'avg_totalprojectedbudget': avg_projected,
                    'total_approved': total_approved,
                    'total_original': total_original,
                    'total_projected': total_projected
                })
                
                total_projects_all += project_count
                total_approved_all += total_approved
                total_original_all += total_original
                total_projected_all += total_projected
                
                print(f"{status:<25} {project_count:>10,} ${avg_approved:>17,.2f} ${avg_original:>17,.2f} ${avg_projected:>17,.2f}")
        
        print("-" * 95)
        overall_avg_approved = total_approved_all / total_projects_all if total_projects_all > 0 else 0
        overall_avg_original = total_original_all / total_projects_all if total_projects_all > 0 else 0
        overall_avg_projected = total_projected_all / total_projects_all if total_projects_all > 0 else 0
        print(f"{'OVERALL AVERAGE':<25} {total_projects_all:>10,} ${overall_avg_approved:>17,.2f} ${overall_avg_original:>17,.2f} ${overall_avg_projected:>17,.2f}")
        
        print(f"\nOverall Summary:")
        print(f"  Total Projects with Budgets: {total_projects_all:,}")
        print(f"  Overall Avg Total Approved Budget: ${overall_avg_approved:,.2f}")
        print(f"  Overall Avg Original Budget: ${overall_avg_original:,.2f}")
        print(f"  Overall Avg Projected Budget: ${overall_avg_projected:,.2f}")
        
        # 3. Breakdown by budgetitemdescription
        print(f"\n{'=' * 80}")
        print("3. BUDGET BREAKDOWN BY BUDGET ITEM DESCRIPTION")
        print("-" * 80)
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                bd.budgetitemdescription,
                COUNT(DISTINCT bd.projectidentifier) as project_count,
                COUNT(DISTINCT bd.budgetidentifier) as budget_count,
                COUNT(*) as record_count,
                AVG(bd.totalbudgetcostamount) as avg_cost,
                SUM(bd.totalbudgetcostamount) as total_cost,
                MIN(bd.totalbudgetcostamount) as min_cost,
                MAX(bd.totalbudgetcostamount) as max_cost
            FROM work_dynamics.curated.budgetdetail bd
            INNER JOIN work_dynamics.curated.project p
                ON bd.projectidentifier = p.id
            WHERE bd.sourcesystem = 'ingenious'
            AND p.sourcesystem = 'ingenious'
            AND bd.projectidentifier IS NOT NULL
            AND p.phasetext IS NOT NULL
            AND LOWER(p.phasetext) NOT IN ('requested', 'cancelled', 'draft')
            AND bd.budgetitemdescription IS NOT NULL
            AND bd.totalbudgetcostamount IS NOT NULL
            AND bd.totalbudgetcostamount > 0
            GROUP BY bd.budgetitemdescription
            ORDER BY total_cost DESC
        """)
        results = cursor.fetchall()
        cursor.close()
        
        if results and len(results) > 0:
            print(f"\n{'Budget Item Description':<60} {'Projects':>10} {'Budgets':>10} {'Records':>12} {'Total Cost':>20} {'Avg Cost':>18}")
            print("-" * 135)
            
            budgetitem_data = []
            for row in results:
                if hasattr(row, '__getitem__') and len(row) >= 8:
                    item_desc = row[0] if row[0] else 'NULL'
                    project_count = row[1]
                    budget_count = row[2]
                    record_count = row[3]
                    avg_cost = row[4] if row[4] else 0
                    total_cost = row[5] if row[5] else 0
                    min_cost = row[6] if row[6] else 0
                    max_cost = row[7] if row[7] else 0
                    
                    budgetitem_data.append({
                        'budgetitemdescription': item_desc,
                        'project_count': project_count,
                        'budget_count': budget_count,
                        'record_count': record_count,
                        'total_cost': total_cost,
                        'avg_cost': avg_cost,
                        'min_cost': min_cost,
                        'max_cost': max_cost
                    })
                    
                    # Truncate long descriptions for display
                    display_desc = item_desc[:58] if len(item_desc) <= 58 else item_desc[:55] + '...'
                    print(f"{display_desc:<60} {project_count:>10,} {budget_count:>10,} {record_count:>12,} ${total_cost:>19,.2f} ${avg_cost:>17,.2f}")
            
            print(f"\nTotal Budget Item Descriptions: {len(budgetitem_data)}")
        else:
            print("\n  ⚠ No budget item descriptions found (all NULL)")
            budgetitem_data = []
        
        # Compile final results
        final_results = {
            'analysis_date': 'current',
            'source_system': 'ingenious',
            'excluded_statuses': ['requested', 'cancelled', 'draft'],
            'budget_count_by_status': budget_count_data,
            'project_budget_averages': {
                'by_status': project_budget_data,
                'overall': {
                    'total_projects': total_projects_all,
                    'avg_totalapprovedbudgetamount': overall_avg_approved,
                    'avg_originalbudgetamount': overall_avg_original,
                    'avg_totalprojectedbudget': overall_avg_projected
                }
            },
            'budget_breakdown_by_item': budgetitem_data
        }
        
        # Save results
        with open('INGENIOUS_BUDGETS_PROJECT_LEVEL.json', 'w') as f:
            json.dump(final_results, f, indent=2, default=str)
        print(f"\n✓ Results saved to: INGENIOUS_BUDGETS_PROJECT_LEVEL.json")
        
        # Create markdown report
        create_project_level_report(final_results)
        
        return final_results
    
    finally:
        conn.close()

def create_project_level_report(results):
    """Create markdown report"""
    report = f"""# Ingenious Projects - Project-Level Budget Analysis

## Summary

**Analysis Date**: {results['analysis_date']}  
**Source System**: {results['source_system']}  
**Excluded Statuses**: {', '.join(results['excluded_statuses'])}

---

## 1. Budget Count per Project by Status

This shows how many distinct budgets exist per project, grouped by project status.

| Status | Projects | Distinct Budgets | Total Records | Avg Budgets per Project |
|--------|----------|------------------|---------------|------------------------|
"""
    
    for item in results['budget_count_by_status']:
        report += f"| {item['status']} | {item['project_count']:,} | {item['distinct_budget_count']:,} | {item['total_budget_records']:,} | {item['avg_budgets_per_project']:.2f} |\n"
    
    report += "\n---\n\n## 2. Average Budget Amounts per Project (from project table)\n\n"
    report += "**Note**: Only includes projects with budgets (originalbudgetamount IS NOT NULL)\n\n"
    report += "| Status | Projects | Avg Total Approved | Avg Original Budget | Avg Projected Budget |\n"
    report += "|--------|----------|-------------------|---------------------|----------------------|\n"
    
    for item in results['project_budget_averages']['by_status']:
        report += f"| {item['status']} | {item['project_count']:,} | ${item['avg_totalapprovedbudgetamount']:,.2f} | ${item['avg_originalbudgetamount']:,.2f} | ${item['avg_totalprojectedbudget']:,.2f} |\n"
    
    overall = results['project_budget_averages']['overall']
    report += f"| **OVERALL** | **{overall['total_projects']:,}** | **${overall['avg_totalapprovedbudgetamount']:,.2f}** | **${overall['avg_originalbudgetamount']:,.2f}** | **${overall['avg_totalprojectedbudget']:,.2f}** |\n"
    
    report += "\n---\n\n## 3. Budget Breakdown by Budget Item Description\n\n"
    report += "| Budget Item Description | Projects | Budgets | Records | Total Cost | Avg Cost |\n"
    report += "|-------------------------|----------|---------|---------|------------|----------|\n"
    
    for item in results['budget_breakdown_by_item'][:50]:  # Top 50
        item_desc = item['budgetitemdescription'].replace('|', '-') if item.get('budgetitemdescription') else 'NULL'
        # Escape markdown special characters
        item_desc = item_desc.replace('\n', ' ').replace('\r', ' ')
        report += f"| {item_desc} | {item['project_count']:,} | {item['budget_count']:,} | {item['record_count']:,} | ${item['total_cost']:,.2f} | ${item['avg_cost']:,.2f} |\n"
    
    report += "\n---\n\n*Report generated from INGENIOUS_BUDGETS_PROJECT_LEVEL.json*\n"
    
    with open('INGENIOUS_BUDGETS_PROJECT_LEVEL_REPORT.md', 'w') as f:
        f.write(report)
    
    print(f"✓ Markdown report saved to: INGENIOUS_BUDGETS_PROJECT_LEVEL_REPORT.md")

if __name__ == "__main__":
    analyze_ingenious_budgets_project_level()
