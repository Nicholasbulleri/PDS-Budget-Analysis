#!/usr/bin/env python3
"""
Comprehensive analysis of EDP integrated systems
Analyzes the edp_sourcesystem catalog to identify all integrated systems
"""

from edp_connection import execute_query
from collections import defaultdict
import json

def get_all_source_systems():
    """Get all source systems from edp_sourcesystem catalog"""
    print("Fetching all source systems from edp_sourcesystem catalog...")
    
    cols, results = execute_query("""
        SHOW SCHEMAS IN edp_sourcesystem
    """)
    
    systems = sorted([row[0] for row in results])
    return systems


def check_system_has_data(system_name):
    """Check if a system has tables/data"""
    try:
        cols, results = execute_query(f"""
            SHOW TABLES IN edp_sourcesystem.{system_name}
        """)
        return len(results) > 0, len(results)
    except:
        return False, 0


def get_system_categories():
    """Categorize systems by type"""
    categories = {
        'Project Management': ['clarizen', 'ingenious', 'workfront', 'pega'],
        'CRM/Sales': ['salesforce', 'dssf', 'oval', 'crm365', 'eloqua', 'marketing_leads', 'leadgenius', 'zoominfo'],
        'Property/Facilities': ['corrigo', 'prism', 'tririga', 'archibus', 'yardi', 'vts', 'leasingos', 'mri', 'costar', 'reonomy'],
        'Finance/ERP': ['peoplesoft', 'netsuite', 'sage_intacct', 'e1', 'tm1', 'jll_finance', 'ffs'],
        'HR/People': ['workday', 'peoplesoft'],
        'Procurement/Vendor': ['jaggaer', 'aravo', 'avetta', 'isn'],
        'ESG/Sustainability': ['envizi', 'epc', 'esgmet', 'breeam'],
        'Research/Data': ['costar', 'reonomy', 'rca', 'str', 'preqin', 'debtinsight', 'definitive_healthcare'],
        'Analytics/BI': ['tableau', 'powerbi', 'alteryx', 'splunk', 'medallia', 'qualtrics'],
        'Collaboration': ['sharepoint', 'outlook', 'webex', 'zoom', 'teams', 'slack'],
        'Document Management': ['box', 'sharepoint'],
        'Customer Experience': ['medallia', 'qualtrics', 'totango', 'pendo'],
        'Compliance/Legal': ['legal', 'sec', 'fortify', 'cmo'],
        'Marketing': ['adobe_analytics', 'facebook', 'linkedin', 'twitter', 'sproutsocial', 'eloqua'],
        'Development/IT': ['github', 'service_now_tables', 'splunk', 'zendesk'],
        'Other/Unknown': []
    }
    return categories


def categorize_system(system_name, categories):
    """Categorize a system"""
    system_lower = system_name.lower()
    
    # Special cases with exact matches (now handled in categories, but kept for clarity)
    special_cases = {
        'dssf': 'CRM/Sales',  # Salesforce
        'ffs': 'Finance/ERP',  # APAC revenue forecasting system
        'cmo': 'Compliance/Legal',  # Legacy health and safety system
        'prism': 'Property/Facilities',  # Property management system
        'oval': 'CRM/Sales',  # Sales opportunity management tool (similar to Salesforce)
    }
    
    if system_lower in special_cases:
        return special_cases[system_lower]
    
    for category, systems in categories.items():
        for sys in systems:
            if sys in system_lower or system_lower in sys:
                return category
    return 'Other/Unknown'


def analyze_edp_systems():
    """Main analysis function"""
    print("=" * 70)
    print("EDP INTEGRATED SYSTEMS ANALYSIS")
    print("=" * 70)
    print()
    
    # Get all systems
    all_systems = get_all_source_systems()
    print(f"Total source systems found: {len(all_systems)}")
    print()
    
    # Categorize systems
    categories = get_system_categories()
    categorized = defaultdict(list)
    
    for system in all_systems:
        category = categorize_system(system, categories)
        categorized[category].append(system)
    
    # Display by category
    print("=" * 70)
    print("SYSTEMS BY CATEGORY")
    print("=" * 70)
    print()
    
    for category in sorted(categorized.keys()):
        systems = sorted(categorized[category])
        print(f"{category}: {len(systems)} systems")
        print("-" * 70)
        for i, system in enumerate(systems, 1):
            print(f"  {i:3}. {system}")
        print()
    
    # Summary statistics
    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print()
    print(f"Total Integrated Systems: {len(all_systems)}")
    print()
    print("Systems by Category:")
    for category in sorted(categorized.keys()):
        print(f"  {category:30} : {len(categorized[category]):3} systems")
    
    # Check which systems have data
    print()
    print("=" * 70)
    print("CHECKING SYSTEMS WITH DATA")
    print("=" * 70)
    print()
    
    systems_with_data = []
    systems_without_data = []
    
    # Sample check (checking first 20 to avoid timeout)
    print("Sampling systems to check for data (first 20)...")
    for system in all_systems[:20]:
        has_data, table_count = check_system_has_data(system)
        if has_data:
            systems_with_data.append((system, table_count))
            print(f"  ✓ {system:30} : {table_count:3} tables")
        else:
            systems_without_data.append(system)
            print(f"  ✗ {system:30} : No tables found")
    
    # Save results
    results = {
        'total_systems': len(all_systems),
        'systems': all_systems,
        'categorized': {k: v for k, v in categorized.items()},
        'systems_with_data_sample': [{'system': s, 'table_count': c} for s, c in systems_with_data],
        'systems_without_data_sample': systems_without_data
    }
    
    with open('edp_systems_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print()
    print(f"✓ Analysis saved to edp_systems_analysis.json")
    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    analyze_edp_systems()

