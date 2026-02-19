#!/usr/bin/env python3
"""
Generate visual ER diagram from Ingenious Curated Views ER schema JSON
"""

import json
import os
from collections import defaultdict

def load_schema():
    """Load the ER schema JSON"""
    with open('INGENIOUS_CURATED_VIEWS_ER_SCHEMA.json', 'r') as f:
        return json.load(f)

def generate_mermaid_diagram(schema):
    """Generate Mermaid ER diagram"""
    views = schema['views']
    relationships = schema['relationships']
    
    # Filter to only views with data (non-empty columns)
    valid_views = {v['table_name']: v for v in views if v['columns']}
    
    # Build Mermaid ER diagram
    mermaid = "erDiagram\n"
    
    # Add entity definitions with key attributes
    for view_name, view_info in sorted(valid_views.items()):
        # Get primary key
        pk_cols = view_info.get('primary_keys', [])
        if not pk_cols:
            # Try to find id column
            for col in view_info['columns']:
                if col['name'].lower() in ['id', f'{view_name.lower()}_id']:
                    pk_cols = [col['name']]
                    break
        
        # Get a few key columns (limit to 5-6 for readability)
        key_cols = []
        for col in view_info['columns'][:8]:
            col_name = col['name']
            if col_name not in pk_cols and col_name not in ['udp_create_ts', 'udp_update_ts', 'udp_delete_flag', 'udp_hash', 'domainname', 'sourcesystem']:
                key_cols.append(col_name)
        
        # Format entity (remove vw_ingenious_ prefix for cleaner names)
        clean_name = view_name.replace('vw_ingenious_', '')
        mermaid += f"    {clean_name} {{\n"
        if pk_cols:
            mermaid += f"        {pk_cols[0]} PK\n"
        for col in key_cols[:6]:  # Limit to 6 non-PK columns
            mermaid += f"        {col}\n"
        mermaid += "    }\n"
    
    # Add relationships
    mermaid += "\n"
    seen_relationships = set()
    for rel in relationships:
        from_view = rel['from_table'].replace('vw_ingenious_', '')
        to_view = rel['to_table'].replace('vw_ingenious_', '')
        
        if from_view in [v.replace('vw_ingenious_', '') for v in valid_views.keys()] and \
           to_view in [v.replace('vw_ingenious_', '') for v in valid_views.keys()]:
            rel_key = (from_view, to_view, rel['from_column'])
            if rel_key not in seen_relationships:
                seen_relationships.add(rel_key)
                # Determine cardinality (simplified - assume many-to-one)
                mermaid += f"    {from_view} ||--o{{ {to_view} : \"{rel['from_column']}\"\n"
    
    # Also add inferred relationships based on common column patterns
    # Look for projectidentifier, projectid, etc.
    project_views = {}
    for view_name, view_info in valid_views.items():
        clean_name = view_name.replace('vw_ingenious_', '')
        for col in view_info['columns']:
            col_name = col['name'].lower()
            if 'projectidentifier' in col_name or 'projectid' in col_name:
                if clean_name not in project_views:
                    project_views[clean_name] = col['name']
    
    # Link to project view if it exists
    if 'project' in [v.replace('vw_ingenious_', '') for v in valid_views.keys()]:
        for view_name, project_col in project_views.items():
            if view_name != 'project':
                rel_key = (view_name, 'project', project_col)
                if rel_key not in seen_relationships:
                    seen_relationships.add(rel_key)
                    mermaid += f"    {view_name} ||--o{{ project : \"{project_col}\"\n"
    
    return mermaid

