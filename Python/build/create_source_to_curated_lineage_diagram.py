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
Create visual lineage diagram from source system to curated schema
Based on naming patterns and known source system tables
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from collections import defaultdict

def load_source_schema():
    """Load source system schema"""
    with open('INGENIOUS_ER_SCHEMA.json', 'r') as f:
        return json.load(f)

def infer_lineage_mapping():
    """Infer lineage mapping based on table names"""
    source_schema = load_source_schema()
    
    # Get source system tables (remove _backup suffix for matching)
    source_tables = {}
    for table_info in source_schema['tables']:
        table_name = table_info['table_name']
        if table_name.endswith('_backup'):
            clean_name = table_name.replace('_backup', '')
            source_tables[clean_name] = table_name
        elif not any(t.startswith(table_name) and t != table_name for t in source_schema['tables']):
            source_tables[table_name] = table_name
    
    # Known curated table names (from our analysis)
    curated_tables = [
        'answer', 'budgetchange', 'budgetdetail', 'businessunit', 'commitment',
        'commitmentchanges', 'directorycontactprojectlnk', 'generictask', 'inspection',
        'inspectionmembers', 'inspectiontemplates', 'locations', 'milestone', 'program',
        'project', 'projectadditionalcustomfield', 'projectsites', 'projectstatsindicator',
        'punchitemmember', 'punchlistitem', 'risk', 'riskcontact', 'riskmembers',
        'users', 'workitem'
    ]
    
    # Map curated to source
    lineage = {}
    for curated_table in curated_tables:
        # Try to find matching source table
        # Pattern 1: exact match
        if curated_table in source_tables:
            lineage[curated_table] = {
                'source_table': source_tables[curated_table],
                'confidence': 'high'
            }
        # Pattern 2: with ingenious_ prefix
        elif f'ingenious_{curated_table}' in source_tables:
            lineage[curated_table] = {
                'source_table': source_tables[f'ingenious_{curated_table}'],
                'confidence': 'high'
            }
        # Pattern 3: with _backup suffix
        elif f'ingenious_{curated_table}_backup' in [t for t in source_schema['tables']]:
            lineage[curated_table] = {
                'source_table': f'ingenious_{curated_table}_backup',
                'confidence': 'high'
            }
        else:
            # Try partial matches
            for source_name, source_full in source_tables.items():
                if curated_table.lower() in source_name.lower() or source_name.lower() in curated_table.lower():
                    lineage[curated_table] = {
                        'source_table': source_full,
                        'confidence': 'medium'
                    }
                    break
    
    return lineage, source_tables

def create_lineage_diagram():
    """Create visual lineage diagram"""
    lineage, source_tables = infer_lineage_mapping()
    
    print("=" * 80)
    print("Creating Source-to-Curated Lineage Diagram")
    print("=" * 80)
    print()
    
    # Create graph
    G = nx.DiGraph()
    
    # Add source system nodes
    source_nodes = set()
    for curated_table, mapping in lineage.items():
        source_table = mapping['source_table']
        source_nodes.add(source_table)
        G.add_node(source_table, node_type='source', table_name=source_table)
    
    # Add curated schema nodes
    curated_nodes = set()
    for curated_table in lineage.keys():
        curated_nodes.add(curated_table)
        G.add_node(curated_table, node_type='curated', table_name=curated_table)
    
    # Add edges
    for curated_table, mapping in lineage.items():
        source_table = mapping['source_table']
        G.add_edge(source_table, curated_table, 
                  confidence=mapping['confidence'])
    
    print(f"Source tables: {len(source_nodes)}")
    print(f"Curated tables: {len(curated_nodes)}")
    print(f"Lineage relationships: {len(G.edges())}")
    print()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(30, 20))
    
    # Create hierarchical layout
    pos = {}
    
    # Position source tables on left
    source_list = sorted(list(source_nodes))
    y_start = 10
    y_step = 0.5
    for i, node in enumerate(source_list):
        pos[node] = (-15, y_start - i * y_step)
    
    # Position curated tables on right
    curated_list = sorted(list(curated_nodes))
    for i, node in enumerate(curated_list):
        pos[node] = (15, y_start - i * y_step)
    
    # Color nodes
    node_colors = []
    node_sizes = []
    for node in G.nodes():
        if G.nodes[node]['node_type'] == 'source':
            node_colors.append('#FF6B6B')  # Red for source
            node_sizes.append(3000)
        else:
            node_colors.append('#4ECDC4')  # Teal for curated
            node_sizes.append(3000)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, alpha=0.9, ax=ax, 
                          linewidths=2, edgecolors='black')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='#666666', 
                           arrows=True, arrowsize=25, alpha=0.6, 
                           width=2, ax=ax)
    
    # Draw labels (shortened for readability)
    labels = {}
    for node in G.nodes():
        # Shorten long names
        if len(node) > 25:
            if node.startswith('ingenious_'):
                short_name = node.replace('ingenious_', '').replace('_backup', '')
            else:
                short_name = node[:22] + '...'
            labels[node] = short_name
        else:
            labels[node] = node
    
    nx.draw_networkx_labels(G, pos, labels, font_size=8, 
                           font_weight='bold', ax=ax)
    
    # Add title and legend
    ax.set_title('Ingenious Source System to Curated Schema Lineage', 
                 fontsize=24, fontweight='bold', pad=20)
    
    # Add section labels
    ax.text(-15, y_start + 2, 'Source System\n(edp_sourcesystem.ingenious)', 
            fontsize=16, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
    
    ax.text(15, y_start + 2, 'Curated Schema\n(work_dynamics.curated)', 
            fontsize=16, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Create legend
    legend_elements = [
        mpatches.Patch(facecolor='#FF6B6B', label='Source System Tables'),
        mpatches.Patch(facecolor='#4ECDC4', label='Curated Schema Tables'),
        plt.Line2D([0], [0], color='#666666', linewidth=2, label='Data Flow')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=14, framealpha=0.95)
    
    # Add statistics
    stats_text = f"Source Tables: {len(source_nodes)}\n"
    stats_text += f"Curated Tables: {len(curated_nodes)}\n"
    stats_text += f"Lineage Relationships: {len(G.edges())}"
    
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes,
            fontsize=12, verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save high-resolution PNG
    plt.savefig('INGENIOUS_SOURCE_TO_CURATED_LINEAGE_DIAGRAM.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("✓ Lineage diagram saved to: INGENIOUS_SOURCE_TO_CURATED_LINEAGE_DIAGRAM.png")
    
    plt.close()
    
    # Also create a summary table
    print("\n" + "=" * 80)
    print("Lineage Mapping Summary")
    print("=" * 80)
    print()
    print(f"{'Curated Table':<35} {'Source Table':<50} {'Confidence'}")
    print("-" * 100)
    for curated_table in sorted(lineage.keys()):
        mapping = lineage[curated_table]
        source_table = mapping['source_table']
        confidence = mapping['confidence']
        print(f"{curated_table:<35} {source_table:<50} {confidence}")

if __name__ == "__main__":
    create_lineage_diagram()







