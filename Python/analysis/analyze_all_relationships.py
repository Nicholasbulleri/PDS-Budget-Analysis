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
Analyze all potential relationships in the curated views beyond just project links
"""

import json
from collections import defaultdict

def load_schema():
    """Load the ER schema JSON"""
    with open('INGENIOUS_CURATED_VIEWS_ER_SCHEMA.json', 'r') as f:
        return json.load(f)

def analyze_all_relationships():
    """Find all potential relationships"""
    schema = load_schema()
    views = schema['views']
    
    # Build index of all columns by name
    column_index = defaultdict(list)  # column_name -> [(view_name, column_info), ...]
    view_columns = {}  # view_name -> {column_name: column_info}
    
    for view_info in views:
        view_name = view_info['table_name']
        clean_name = view_name.replace('vw_ingenious_', '')
        view_columns[clean_name] = {}
        
        for col in view_info.get('columns', []):
            col_name = col['name'].lower()
            column_index[col_name].append((clean_name, col))
            view_columns[clean_name][col_name] = col
    
    print("=" * 80)
    print("Comprehensive Relationship Analysis")
    print("=" * 80)
    print()
    
    # Find all potential foreign key relationships
    relationships = []
    
    # Pattern 1: Columns ending with _id or _identifier
    print("Pattern 1: Columns ending with _id or _identifier")
    print("-" * 80)
    
    id_patterns = {}
    for view_name, cols in view_columns.items():
        for col_name, col_info in cols.items():
            if col_name.endswith('_id') or col_name.endswith('_identifier'):
                base_name = col_name.replace('_id', '').replace('_identifier', '')
                if base_name not in id_patterns:
                    id_patterns[base_name] = []
                id_patterns[base_name].append((view_name, col_name))
    
    # Look for matching views
    for base_name, occurrences in sorted(id_patterns.items()):
        if len(occurrences) > 1:
            # Check if there's a view that matches this base name
            matching_views = [v for v in view_columns.keys() if base_name in v.lower() or v.lower() in base_name]
            if matching_views:
                for view_name, col_name in occurrences:
                    for target_view in matching_views:
                        if view_name != target_view:
                            # Check if target view has an id column
                            target_id_cols = [c for c in view_columns[target_view].keys() 
                                            if c == 'id' or c.endswith('_id') or c.endswith('_identifier')]
                            if target_id_cols:
                                relationships.append({
                                    'from_view': view_name,
                                    'from_column': col_name,
                                    'to_view': target_view,
                                    'to_column': 'id',
                                    'pattern': 'id/identifier_match',
                                    'confidence': 'medium'
                                })
    
    # Pattern 2: Direct column name matches
    print("\nPattern 2: Direct column name matches to view names")
    print("-" * 80)
    
    for view_name, cols in view_columns.items():
        for col_name, col_info in cols.items():
            # Check if column name matches another view name
            for other_view in view_columns.keys():
                if other_view != view_name:
                    # Check various patterns
                    if col_name == other_view or \
                       col_name == f'{other_view}_id' or \
                       col_name == f'{other_view}identifier' or \
                       col_name == f'{other_view}_identifier':
                        # Check if target has id
                        target_id_cols = [c for c in view_columns[other_view].keys() 
                                        if c == 'id' or c.endswith('_id')]
                        if target_id_cols:
                            relationships.append({
                                'from_view': view_name,
                                'from_column': col_name,
                                'to_view': other_view,
                                'to_column': 'id',
                                'pattern': 'direct_name_match',
                                'confidence': 'high'
                            })
    
    # Pattern 3: Common relationship patterns
    print("\nPattern 3: Common relationship patterns")
    print("-" * 80)
    
    common_patterns = {
        'inspectionidentifier': 'inspection',
        'inspectiontemplateidentifier': 'inspectiontemplates',
        'surveytemplateidentifier': 'inspectiontemplates',
        'memberidentifier': ['inspectionmembers', 'riskmembers', 'punchitemmember'],
        'contactidentifier': ['riskcontact', 'directorycontactprojectlnk'],
        'riskidentifier': ['riskcontact', 'riskmembers'],
        'punchlistitemidentifier': 'punchitemmember',
        'workitemidentifier': 'workitem',
        'budgetidentifier': ['budgetdetail', 'budgetchange'],
        'commitmentidentifier': 'commitmentchanges',
        'programidentifier': 'program',
        'locationidentifier': 'locations',
        'businessunitidentifier': 'businessunit',
        'useridentifier': 'users',
        'companyidentifier': 'businessunit',
        'propertyidentifier': 'projectsites',
    }
    
    for col_pattern, target_views in common_patterns.items():
        if isinstance(target_views, str):
            target_views = [target_views]
        
        for view_name, cols in view_columns.items():
            for col_name, col_info in cols.items():
                if col_pattern in col_name.lower():
                    for target_view in target_views:
                        if target_view in view_columns and view_name != target_view:
                            relationships.append({
                                'from_view': view_name,
                                'from_column': col_name,
                                'to_view': target_view,
                                'to_column': 'id',
                                'pattern': 'common_pattern',
                                'confidence': 'high'
                            })
    
    # Remove duplicates
    seen = set()
    unique_relationships = []
    for rel in relationships:
        key = (rel['from_view'], rel['from_column'], rel['to_view'])
        if key not in seen:
            seen.add(key)
            unique_relationships.append(rel)
    
    # Group by relationship type
    print("\n" + "=" * 80)
    print("ALL IDENTIFIED RELATIONSHIPS")
    print("=" * 80)
    print()
    
    # Group by to_view
    by_target = defaultdict(list)
    for rel in unique_relationships:
        by_target[rel['to_view']].append(rel)
    
    for target_view in sorted(by_target.keys()):
        print(f"\n{target_view.upper()} (target entity):")
        print("-" * 80)
        for rel in sorted(by_target[target_view], key=lambda x: x['from_view']):
            print(f"  {rel['from_view']:35} -> {rel['from_column']:40} ({rel['pattern']}, {rel['confidence']})")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    print(f"\nTotal Relationships Found: {len(unique_relationships)}")
    print(f"Relationships to Project: {len([r for r in unique_relationships if r['to_view'] == 'project'])}")
    print(f"Other Relationships: {len([r for r in unique_relationships if r['to_view'] != 'project'])}")
    
    # Group by pattern
    by_pattern = defaultdict(list)
    for rel in unique_relationships:
        by_pattern[rel['pattern']].append(rel)
    
    print("\nBy Pattern Type:")
    for pattern, rels in sorted(by_pattern.items()):
        print(f"  {pattern:25}: {len(rels)} relationships")
    
    # Save to JSON
    output = {
        'total_relationships': len(unique_relationships),
        'relationships': unique_relationships,
        'summary': {
            'project_relationships': len([r for r in unique_relationships if r['to_view'] == 'project']),
            'other_relationships': len([r for r in unique_relationships if r['to_view'] != 'project'])
        }
    }
    
    with open('INGENIOUS_ALL_RELATIONSHIPS.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Detailed relationships saved to: INGENIOUS_ALL_RELATIONSHIPS.json")
    
    return unique_relationships

if __name__ == "__main__":
    analyze_all_relationships()







