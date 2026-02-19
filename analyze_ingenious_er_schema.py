#!/usr/bin/env python3
"""
Analyze all tables in the Ingenious source system and create an Entity Relationship schema
"""

from edp_connection import execute_query
import json
from collections import defaultdict
import re

def get_all_ingenious_tables():
    """Get all tables in edp_sourcesystem.ingenious schema"""
    print("Fetching all tables in edp_sourcesystem.ingenious...")
    
    try:
        cols, results = execute_query("SHOW TABLES IN edp_sourcesystem.ingenious")
        
        tables = []
        for row in results:
            # SHOW TABLES returns: [database, tableName, isTemporary]
            if len(row) >= 2:
                table_name = row[1] if hasattr(row, '__getitem__') else str(row)
                tables.append(table_name)
        
        print(f"Found {len(tables)} tables")
        return sorted(tables)
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

def get_table_schema(table_name):
    """Get detailed schema information for a table"""
    schema_info = {
        'table_name': table_name,
        'columns': [],
        'primary_keys': [],
        'foreign_keys': [],
        'indexes': [],
        'row_count': None,
        'description': None
    }
    
    try:
        # Get column information
        cols, results = execute_query(f"DESCRIBE TABLE edp_sourcesystem.ingenious.{table_name}")
        
        for row in results:
            if hasattr(row, '__getitem__') and len(row) >= 2:
                col_name = row[0] if len(row) > 0 else None
                col_type = row[1] if len(row) > 1 else None
                col_nullable = row[2] if len(row) > 2 else None
                col_comment = row[3] if len(row) > 3 else None
                
                if col_name and col_type:
                    column_info = {
                        'name': col_name,
                        'type': col_type,
                        'nullable': col_nullable,
                        'comment': col_comment
                    }
                    schema_info['columns'].append(column_info)
                    
                    # Check if column name suggests primary key
                    if col_name.lower() in ['id', f'{table_name.lower()}_id', f'{table_name.lower()}id']:
                        schema_info['primary_keys'].append(col_name)
    except Exception as e:
        print(f"  Warning: Could not get schema for {table_name}: {e}")
    
    try:
        # Try to get row count (with limit to avoid long queries)
        cols, results = execute_query(f"SELECT COUNT(*) FROM edp_sourcesystem.ingenious.{table_name} LIMIT 1")
        if results and len(results) > 0:
            schema_info['row_count'] = results[0][0] if hasattr(results[0], '__getitem__') else None
    except Exception as e:
        # Row count might fail for views or large tables
        pass
    
    try:
        # Try to get table comment/description
        cols, results = execute_query(f"""
            SELECT comment 
            FROM system.information_schema.tables 
            WHERE table_schema = 'ingenious' 
            AND table_catalog = 'edp_sourcesystem'
            AND table_name = '{table_name}'
        """)
        if results and len(results) > 0:
            comment = results[0][0] if hasattr(results[0], '__getitem__') else None
            if comment:
                schema_info['description'] = comment
    except Exception as e:
        # This might not be available in all Databricks versions
        pass
    
    return schema_info

def analyze_relationships(tables_schema):
    """Analyze potential relationships between tables based on column names"""
    relationships = []
    
    # Build index of columns by name
    column_index = defaultdict(list)  # column_name -> [(table, column_info), ...]
    
    for table_info in tables_schema:
        table_name = table_info['table_name']
        for col in table_info['columns']:
            col_name = col['name'].lower()
            column_index[col_name].append((table_name, col))
    
    # Look for foreign key patterns
    for table_info in tables_schema:
        table_name = table_info['table_name']
        
        for col in table_info['columns']:
            col_name = col['name'].lower()
            
            # Pattern 1: Column ends with _id (foreign key pattern)
            if col_name.endswith('_id') and col_name != 'id':
                # Try to find referenced table
                referenced_table = col_name[:-3]  # Remove _id suffix
                
                # Look for tables that might match
                for other_table_info in tables_schema:
                    other_table = other_table_info['table_name'].lower()
                    if referenced_table in other_table or other_table in referenced_table:
                        # Check if the other table has an id column
                        has_id = any(c['name'].lower() in ['id', f'{other_table_info["table_name"].lower()}_id'] 
                                    for c in other_table_info['columns'])
                        if has_id:
                            relationships.append({
                                'from_table': table_name,
                                'from_column': col['name'],
                                'to_table': other_table_info['table_name'],
                                'to_column': 'id',  # Assume id column
                                'relationship_type': 'foreign_key',
                                'confidence': 'medium'
                            })
            
            # Pattern 2: Column name matches another table name
            for other_table_info in tables_schema:
                other_table = other_table_info['table_name'].lower()
                if col_name == other_table or col_name == f'{other_table}_id':
                    # Check if the other table has an id column
                    has_id = any(c['name'].lower() in ['id', f'{other_table_info["table_name"].lower()}_id'] 
                                for c in other_table_info['columns'])
                    if has_id:
                        relationships.append({
                            'from_table': table_name,
                            'from_column': col['name'],
                            'to_table': other_table_info['table_name'],
                            'to_column': 'id',
                            'relationship_type': 'foreign_key',
                            'confidence': 'medium'
                        })
    
    # Remove duplicates
    seen = set()
    unique_relationships = []
    for rel in relationships:
        key = (rel['from_table'], rel['from_column'], rel['to_table'])
        if key not in seen:
            seen.add(key)
            unique_relationships.append(rel)
    
    return unique_relationships

