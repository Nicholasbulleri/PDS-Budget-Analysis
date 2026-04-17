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
Create a high-quality PNG ER diagram for Ingenious curated views
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

def create_enhanced_er_diagram():
    """Create an enhanced ER diagram PNG"""
    schema = load_schema()
    views = schema['views']
    relationships = schema['relationships']
    
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
            'has_project_link': False
        }
    
    # Add edges from explicit relationships
    seen_relationships = set()
    for rel in relationships:
        from_view = rel['from_table'].replace('vw_ingenious_', '')
        to_view = rel['to_table'].replace('vw_ingenious_', '')
        
        if from_view in view_metadata and to_view in view_metadata:
            rel_key = (from_view, to_view)
            if rel_key not in seen_relationships:
                seen_relationships.add(rel_key)
                G.add_edge(from_view, to_view, label=rel['from_column'])
                if to_view == 'project':
                    view_metadata[from_view]['has_project_link'] = True
    
    # Add inferred relationships based on projectidentifier columns
    project_views = {}
    for view_name, view_info in valid_views.items():
        clean_name = view_name.replace('vw_ingenious_', '')
        for col in view_info['columns']:
            col_name = col['name'].lower()
            if 'projectidentifier' in col_name or col_name == 'projectid' or col_name == 'project':
                if clean_name not in project_views and clean_name != 'project':
                    project_views[clean_name] = col['name']
                    view_metadata[clean_name]['has_project_link'] = True
    
    # Link to project view if it exists
    if 'project' in view_metadata:
        for view_name, project_col in project_views.items():
            rel_key = (view_name, 'project')
            if rel_key not in seen_relationships:
                seen_relationships.add(rel_key)
                G.add_edge(view_name, 'project', label=project_col)
    
    # Create figure with better sizing
    fig, ax = plt.subplots(figsize=(28, 20))
    
    # Use hierarchical layout with project at center
    if 'project' in G.nodes():
        # Position project at center
        pos = {}
        project_pos = (0, 0)
        pos['project'] = project_pos
        
        # Position other nodes around project
        other_nodes = [n for n in G.nodes() if n != 'project']
        
        # Use spring layout for non-project nodes
        if len(other_nodes) > 0:
            subgraph = G.subgraph(other_nodes)
            if len(subgraph.edges()) > 0:
                sub_pos = nx.spring_layout(subgraph, k=8, iterations=100, seed=42)
                # Scale and position around project
                for node, (x, y) in sub_pos.items():
                    pos[node] = (x * 12, y * 10)
            else:
                # Circular layout if no edges
                import math
                angle_step = 2 * math.pi / len(other_nodes)
                radius = 12
                for i, node in enumerate(other_nodes):
                    angle = i * angle_step
                    pos[node] = (radius * math.cos(angle), radius * math.sin(angle))
    else:
        pos = nx.spring_layout(G, k=6, iterations=100, seed=42)
    
    # Color nodes by category
    node_colors = []
    for node in G.nodes():
        if node == 'project':
            node_colors.append('#FF6B6B')  # Red for project
        elif view_metadata[node]['has_project_link']:
            node_colors.append('#4ECDC4')  # Teal for project-linked views
        else:
            node_colors.append('#95E1D3')  # Light teal for other views
    
    # Draw nodes with size based on row count
    node_sizes = []
    for node in G.nodes():
        row_count = view_metadata[node]['row_count']
        if row_count > 100000:
            size = 5000
        elif row_count > 10000:
            size = 3000
        elif row_count > 1000:
            size = 2000
        else:
            size = 1500
        node_sizes.append(size)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, alpha=0.9, ax=ax)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='#666666', 
                           arrows=True, arrowsize=25, alpha=0.5, 
                           width=2, ax=ax, connectionstyle='arc3,rad=0.1')
    
    # Draw labels with better formatting
    labels = {}
    for node in G.nodes():
        row_count = view_metadata[node]['row_count']
        col_count = view_metadata[node]['column_count']
        if row_count > 0:
            labels[node] = f"{node}\n({row_count:,} rows)"
        else:
            labels[node] = node
    
    nx.draw_networkx_labels(G, pos, labels, font_size=10, 
                           font_weight='bold', ax=ax)
    
    # Draw edge labels (only for project relationships)
    edge_labels = {}
    for (u, v, d) in G.edges(data=True):
        if v == 'project' and 'label' in d:
            edge_labels[(u, v)] = d['label']
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, 
                                 bbox=dict(boxstyle='round,pad=0.3', 
                                          facecolor='white', alpha=0.7), ax=ax)
    
    # Add title and legend
    ax.set_title('Ingenious Curated Consumption Views - Entity Relationship Diagram', 
                 fontsize=24, fontweight='bold', pad=20)
    
    # Create legend
    legend_elements = [
        mpatches.Patch(facecolor='#FF6B6B', label='Project (Central Entity)'),
        mpatches.Patch(facecolor='#4ECDC4', label='Views Linked to Project'),
        mpatches.Patch(facecolor='#95E1D3', label='Other Views'),
        plt.Line2D([0], [0], color='#666666', linewidth=2, label='Relationship')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=12, framealpha=0.9)
    
    # Add statistics text box
    stats_text = f"Total Views: {len(valid_views)}\n"
    stats_text += f"Total Relationships: {len(G.edges())}\n"
    stats_text += f"Total Rows: {sum(v['row_count'] or 0 for v in valid_views.values()):,}"
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save high-resolution PNG
    plt.savefig('INGENIOUS_CURATED_VIEWS_ER_DIAGRAM.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ High-resolution PNG saved to: INGENIOUS_CURATED_VIEWS_ER_DIAGRAM.png")
    
    plt.close()

if __name__ == "__main__":
    print("=" * 80)
    print("Creating Enhanced ER Diagram PNG")
    print("=" * 80)
    print()
    create_enhanced_er_diagram()
    print("\nDiagram created successfully!")







