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
Generate visual ER diagram from Ingenious ER schema JSON
Creates multiple formats: Mermaid diagram, Graphviz diagram, and NetworkX visualization
"""

import json
import os
from collections import defaultdict

def load_schema():
    """Load the ER schema JSON"""
    with open('INGENIOUS_ER_SCHEMA.json', 'r') as f:
        return json.load(f)

def generate_mermaid_diagram(schema):
    """Generate Mermaid ER diagram"""
    tables = schema['tables']
    relationships = schema['relationships']
    
    # Filter to only tables with data (non-empty columns)
    valid_tables = {t['table_name']: t for t in tables if t['columns']}
    
    # Group relationships by from_table
    rel_by_table = defaultdict(list)
    for rel in relationships:
        if rel['from_table'] in valid_tables and rel['to_table'] in valid_tables:
            rel_by_table[rel['from_table']].append(rel)
    
    # Focus on core tables (remove _backup suffix for cleaner diagram)
    core_tables = {}
    for table_name, table_info in valid_tables.items():
        # Use backup tables as primary, but show cleaner names
        if '_backup' in table_name:
            clean_name = table_name.replace('_backup', '')
            core_tables[clean_name] = table_info
        elif not any(t.startswith(table_name) and t != table_name for t in valid_tables.keys()):
            core_tables[table_name] = table_info
    
    # Build Mermaid ER diagram
    mermaid = "erDiagram\n"
    
    # Add entity definitions with key attributes
    for table_name, table_info in sorted(core_tables.items()):
        # Get primary key
        pk_cols = table_info.get('primary_keys', [])
        if not pk_cols:
            # Try to find id column
            for col in table_info['columns']:
                if col['name'].lower() in ['id', f'{table_name.lower()}_id']:
                    pk_cols = [col['name']]
                    break
        
        # Get a few key columns (limit to 5-6 for readability)
        key_cols = []
        for col in table_info['columns'][:6]:
            col_name = col['name']
            if col_name not in pk_cols and col_name not in ['udp_create_ts', 'udp_update_ts', 'udp_delete_flag', 'udp_hash', 'domain_name']:
                key_cols.append(col_name)
        
        # Format entity
        mermaid += f"    {table_name} {{\n"
        if pk_cols:
            mermaid += f"        {pk_cols[0]} PK\n"
        for col in key_cols[:5]:  # Limit to 5 non-PK columns
            mermaid += f"        {col}\n"
        mermaid += "    }\n"
    
    # Add relationships
    mermaid += "\n"
    seen_relationships = set()
    for rel in relationships:
        from_table = rel['from_table'].replace('_backup', '')
        to_table = rel['to_table'].replace('_backup', '')
        
        if from_table in core_tables and to_table in core_tables:
            rel_key = (from_table, to_table, rel['from_column'])
            if rel_key not in seen_relationships:
                seen_relationships.add(rel_key)
                # Determine cardinality (simplified - assume many-to-one)
                mermaid += f"    {from_table} ||--o{{ {to_table} : \"{rel['from_column']}\"\n"
    
    return mermaid

def generate_graphviz_diagram(schema):
    """Generate Graphviz DOT diagram"""
    try:
        from graphviz import Digraph
    except ImportError:
        return None
    
    tables = schema['tables']
    relationships = schema['relationships']
    
    # Filter to only tables with data
    valid_tables = {t['table_name']: t for t in tables if t['columns']}
    
    # Create graph
    dot = Digraph(comment='Ingenious ER Schema', format='png')
    dot.attr(rankdir='LR', size='12,16', ratio='compress')
    dot.attr('node', shape='record', style='rounded,filled', fillcolor='lightblue')
    
    # Add nodes (tables)
    core_tables = {}
    for table_name, table_info in valid_tables.items():
        if '_backup' in table_name:
            clean_name = table_name.replace('_backup', '')
            if clean_name not in core_tables:  # Prefer backup version
                core_tables[clean_name] = table_info
        elif table_name not in core_tables:
            core_tables[table_name] = table_info
    
    for table_name, table_info in sorted(core_tables.items()):
        # Get primary key
        pk_cols = table_info.get('primary_keys', [])
        if not pk_cols:
            for col in table_info['columns']:
                if col['name'].lower() in ['id', f'{table_name.lower()}_id']:
                    pk_cols = [col['name']]
                    break
        
        # Build label with key columns
        label_parts = [f"<b>{table_name}</b>"]
        if pk_cols:
            label_parts.append(f"<i>{pk_cols[0]} (PK)</i>")
        
        # Add a few key columns
        key_cols = []
        for col in table_info['columns'][:4]:
            col_name = col['name']
            if col_name not in pk_cols and col_name not in ['udp_create_ts', 'udp_update_ts', 'udp_delete_flag', 'udp_hash', 'domain_name']:
                key_cols.append(col_name)
        
        for col in key_cols:
            label_parts.append(col)
        
        label = "|".join(label_parts)
        dot.node(table_name, label)
    
    # Add edges (relationships)
    seen_relationships = set()
    for rel in relationships:
        from_table = rel['from_table'].replace('_backup', '')
        to_table = rel['to_table'].replace('_backup', '')
        
        if from_table in core_tables and to_table in core_tables:
            rel_key = (from_table, to_table)
            if rel_key not in seen_relationships:
                seen_relationships.add(rel_key)
                dot.edge(from_table, to_table, label=rel['from_column'])
    
    return dot

def generate_networkx_diagram(schema):
    """Generate NetworkX matplotlib diagram"""
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError:
        return None
    
    tables = schema['tables']
    relationships = schema['relationships']
    
    # Filter to only tables with data
    valid_tables = {t['table_name']: t for t in tables if t['columns']}
    
    # Create graph
    G = nx.DiGraph()
    
    # Add nodes
    core_tables = {}
    for table_name, table_info in valid_tables.items():
        if '_backup' in table_name:
            clean_name = table_name.replace('_backup', '')
            if clean_name not in core_tables:
                core_tables[clean_name] = table_info
        elif table_name not in core_tables:
            core_tables[table_name] = table_info
    
    for table_name in core_tables.keys():
        G.add_node(table_name)
    
    # Add edges
    seen_relationships = set()
    for rel in relationships:
        from_table = rel['from_table'].replace('_backup', '')
        to_table = rel['to_table'].replace('_backup', '')
        
        if from_table in core_tables and to_table in core_tables:
            rel_key = (from_table, to_table)
            if rel_key not in seen_relationships:
                seen_relationships.add(rel_key)
                G.add_edge(from_table, to_table, label=rel['from_column'])
    
    # Create layout
    plt.figure(figsize=(20, 16))
    
    # Use hierarchical layout for better organization
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                          node_size=3000, alpha=0.9)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', 
                           arrows=True, arrowsize=20, alpha=0.6)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
    
    # Draw edge labels (only for key relationships to avoid clutter)
    edge_labels = {}
    for (u, v, d) in G.edges(data=True):
        if 'label' in d:
            # Only show label for project_id relationships (most important)
            if 'project' in d['label'].lower() or 'contract' in d['label'].lower():
                edge_labels[(u, v)] = d['label']
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
    
    plt.title('Ingenious Source System - Entity Relationship Diagram', 
              fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    return plt

def main():
    print("=" * 80)
    print("Generating Visual ER Diagrams")
    print("=" * 80)
    print()
    
    # Load schema
    print("Loading schema data...")
    schema = load_schema()
    print(f"Loaded {len(schema['tables'])} tables and {len(schema['relationships'])} relationships")
    print()
    
    # Generate Mermaid diagram
    print("Generating Mermaid diagram...")
    mermaid = generate_mermaid_diagram(schema)
    
    # Save Mermaid diagram
    with open('INGENIOUS_ER_DIAGRAM.mmd', 'w') as f:
        f.write(mermaid)
    print("✓ Mermaid diagram saved to: INGENIOUS_ER_DIAGRAM.mmd")
    
    # Also create a markdown file with embedded Mermaid
    md_content = "# Ingenious ER Diagram (Mermaid)\n\n"
    md_content += "This diagram can be viewed in any Mermaid-compatible viewer (GitHub, GitLab, etc.)\n\n"
    md_content += "```mermaid\n"
    md_content += mermaid
    md_content += "\n```\n"
    
    with open('INGENIOUS_ER_DIAGRAM.md', 'w') as f:
        f.write(md_content)
    print("✓ Mermaid markdown saved to: INGENIOUS_ER_DIAGRAM.md")
    print()
    
    # Generate Graphviz diagram
    print("Generating Graphviz diagram...")
    try:
        dot = generate_graphviz_diagram(schema)
        if dot:
            dot.render('INGENIOUS_ER_DIAGRAM', format='png', cleanup=True)
            print("✓ Graphviz PNG diagram saved to: INGENIOUS_ER_DIAGRAM.png")
            
            # Also generate SVG
            dot.format = 'svg'
            dot.render('INGENIOUS_ER_DIAGRAM', format='svg', cleanup=True)
            print("✓ Graphviz SVG diagram saved to: INGENIOUS_ER_DIAGRAM.svg")
        else:
            print("⚠ Graphviz not available (install with: pip install graphviz)")
    except Exception as e:
        print(f"⚠ Graphviz generation failed: {e}")
        print("  Install graphviz: pip install graphviz")
        print("  Also need system graphviz: brew install graphviz (macOS) or apt-get install graphviz (Linux)")
    print()
    
    # Generate NetworkX diagram
    print("Generating NetworkX matplotlib diagram...")
    try:
        plt = generate_networkx_diagram(schema)
        if plt:
            plt.savefig('INGENIOUS_ER_DIAGRAM_networkx.png', dpi=300, bbox_inches='tight')
            print("✓ NetworkX diagram saved to: INGENIOUS_ER_DIAGRAM_networkx.png")
            plt.close()
        else:
            print("⚠ NetworkX/matplotlib not available (install with: pip install networkx matplotlib)")
    except Exception as e:
        print(f"⚠ NetworkX generation failed: {e}")
        print("  Install dependencies: pip install networkx matplotlib")
    print()
    
    print("=" * 80)
    print("Diagram Generation Complete")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - INGENIOUS_ER_DIAGRAM.mmd (Mermaid source)")
    print("  - INGENIOUS_ER_DIAGRAM.md (Mermaid in markdown)")
    print("  - INGENIOUS_ER_DIAGRAM.png (Graphviz PNG - if available)")
    print("  - INGENIOUS_ER_DIAGRAM.svg (Graphviz SVG - if available)")
    print("  - INGENIOUS_ER_DIAGRAM_networkx.png (NetworkX visualization - if available)")
    print("\nNote: Mermaid diagrams can be viewed on GitHub, GitLab, or at https://mermaid.live/")

if __name__ == "__main__":
    main()