def generate_er_schema_markdown(tables_schema, relationships):
    """Generate a markdown document with ER schema"""
    
    md = "# Ingenious Source System - Entity Relationship Schema\n\n"
    md += f"**Total Tables:** {len(tables_schema)}\n\n"
    md += f"**Total Relationships Identified:** {len(relationships)}\n\n"
    md += "---\n\n"
    
    # Group tables by prefix/domain (if any)
    table_groups = defaultdict(list)
    for table_info in tables_schema:
        table_name = table_info['table_name']
        # Try to identify prefix (e.g., "project_", "user_", etc.)
        parts = table_name.split('_')
        if len(parts) > 1:
            prefix = parts[0]
            table_groups[prefix].append(table_info)
        else:
            table_groups['other'].append(table_info)
    
    # Tables section
    md += "## Tables\n\n"
    
    for group in sorted(table_groups.keys()):
        if group != 'other':
            md += f"### {group.title()} Tables\n\n"
        
        for table_info in sorted(table_groups[group], key=lambda x: x['table_name']):
            table_name = table_info['table_name']
            md += f"#### {table_name}\n\n"
            
            if table_info['description']:
                md += f"*{table_info['description']}*\n\n"
            
            if table_info['row_count'] is not None:
                md += f"**Row Count:** {table_info['row_count']:,}\n\n"
            
            md += "**Columns:**\n\n"
            md += "| Column Name | Data Type | Nullable | Description |\n"
            md += "|-------------|-----------|----------|-------------|\n"
            
            for col in table_info['columns']:
                col_name = col['name']
                col_type = col['type']
                nullable = col.get('nullable', '')
                comment = col.get('comment', '') or ''
                
                # Mark primary keys
                if col_name in table_info['primary_keys']:
                    col_name = f"**{col_name}** (PK)"
                
                md += f"| {col_name} | {col_type} | {nullable} | {comment} |\n"
            
            md += "\n"
    
    # Relationships section
    md += "---\n\n"
    md += "## Relationships\n\n"
    
    if relationships:
        md += "| From Table | From Column | To Table | To Column | Type | Confidence |\n"
        md += "|------------|-------------|----------|-----------|------|------------|\n"
        
        for rel in sorted(relationships, key=lambda x: (x['from_table'], x['to_table'])):
            md += f"| {rel['from_table']} | {rel['from_column']} | {rel['to_table']} | {rel['to_column']} | {rel['relationship_type']} | {rel['confidence']} |\n"
    else:
        md += "*No relationships automatically identified. Manual review recommended.*\n"
    
    md += "\n---\n\n"
    
    # ER Diagram (text-based)
    md += "## Entity Relationship Diagram (Text Representation)\n\n"
    md += "```\n"
    
    # Group relationships by from_table
    rel_by_table = defaultdict(list)
    for rel in relationships:
        rel_by_table[rel['from_table']].append(rel)
    
    for table_info in sorted(tables_schema, key=lambda x: x['table_name']):
        table_name = table_info['table_name']
        md += f"\n{table_name}\n"
        md += "-" * len(table_name) + "\n"
        
        # Show primary keys
        if table_info['primary_keys']:
            md += f"  PK: {', '.join(table_info['primary_keys'])}\n"
        
        # Show key columns (first 5)
        key_cols = [col['name'] for col in table_info['columns'][:5]]
        md += f"  Columns: {', '.join(key_cols)}"
        if len(table_info['columns']) > 5:
            md += f" ... (+{len(table_info['columns']) - 5} more)"
        md += "\n"
        
        # Show relationships
        if table_name in rel_by_table:
            md += "  Relationships:\n"
            for rel in rel_by_table[table_name]:
                md += f"    -> {rel['to_table']} via {rel['from_column']}\n"
    
    md += "```\n\n"
    
    # Summary statistics
    md += "---\n\n"
    md += "## Summary Statistics\n\n"
    
    total_columns = sum(len(t['columns']) for t in tables_schema)
    total_rows = sum(t['row_count'] or 0 for t in tables_schema)
    tables_with_pk = sum(1 for t in tables_schema if t['primary_keys'])
    
    md += f"- **Total Tables:** {len(tables_schema)}\n"
    md += f"- **Total Columns:** {total_columns}\n"
    md += f"- **Total Rows:** {total_rows:,}\n"
    md += f"- **Tables with Primary Keys:** {tables_with_pk}\n"
    md += f"- **Identified Relationships:** {len(relationships)}\n"
    md += f"- **Average Columns per Table:** {total_columns / len(tables_schema):.1f}\n"
    
    return md

