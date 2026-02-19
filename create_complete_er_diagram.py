#!/usr/bin/env python3
"""
Create a complete ER diagram with all relationships including indirect chains
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from collections import defaultdict

def load_schema():
    """Load the ER schema JSON"""
    with open('INGENIOUS_CURATED_VIEWS_ER_SCHEMA.json', 'r') as f:
        return json.load(f)

def load_enhanced_relationships():
    """Load enhanced relationships including chains"""
    try:
        with open('INGENIOUS_ENHANCED_RELATIONSHIPS.json', 'r') as f:
            return json.load(f)
    except:
        # Fallback to basic relationships
        with open('INGENIOUS_ALL_RELATIONSHIPS.json', 'r') as f:
            data = json.load(f)
            return {
                'relationships': data['relationships'],
                'chains': []
            }

def create_complete_er_diagram():
    """Create ER diagram with all relationships"""
    schema = load_schema()
    rel_data = load_enhanced_relationships()
    
    views = schema['views']
    all_relationships = rel_data['relationships']
    chains = rel_data.get('chains', [])
    
    # Filter to only views with data
    valid_views = {v['table_name']: v for v in views if v['columns']}
    
    # Create graph
    G = nx.DiGraph()
    
    # Add nodes with metadata
    view_metadata = {}
    for view_name, view_info in valid_views.items():
        clean_name = view_name.replace('vw_ingenious_', '')
        G.add_node(clean_name)
        view_metadata[clean_name] = {
            'row_count': view_info.get('row_count', 0) or 0,
            'column_count': len(view_info.get('columns', [])),
            'has_project_link': False,
            'has_indirect_project_link': False
        }
    
    # Add direct relationships
    seen_edges = set()
    for rel in all_relationships:
        from_view = rel['from_view']
        to_view = rel['to_view']
        
        edge_key = (from_view, to_view)
        if edge_key not in seen_edges:
            seen_edges.add(edge_key)
            G.add_edge(from_view, to_view, 
                      label=rel.get('from_column', ''),
                      rel_type='direct',
                      confidence=rel.get('confidence', 'medium'))
            
            if to_view == 'project':
                view_metadata[from_view]['has_project_link'] = True
    
    # Add important indirect relationships (chains to project)
    for chain in chains:
        if chain.get('chain_type') == 'two_hop_to_project':
            from_view = chain['from_view']
            intermediate = chain['intermediate_view']
            to_view = chain['to_view']  # should be 'project'
            
            # Add edge from source to intermediate (if not already there)
            edge_key1 = (from_view, intermediate)
            if edge_key1 not in seen_edges:
                seen_edges.add(edge_key1)
                G.add_edge(from_view, intermediate,
                          label=chain['from_column'],
                          rel_type='direct',
                          confidence='high')
            
            # Mark indirect project link
            if to_view == 'project':
                view_metadata[from_view]['has_indirect_project_link'] = True
    
    # Create figure with better sizing
    fig, ax = plt.subplots(figsize=(32, 24))
    
    # Use hierarchical layout with project at center
    if 'project' in G.nodes():
        # Position project at center
        pos = {}
        project_pos = (0, 0)
        pos['project'] = project_pos
        
        # Categorize nodes by relationship type
        direct_project_nodes = []
        indirect_project_nodes = []
        other_nodes = []
        
        for node in G.nodes():
            if node == 'project':
                continue
            if view_metadata[node]['has_project_link']:
                direct_project_nodes.append(node)
            elif view_metadata[node]['has_indirect_project_link']:
                indirect_project_nodes.append(node)
            else:
                other_nodes.append(node)
        
        # Position direct project links in inner ring
        import math
        if direct_project_nodes:
            angle_step = 2 * math.pi / len(direct_project_nodes)
            radius1 = 8
            for i, node in enumerate(direct_project_nodes):
                angle = i * angle_step
                pos[node] = (radius1 * math.cos(angle), radius1 * math.sin(angle))
        
        # Position indirect project links in middle ring
        if indirect_project_nodes:
            angle_step = 2 * math.pi / len(indirect_project_nodes)
            radius2 = 14
            for i, node in enumerate(indirect_project_nodes):
                angle = i * angle_step
                pos[node] = (radius2 * math.cos(angle), radius2 * math.sin(angle))
        
        # Position other nodes in outer ring
        if other_nodes:
            angle_step = 2 * math.pi / len(other_nodes)
            radius3 = 20
            for i, node in enumerate(other_nodes):
                angle = i * angle_step
                pos[node] = (radius3 * math.cos(angle), radius3 * math.sin(angle))
    else:
        pos = nx.spring_layout(G, k=8, iterations=100, seed=42)
    
    # Color nodes by category
    node_colors = []
    for node in G.nodes():
        if node == 'project':
            node_colors.append('#FF6B6B')  # Red for project
        elif view_metadata[node]['has_project_link']:
            node_colors.append('#4ECDC4')  # Teal for direct project links
        elif view_metadata[node]['has_indirect_project_link']:
            node_colors.append('#95E1D3')  # Light teal for indirect project links
        else:
            node_colors.append('#FFE66D')  # Yellow for other views
    
    # Draw nodes with size based on row count
    node_sizes = []
    for node in G.nodes():
        row_count = view_metadata[node]['row_count']
        if row_count > 100000:
            size = 6000
        elif row_count > 10000:
            size = 4000
        elif row_count > 1000:
            size = 2500
        else:
            size = 1500
        node_sizes.append(size)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, alpha=0.9, ax=ax, linewidths=2, edgecolors='black')
    
    # Separate edges by type
    direct_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('rel_type') == 'direct']
    
    # Draw edges - use different styles for project links
    project_edges = []
    other_edges = []
    
    for u, v in G.edges():
        if v == 'project' or u == 'project':
            project_edges.append((u, v))
        else:
            other_edges.append((u, v))
    
    # Draw project edges in bold
    if project_edges:
        nx.draw_networkx_edges(G, pos, edgelist=project_edges, 
                              edge_color='#FF6B6B', arrows=True, arrowsize=30, 
                              alpha=0.7, width=3, ax=ax, connectionstyle='arc3,rad=0.1')
    
    # Draw other edges
    if other_edges:
        nx.draw_networkx_edges(G, pos, edgelist=other_edges, 
                              edge_color='#666666', arrows=True, arrowsize=20, 
                              alpha=0.4, width=1.5, ax=ax, connectionstyle='arc3,rad=0.1')
    
    # Draw labels
    labels = {}
    for node in G.nodes():
        row_count = view_metadata[node]['row_count']
        if row_count > 0:
            labels[node] = f"{node}\n({row_count:,})"
        else:
            labels[node] = node
    
    nx.draw_networkx_labels(G, pos, labels, font_size=11, 
                           font_weight='bold', ax=ax)
    
    # Draw edge labels for key relationships
    edge_labels = {}
    for (u, v, d) in G.edges(data=True):
        if 'label' in d and d['label']:
            # Show labels for project relationships and important chains
            if v == 'project' or (u in ['inspection', 'projectsites'] and v in ['inspection', 'projectsites', 'project']):
                label = d['label']
                if len(label) > 25:
                    label = label[:22] + '...'
                edge_labels[(u, v)] = label
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, 
                                 bbox=dict(boxstyle='round,pad=0.3', 
                                          facecolor='white', alpha=0.8), ax=ax)
    
    # Add title and legend
    ax.set_title('Ingenious Curated Consumption Views - Complete ER Diagram\n(All Relationships Including Indirect Chains)', 
                 fontsize=26, fontweight='bold', pad=25)
    
    # Create legend
    legend_elements = [
        mpatches.Patch(facecolor='#FF6B6B', label='Project (Central Entity)'),
        mpatches.Patch(facecolor='#4ECDC4', label='Direct Project Links'),
        mpatches.Patch(facecolor='#95E1D3', label='Indirect Project Links (via intermediate)'),
        mpatches.Patch(facecolor='#FFE66D', label='Other Views'),
        plt.Line2D([0], [0], color='#FF6B6B', linewidth=3, label='Project Relationships'),
        plt.Line2D([0], [0], color='#666666', linewidth=1.5, label='Other Relationships')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=13, framealpha=0.95)
    
    # Add statistics text box
    direct_project = len([v for v in view_metadata.values() if v['has_project_link']])
    indirect_project = len([v for v in view_metadata.values() if v['has_indirect_project_link']])
    
    stats_text = f"Total Views: {len(valid_views)}\n"
    stats_text += f"Total Relationships: {len(G.edges())}\n"
    stats_text += f"Direct Project Links: {direct_project}\n"
    stats_text += f"Indirect Project Links: {indirect_project}\n"
    stats_text += f"Total Rows: {sum(v['row_count'] or 0 for v in valid_views.values()):,}"
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save high-resolution PNG
    plt.savefig('INGENIOUS_COMPLETE_ER_DIAGRAM.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Complete ER diagram saved to: INGENIOUS_COMPLETE_ER_DIAGRAM.png")
    
    plt.close()
    
    # Print summary
    print("\n" + "=" * 80)
    print("Diagram Summary")
    print("=" * 80)
    print(f"Total Views: {len(valid_views)}")
    print(f"Total Edges: {len(G.edges())}")
    print(f"Direct Project Links: {direct_project}")
    print(f"Indirect Project Links: {indirect_project}")
    print(f"Other Relationships: {len(G.edges()) - direct_project - indirect_project}")

if __name__ == "__main__":
    print("=" * 80)
    print("Creating Complete ER Diagram with All Relationships")
    print("=" * 80)
    print()
    create_complete_er_diagram()
    print("\n✓ Diagram created successfully!")

