#!/usr/bin/env python3
"""
Analyze all views in curated_consumption schema that start with vw_ingenious
and create an Entity Relationship schema
"""

from edp_connection import execute_query
import json
from collections import defaultdict
import re

def get_all_ingenious_views():
    """Get all views in curated_consumption schema that start with vw_ingenious"""
    print("Fetching all views in curated_consumption starting with vw_ingenious...")
    
    try:
        # Query information_schema - most reliable method
        try:
            cols, results = execute_query("""
                SELECT table_name 
                FROM system.information_schema.tables 
                WHERE table_schema = 'curated_consumption' 
                AND table_catalog = 'work_dynamics'
                AND table_name LIKE 'vw_ingenious%'
                ORDER BY table_name
            """)
            views = []
            for row in results:
                if hasattr(row, '__getitem__'):
                    view_name = row[0] if len(row) > 0 else None
                    if view_name:
                        views.append(view_name)
            if views:
                print(f"Found {len(views)} views using information_schema")
                return sorted(views)
        except Exception as e:
            print(f"information_schema query failed: {e}")
        
        # Fallback: Try SHOW TABLES
        try:
            cols, results = execute_query("SHOW TABLES IN work_dynamics.curated_consumption")
            views = []
            for row in results:
                if len(row) >= 2:
                    table_name = row[1] if hasattr(row, '__getitem__') else str(row)
                    if table_name.startswith('vw_ingenious'):
                        views.append(table_name)
            if views:
                print(f"Found {len(views)} views/tables starting with vw_ingenious")
                return sorted(views)
        except Exception as e:
            print(f"SHOW TABLES failed: {e}")
        
        print("No views found. Returning empty list.")
        return []
        
    except Exception as e:
        print(f"Error fetching views: {e}")
        return []

def get_view_schema(view_name):
    """Get detailed schema information for a view"""
    schema_info = {
        'table_name': view_name,
        'columns': [],
        'primary_keys': [],
        'foreign_keys': [],
        'indexes': [],
        'row_count': None,
        'description': None,
        'view_definition': None
    }
    
    try:
        # Get column information
        cols, results = execute_query(f"DESCRIBE TABLE work_dynamics.curated_consumption.{view_name}")
        
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
                    if col_name.lower() in ['id', f'{view_name.lower()}_id', f'{view_name.lower().replace("vw_", "")}_id']:
                        schema_info['primary_keys'].append(col_name)
    except Exception as e:
        print(f"  Warning: Could not get schema for {view_name}: {e}")
    
    try:
        # Try to get view definition
        cols, results = execute_query(f"SHOW CREATE TABLE work_dynamics.curated_consumption.{view_name}")
        if results:
            definition = ' '.join([str(row) for row in results])
            schema_info['view_definition'] = definition
    except Exception as e:
        # View definition might not be available
        pass
    
    try:
        # Try to get row count (with limit to avoid long queries)
        cols, results = execute_query(f"SELECT COUNT(*) FROM work_dynamics.curated_consumption.{view_name} LIMIT 1")
        if results and len(results) > 0:
            schema_info['row_count'] = results[0][0] if hasattr(results[0], '__getitem__') else None
    except Exception as e:
        # Row count might fail for views
        pass
    
    try:
        # Try to get view comment/description
        cols, results = execute_query(f"""
            SELECT comment 
            FROM system.information_schema.tables 
            WHERE table_schema = 'curated_consumption' 
            AND table_catalog = 'work_dynamics'
            AND table_name = '{view_name}'
        """)
        if results and len(results) > 0:
            comment = results[0][0] if hasattr(results[0], '__getitem__') else None
            if comment:
                schema_info['description'] = comment
    except Exception as e:
        # This might not be available in all Databricks versions
        pass
    
    return schema_info

