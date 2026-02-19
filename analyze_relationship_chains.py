#!/usr/bin/env python3
"""
Analyze relationship chains and secondary relationships
Example: inspection -> projectsites (via propertyidentifier) -> project (via projectidentifier)
"""

import json
from collections import defaultdict

def load_schema():
    """Load the ER schema JSON"""
    with open('INGENIOUS_CURATED_VIEWS_ER_SCHEMA.json', 'r') as f:
        return json.load(f)

def load_relationships():
    """Load all identified relationships"""
    with open('INGENIOUS_ALL_RELATIONSHIPS.json', 'r') as f:
        return json.load(f)

def analyze_relationship_chains():
    """Find relationship chains and secondary relationships"""
    schema = load_schema()
    rel_data = load_relationships()
    
    views = schema['views']
    all_relationships = rel_data['relationships']
    
    # Build view column index
    view_columns = {}
    for view_info in views:
        view_name = view_info['table_name'].replace('vw_ingenious_', '')
        view_columns[view_name] = {}
        for col in view_info.get('columns', []):
            view_columns[view_name][col['name'].lower()] = col
    
    print("=" * 80)
    print("Relationship Chain Analysis")
    print("=" * 80)
    print()
    
    # Build relationship graph
    rel_graph = defaultdict(list)  # to_view -> [(from_view, from_column, to_column), ...]
    for rel in all_relationships:
        rel_graph[rel['to_view']].append({
            'from_view': rel['from_view'],
            'from_column': rel['from_column'],
            'to_column': rel['to_column'],
            'pattern': rel['pattern'],
            'confidence': rel['confidence']
        })
    
    # Find relationship chains
    print("Finding relationship chains...")
    print("-" * 80)
    
    chains = []
    
    # Example: inspection -> projectsites -> project
    # Find views that link to intermediate views that then link to project
    for rel in all_relationships:
        from_view = rel['from_view']
        to_view = rel['to_view']
        
        # If this relationship doesn't go directly to project, check if target links to project
        if to_view != 'project' and to_view in rel_graph:
            # Check if target view has relationships to project
            target_to_project = [r for r in rel_graph.get('project', []) 
                                if r['from_view'] == to_view]
            
            if target_to_project:
                # Found a chain: from_view -> to_view -> project
                chain_rel = target_to_project[0]
                chains.append({
                    'from_view': from_view,
                    'intermediate_view': to_view,
                    'to_view': 'project',
                    'from_column': rel['from_column'],
                    'intermediate_column': chain_rel['from_column'],
                    'to_column': 'id',
                    'chain_type': 'two_hop_to_project',
                    'confidence': 'medium'
                })
    
    # Find other multi-hop relationships
    print("\nFinding other multi-hop relationships...")
    print("-" * 80)
    
    # Build reverse graph (from_view -> [(to_view, ...), ...])
    reverse_graph = defaultdict(list)
    for rel in all_relationships:
        reverse_graph[rel['from_view']].append(rel['to_view'])
    
    # Find paths between any two views (up to 2 hops)
    for start_view in view_columns.keys():
        for end_view in view_columns.keys():
            if start_view != end_view:
                # Check direct relationship
                direct = [r for r in all_relationships 
                         if r['from_view'] == start_view and r['to_view'] == end_view]
                
                # Check 2-hop relationship
                if not direct and start_view in reverse_graph:
                    intermediates = reverse_graph[start_view]
                    for intermediate in intermediates:
                        if intermediate in reverse_graph:
                            if end_view in reverse_graph[intermediate]:
                                # Found 2-hop path
                                hop1 = [r for r in all_relationships 
                                       if r['from_view'] == start_view and r['to_view'] == intermediate][0]
                                hop2 = [r for r in all_relationships 
                                       if r['from_view'] == intermediate and r['to_view'] == end_view][0]
                                
                                chains.append({
                                    'from_view': start_view,
                                    'intermediate_view': intermediate,
                                    'to_view': end_view,
                                    'from_column': hop1['from_column'],
                                    'intermediate_column': hop2['from_column'],
                                    'to_column': hop2['to_column'],
                                    'chain_type': 'two_hop',
                                    'confidence': 'low'
                                })
    
    # Print chains
    print(f"\nFound {len(chains)} relationship chains")
    print()
    
    # Group by chain type
    by_type = defaultdict(list)
    for chain in chains:
        by_type[chain['chain_type']].append(chain)
    
    print("Chains to Project (via intermediate view):")
    print("-" * 80)
    for chain in by_type.get('two_hop_to_project', []):
        print(f"  {chain['from_view']:30} -> {chain['intermediate_view']:30} -> {chain['to_view']}")
        print(f"    via: {chain['from_column']} -> {chain['intermediate_column']}")
        print()
    
    # Add all relationships (direct + chains) to final list
    final_relationships = []
    
    # Add all direct relationships
    for rel in all_relationships:
        final_relationships.append({
            'from_view': rel['from_view'],
            'from_column': rel['from_column'],
            'to_view': rel['to_view'],
            'to_column': rel['to_column'],
            'relationship_type': 'direct',
            'pattern': rel['pattern'],
            'confidence': rel['confidence']
        })
    
    # Add chain relationships (as indirect relationships)
    for chain in chains:
        if chain['chain_type'] == 'two_hop_to_project':
            # Add as indirect relationship
            final_relationships.append({
                'from_view': chain['from_view'],
                'from_column': chain['from_column'],
                'to_view': chain['to_view'],
                'to_column': chain['to_column'],
                'relationship_type': 'indirect_via',
                'intermediate_view': chain['intermediate_view'],
                'intermediate_column': chain['intermediate_column'],
                'confidence': chain['confidence']
            })
    
    # Summary
    print("=" * 80)
    print("FINAL RELATIONSHIP SUMMARY")
    print("=" * 80)
    print(f"\nTotal Direct Relationships: {len(all_relationships)}")
    print(f"Total Indirect Relationships (chains): {len(chains)}")
    print(f"Total Relationships (direct + indirect): {len(final_relationships)}")
    
    # Group by target
    by_target = defaultdict(list)
    for rel in final_relationships:
        by_target[rel['to_view']].append(rel)
    
    print("\nRelationships by Target Entity:")
    print("-" * 80)
    for target in sorted(by_target.keys()):
        direct_count = len([r for r in by_target[target] if r['relationship_type'] == 'direct'])
        indirect_count = len([r for r in by_target[target] if r['relationship_type'] == 'indirect_via'])
        print(f"  {target:30}: {direct_count} direct, {indirect_count} indirect")
    
    # Save enhanced relationships
    output = {
        'total_relationships': len(final_relationships),
        'direct_relationships': len(all_relationships),
        'indirect_relationships': len(chains),
        'relationships': final_relationships,
        'chains': chains
    }
    
    with open('INGENIOUS_ENHANCED_RELATIONSHIPS.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Enhanced relationships saved to: INGENIOUS_ENHANCED_RELATIONSHIPS.json")
    
    return final_relationships

if __name__ == "__main__":
    analyze_relationship_chains()