def generate_networkx_diagram(schema):
    """Generate NetworkX matplotlib diagram"""
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError:
        return None
    
    views = schema['views']
    relationships = schema['relationships']
    
    # Filter to only views with data
    valid_views = {v['table_name']: v for v in views if v['columns']}
    
    # Create graph
    G = nx.DiGraph()
    
    # Add nodes
    for view_name in valid_views.keys():
        clean_name = view_name.replace('vw_ingenious_', '')
        G.add_node(clean_name)
    
    # Add edges from explicit relationships
    seen_relationships = set()
    for rel in relationships:
        from_view = rel['from_table'].replace('vw_ingenious_', '')
        to_view = rel['to_table'].replace('vw_ingenious_', '')
        
        if from_view in [v.replace('vw_ingenious_', '') for v in valid_views.keys()] and \
           to_view in [v.replace('vw_ingenious_', '') for v in valid_views.keys()]:
            rel_key = (from_view, to_view)
            if rel_key not in seen_relationships:
                seen_relationships.add(rel_key)
                G.add_edge(from_view, to_view, label=rel['from_column'])
    
    # Add inferred relationships based on projectidentifier columns
    project_views = {}
    for view_name, view_info in valid_views.items():
        clean_name = view_name.replace('vw_ingenious_', '')
        for col in view_info['columns']:
            col_name = col['name'].lower()
            if 'projectidentifier' in col_name or 'projectid' in col_name:
                if clean_name not in project_views:
                    project_views[clean_name] = col['name']
    
    # Link to project view if it exists
    if 'project' in [v.replace('vw_ingenious_', '') for v in valid_views.keys()]:
        for view_name, project_col in project_views.items():
            if view_name != 'project':
                rel_key = (view_name, 'project')
                if rel_key not in seen_relationships:
                    seen_relationships.add(rel_key)
                    G.add_edge(view_name, 'project', label=project_col)
    
    # Create layout
    plt.figure(figsize=(24, 18))
    
    # Use hierarchical layout for better organization
    pos = nx.spring_layout(G, k=4, iterations=100)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightgreen', 
                          node_size=4000, alpha=0.9)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', 
                           arrows=True, arrowsize=20, alpha=0.6)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
    
    # Draw edge labels (only for key relationships to avoid clutter)
    edge_labels = {}
    for (u, v, d) in G.edges(data=True):
        if 'label' in d:
            # Show label for project relationships (most important)
            if 'project' in d['label'].lower() or 'projectidentifier' in d['label'].lower():
                edge_labels[(u, v)] = d['label']
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7)
    
    plt.title('Ingenious Curated Consumption Views - Entity Relationship Diagram', 
              fontsize=18, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    return plt

def main():
    print("=" * 80)
    print("Generating Visual ER Diagrams for Curated Consumption Views")
    print("=" * 80)
    print()
    
    # Load schema
    print("Loading schema data...")
    schema = load_schema()
    print(f"Loaded {len(schema['views'])} views and {len(schema['relationships'])} relationships")
    print()
    
    # Generate Mermaid diagram
    print("Generating Mermaid diagram...")
    mermaid = generate_mermaid_diagram(schema)
    
    # Save Mermaid diagram
    with open('INGENIOUS_CURATED_VIEWS_ER_DIAGRAM.mmd', 'w') as f:
        f.write(mermaid)
    print("✓ Mermaid diagram saved to: INGENIOUS_CURATED_VIEWS_ER_DIAGRAM.mmd")
    
    # Also create a markdown file with embedded Mermaid
    md_content = "# Ingenious Curated Consumption Views ER Diagram (Mermaid)\n\n"
    md_content += "This diagram shows the entity relationships between curated consumption views.\n\n"
    md_content += "```mermaid\n"
    md_content += mermaid
    md_content += "\n```\n"
    
    with open('INGENIOUS_CURATED_VIEWS_ER_DIAGRAM.md', 'w') as f:
        f.write(md_content)
    print("✓ Mermaid markdown saved to: INGENIOUS_CURATED_VIEWS_ER_DIAGRAM.md")
    print()
    
    # Generate NetworkX diagram
    print("Generating NetworkX matplotlib diagram...")
    try:
        plt = generate_networkx_diagram(schema)
        if plt:
            plt.savefig('INGENIOUS_CURATED_VIEWS_ER_DIAGRAM_networkx.png', dpi=300, bbox_inches='tight')
            print("✓ NetworkX diagram saved to: INGENIOUS_CURATED_VIEWS_ER_DIAGRAM_networkx.png")
            plt.close()
        else:
            print("⚠ NetworkX/matplotlib not available")
    except Exception as e:
        print(f"⚠ NetworkX generation failed: {e}")
    print()
    
    print("=" * 80)
    print("Diagram Generation Complete")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - INGENIOUS_CURATED_VIEWS_ER_DIAGRAM.mmd (Mermaid source)")
    print("  - INGENIOUS_CURATED_VIEWS_ER_DIAGRAM.md (Mermaid in markdown)")
    print("  - INGENIOUS_CURATED_VIEWS_ER_DIAGRAM_networkx.png (NetworkX visualization)")
    print("\nNote: Mermaid diagrams can be viewed on GitHub, GitLab, or at https://mermaid.live/")

if __name__ == "__main__":
    main()