def analyze_relationships(views_schema):
    """Analyze potential relationships between views based on column names"""
    relationships = []
    
    # Build index of columns by name
    column_index = defaultdict(list)  # column_name -> [(view, column_info), ...]
    
    for view_info in views_schema:
        view_name = view_info['table_name']
        for col in view_info['columns']:
            col_name = col['name'].lower()
            column_index[col_name].append((view_name, col))
    
    # Look for foreign key patterns
    for view_info in views_schema:
        view_name = view_info['table_name']
        
        for col in view_info['columns']:
            col_name = col['name'].lower()
            
            # Pattern 1: Column ends with _id (foreign key pattern)
            if col_name.endswith('_id') and col_name != 'id':
                # Try to find referenced view
                referenced_view = col_name[:-3]  # Remove _id suffix
                
                # Look for views that might match
                for other_view_info in views_schema:
                    other_view = other_view_info['table_name'].lower()
                    # Remove vw_ prefix for matching
                    other_view_clean = other_view.replace('vw_ingenious_', '').replace('vw_', '')
                    referenced_view_clean = referenced_view.replace('ingenious_', '')
                    
                    if referenced_view_clean in other_view_clean or other_view_clean in referenced_view_clean:
                        # Check if the other view has an id column
                        has_id = any(c['name'].lower() in ['id', f'{other_view_info["table_name"].lower()}_id'] 
                                    for c in other_view_info['columns'])
                        if has_id:
                            relationships.append({
                                'from_table': view_name,
                                'from_column': col['name'],
                                'to_table': other_view_info['table_name'],
                                'to_column': 'id',
                                'relationship_type': 'foreign_key',
                                'confidence': 'medium'
                            })
            
            # Pattern 2: Column name matches another view name
            for other_view_info in views_schema:
                other_view = other_view_info['table_name'].lower()
                other_view_clean = other_view.replace('vw_ingenious_', '').replace('vw_', '')
                if col_name == other_view_clean or col_name == f'{other_view_clean}_id':
                    # Check if the other view has an id column
                    has_id = any(c['name'].lower() in ['id', f'{other_view_info["table_name"].lower()}_id'] 
                                for c in other_view_info['columns'])
                    if has_id:
                        relationships.append({
                            'from_table': view_name,
                            'from_column': col['name'],
                            'to_table': other_view_info['table_name'],
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

def generate_er_schema_markdown(views_schema, relationships):
    """Generate a markdown document with ER schema"""
    
    md = "# Ingenious Curated Consumption Views - Entity Relationship Schema\n\n"
    md += f"**Total Views:** {len(views_schema)}\n\n"
    md += f"**Total Relationships Identified:** {len(relationships)}\n\n"
    md += "---\n\n"
    
    # Views section
    md += "## Views\n\n"
    
    for view_info in sorted(views_schema, key=lambda x: x['table_name']):
        view_name = view_info['table_name']
        md += f"#### {view_name}\n\n"
        
        if view_info['description']:
            md += f"*{view_info['description']}*\n\n"
        
        if view_info['row_count'] is not None:
            md += f"**Row Count:** {view_info['row_count']:,}\n\n"
        
        md += "**Columns:**\n\n"
        md += "| Column Name | Data Type | Nullable | Description |\n"
        md += "|-------------|-----------|----------|-------------|\n"
        
        for col in view_info['columns']:
            col_name = col['name']
            col_type = col['type']
            nullable = col.get('nullable', '')
            comment = col.get('comment', '') or ''
            
            # Mark primary keys
            if col_name in view_info['primary_keys']:
                col_name = f"**{col_name}** (PK)"
            
            md += f"| {col_name} | {col_type} | {nullable} | {comment} |\n"
        
        md += "\n"
    
    # Relationships section
    md += "---\n\n"
    md += "## Relationships\n\n"
    
    if relationships:
        md += "| From View | From Column | To View | To Column | Type | Confidence |\n"
        md += "|-----------|-------------|---------|-----------|------|------------|\n"
        
        for rel in sorted(relationships, key=lambda x: (x['from_table'], x['to_table'])):
            md += f"| {rel['from_table']} | {rel['from_column']} | {rel['to_table']} | {rel['to_column']} | {rel['relationship_type']} | {rel['confidence']} |\n"
    else:
        md += "*No relationships automatically identified. Manual review recommended.*\n"
    
    md += "\n---\n\n"
    
    # Summary statistics
    md += "## Summary Statistics\n\n"
    
    total_columns = sum(len(v['columns']) for v in views_schema)
    total_rows = sum(v['row_count'] or 0 for v in views_schema)
    views_with_pk = sum(1 for v in views_schema if v['primary_keys'])
    
    md += f"- **Total Views:** {len(views_schema)}\n"
    md += f"- **Total Columns:** {total_columns}\n"
    md += f"- **Total Rows:** {total_rows:,}\n"
    md += f"- **Views with Primary Keys:** {views_with_pk}\n"
    md += f"- **Identified Relationships:** {len(relationships)}\n"
    if views_schema:
        md += f"- **Average Columns per View:** {total_columns / len(views_schema):.1f}\n"
    
    return md

def generate_er_schema_json(views_schema, relationships):
    """Generate JSON representation of ER schema"""
    return {
        'system': 'ingenious',
        'catalog': 'work_dynamics',
        'schema': 'curated_consumption',
        'view_prefix': 'vw_ingenious',
        'total_views': len(views_schema),
        'total_relationships': len(relationships),
        'views': views_schema,
        'relationships': relationships,
        'metadata': {
            'generated_at': str(__import__('datetime').datetime.now()),
            'analysis_version': '1.0'
        }
    }

def main():
    print("=" * 80)
    print("Ingenious Curated Consumption Views - ER Schema Analysis")
    print("=" * 80)
    print()
    
    # Get all views
    views = get_all_ingenious_views()
    
    if not views:
        print("No views found in work_dynamics.curated_consumption starting with vw_ingenious")
        return
    
    # Analyze each view
    print("\n" + "=" * 80)
    print("Analyzing view schemas...")
    print("=" * 80)
    
    views_schema = []
    
    for i, view in enumerate(views, 1):
        print(f"\n[{i}/{len(views)}] Analyzing: {view}")
        schema_info = get_view_schema(view)
        views_schema.append(schema_info)
        
        print(f"  Columns: {len(schema_info['columns'])}")
        if schema_info['row_count'] is not None:
            print(f"  Rows: {schema_info['row_count']:,}")
        if schema_info['primary_keys']:
            print(f"  Primary Keys: {', '.join(schema_info['primary_keys'])}")
    
    # Analyze relationships
    print("\n" + "=" * 80)
    print("Analyzing relationships...")
    print("=" * 80)
    
    relationships = analyze_relationships(views_schema)
    print(f"\nIdentified {len(relationships)} potential relationships")
    
    # Generate outputs
    print("\n" + "=" * 80)
    print("Generating ER Schema Documentation...")
    print("=" * 80)
    
    # Markdown report
    md_content = generate_er_schema_markdown(views_schema, relationships)
    with open('INGENIOUS_CURATED_VIEWS_ER_SCHEMA.md', 'w') as f:
        f.write(md_content)
    print(f"\n✓ Markdown report saved to: INGENIOUS_CURATED_VIEWS_ER_SCHEMA.md")
    
    # JSON export
    json_content = generate_er_schema_json(views_schema, relationships)
    with open('INGENIOUS_CURATED_VIEWS_ER_SCHEMA.json', 'w') as f:
        json.dump(json_content, f, indent=2)
    print(f"✓ JSON export saved to: INGENIOUS_CURATED_VIEWS_ER_SCHEMA.json")
    
    # Summary
    print("\n" + "=" * 80)
    print("Analysis Complete")
    print("=" * 80)
    print(f"\nTotal Views Analyzed: {len(views_schema)}")
    print(f"Total Columns: {sum(len(v['columns']) for v in views_schema)}")
    print(f"Total Relationships Identified: {len(relationships)}")
    print(f"\nDocumentation files created:")
    print(f"  - INGENIOUS_CURATED_VIEWS_ER_SCHEMA.md (human-readable)")
    print(f"  - INGENIOUS_CURATED_VIEWS_ER_SCHEMA.json (machine-readable)")

if __name__ == "__main__":
    main()