def generate_er_schema_json(tables_schema, relationships):
    """Generate JSON representation of ER schema"""
    return {
        'system': 'ingenious',
        'catalog': 'edp_sourcesystem',
        'schema': 'ingenious',
        'total_tables': len(tables_schema),
        'total_relationships': len(relationships),
        'tables': tables_schema,
        'relationships': relationships,
        'metadata': {
            'generated_at': str(__import__('datetime').datetime.now()),
            'analysis_version': '1.0'
        }
    }

def main():
    print("=" * 80)
    print("Ingenious Source System - ER Schema Analysis")
    print("=" * 80)
    print()
    
    # Get all tables
    tables = get_all_ingenious_tables()
    
    if not tables:
        print("No tables found in edp_sourcesystem.ingenious")
        return
    
    # Analyze each table
    print("\n" + "=" * 80)
    print("Analyzing table schemas...")
    print("=" * 80)
    
    tables_schema = []
    
    for i, table in enumerate(tables, 1):
        print(f"\n[{i}/{len(tables)}] Analyzing: {table}")
        schema_info = get_table_schema(table)
        tables_schema.append(schema_info)
        
        print(f"  Columns: {len(schema_info['columns'])}")
        if schema_info['row_count'] is not None:
            print(f"  Rows: {schema_info['row_count']:,}")
        if schema_info['primary_keys']:
            print(f"  Primary Keys: {', '.join(schema_info['primary_keys'])}")
    
    # Analyze relationships
    print("\n" + "=" * 80)
    print("Analyzing relationships...")
    print("=" * 80)
    
    relationships = analyze_relationships(tables_schema)
    print(f"\nIdentified {len(relationships)} potential relationships")
    
    # Generate outputs
    print("\n" + "=" * 80)
    print("Generating ER Schema Documentation...")
    print("=" * 80)
    
    # Markdown report
    md_content = generate_er_schema_markdown(tables_schema, relationships)
    with open('INGENIOUS_ER_SCHEMA.md', 'w') as f:
        f.write(md_content)
    print(f"\n✓ Markdown report saved to: INGENIOUS_ER_SCHEMA.md")
    
    # JSON export
    json_content = generate_er_schema_json(tables_schema, relationships)
    with open('INGENIOUS_ER_SCHEMA.json', 'w') as f:
        json.dump(json_content, f, indent=2)
    print(f"✓ JSON export saved to: INGENIOUS_ER_SCHEMA.json")
    
    # Summary
    print("\n" + "=" * 80)
    print("Analysis Complete")
    print("=" * 80)
    print(f"\nTotal Tables Analyzed: {len(tables_schema)}")
    print(f"Total Columns: {sum(len(t['columns']) for t in tables_schema)}")
    print(f"Total Relationships Identified: {len(relationships)}")
    print(f"\nDocumentation files created:")
    print(f"  - INGENIOUS_ER_SCHEMA.md (human-readable)")
    print(f"  - INGENIOUS_ER_SCHEMA.json (machine-readable)")

if __name__ == "__main__":
    main()







