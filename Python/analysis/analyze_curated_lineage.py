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
Analyze lineage for all tables in work_dynamics.curated schema
"""

from edp_connection import execute_query
import json
from collections import defaultdict

def get_all_tables():
    """Get all tables in work_dynamics.curated schema"""
    print("Fetching all tables in work_dynamics.curated...")
    cols, results = execute_query("SHOW TABLES IN work_dynamics.curated")
    
    tables = []
    for row in results:
        # SHOW TABLES returns: [database, tableName, isTemporary]
        if len(row) >= 2:
            table_name = row[1] if hasattr(row, '__getitem__') else str(row)
            tables.append(table_name)
    
    print(f"Found {len(tables)} tables")
    return tables

def get_table_details(table_name):
    """Get detailed information about a table including lineage hints"""
    details = {
        'table': table_name,
        'upstream': [],
        'downstream': [],
        'description': None,
        'properties': {}
    }
    
    try:
        # Try DESCRIBE DETAIL for Unity Catalog metadata
        cols, results = execute_query(f"DESCRIBE DETAIL work_dynamics.curated.{table_name}")
        if results:
            for row in results:
                if hasattr(row, '__getitem__'):
                    key = row[0] if len(row) > 0 else None
                    value = row[1] if len(row) > 1 else None
                    if key and value:
                        details['properties'][key] = value
    except Exception as e:
        print(f"  Warning: Could not get DETAIL for {table_name}: {e}")
    
    try:
        # Try DESCRIBE EXTENDED for additional metadata
        cols, results = execute_query(f"DESCRIBE EXTENDED work_dynamics.curated.{table_name}")
        if results:
            for row in results:
                if hasattr(row, '__getitem__'):
                    col_name = row[0] if len(row) > 0 else None
                    col_type = row[1] if len(row) > 1 else None
                    comment = row[2] if len(row) > 2 else None
                    
                    # Look for lineage hints in comments
                    if comment and ('from' in comment.lower() or 'source' in comment.lower() or 'upstream' in comment.lower()):
                        details['description'] = comment
    except Exception as e:
        print(f"  Warning: Could not get EXTENDED for {table_name}: {e}")
    
    try:
        # Try to get table comment/description
        cols, results = execute_query(f"""
            SELECT comment 
            FROM system.information_schema.tables 
            WHERE table_schema = 'curated' 
            AND table_catalog = 'work_dynamics'
            AND table_name = '{table_name}'
        """)
        if results and len(results) > 0:
            comment = results[0][0] if hasattr(results[0], '__getitem__') else None
            if comment:
                details['description'] = comment
    except Exception as e:
        # This might not be available in all Databricks versions
        pass
    
    return details

def get_lineage_from_system_table():
    """Get lineage from system.access.table_lineage system table"""
    dependencies = defaultdict(lambda: {'upstream': [], 'downstream': []})
    
    try:
        print("Querying Unity Catalog lineage from system.access.table_lineage...")
        # First, let's check what columns are available
        try:
            cols, sample = execute_query("SELECT * FROM system.access.table_lineage LIMIT 1")
            if cols:
                print(f"Available columns: {', '.join(cols)}")
        except:
            pass
        
        # Try different possible column name variations
        # The actual column names might vary by Databricks version
        queries_to_try = [
            # Standard Unity Catalog lineage columns
            """
            SELECT 
                source_catalog_name as source_catalog,
                source_schema_name as source_schema,
                source_table_name as source_table,
                destination_catalog_name as target_catalog,
                destination_schema_name as target_schema,
                destination_table_name as target_table
            FROM system.access.table_lineage
            WHERE (destination_catalog_name = 'work_dynamics' AND destination_schema_name = 'curated')
               OR (source_catalog_name = 'work_dynamics' AND source_schema_name = 'curated')
            """,
            # Alternative column names
            """
            SELECT 
                source_catalog,
                source_schema,
                source_table,
                target_catalog,
                target_schema,
                target_table
            FROM system.access.table_lineage
            WHERE (target_catalog = 'work_dynamics' AND target_schema = 'curated')
               OR (source_catalog = 'work_dynamics' AND source_schema = 'curated')
            """,
            # Try with different naming
            """
            SELECT *
            FROM system.access.table_lineage
            WHERE destination_catalog_name = 'work_dynamics' 
              AND destination_schema_name = 'curated'
            LIMIT 100
            """
        ]
        
        for i, query in enumerate(queries_to_try, 1):
            try:
                print(f"  Trying query variant {i}...")
                cols, results = execute_query(query)
                
                if results and len(results) > 0:
                    print(f"✓ Found {len(results)} lineage relationships using variant {i}")
                    print(f"  Columns: {', '.join(cols) if cols else 'unknown'}")
                    
                    # Parse results - need to map columns dynamically
                    for row in results:
                        if hasattr(row, '__getitem__'):
                            # Try to find the right column indices
                            row_dict = {}
                            if cols:
                                for idx, col in enumerate(cols):
                                    if idx < len(row):
                                        row_dict[col.lower()] = row[idx]
                            
                            # Extract source and target info
                            source_catalog = (row_dict.get('source_catalog_name') or 
                                            row_dict.get('source_catalog') or '')
                            source_schema = (row_dict.get('source_schema_name') or 
                                           row_dict.get('source_schema') or '')
                            source_table = (row_dict.get('source_table_name') or 
                                          row_dict.get('source_table') or '')
                            target_catalog = (row_dict.get('destination_catalog_name') or 
                                            row_dict.get('target_catalog') or 
                                            row_dict.get('destination_catalog') or '')
                            target_schema = (row_dict.get('destination_schema_name') or 
                                           row_dict.get('target_schema') or 
                                           row_dict.get('destination_schema') or '')
                            target_table = (row_dict.get('destination_table_name') or 
                                           row_dict.get('target_table') or 
                                           row_dict.get('destination_table') or '')
                            
                            # Build full table names
                            if source_catalog and source_schema and source_table:
                                source_full = f"{source_catalog}.{source_schema}.{source_table}"
                            elif source_schema and source_table:
                                source_full = f"{source_schema}.{source_table}"
                            elif source_table:
                                source_full = source_table
                            else:
                                continue
                            
                            if target_catalog and target_schema and target_table:
                                target_full = f"{target_catalog}.{target_schema}.{target_table}"
                            elif target_schema and target_table:
                                target_full = f"{target_schema}.{target_table}"
                            elif target_table:
                                target_full = target_table
                            else:
                                continue
                            
                            # Only process if target is in our schema
                            if target_catalog == 'work_dynamics' and target_schema == 'curated':
                                dependencies[target_table]['upstream'].append(source_full)
                            
                            # Also track if source is in our schema (for downstream)
                            if source_catalog == 'work_dynamics' and source_schema == 'curated':
                                dependencies[source_table]['downstream'].append(target_full)
                    
                    return dependencies, True
            except Exception as e:
                print(f"  Variant {i} failed: {e}")
                continue
        
        print("No lineage data found in system.access.table_lineage with any query variant")
        return dependencies, False
    except Exception as e:
        print(f"Could not query system.access.table_lineage: {e}")
        return dependencies, False

def get_lineage_from_rest_api(table_name):
    """Get lineage for a specific table using Databricks REST API"""
    try:
        import os
        import requests
        from edp_connection import EDP_CONFIG
        
        # Get workspace URL from server hostname
        server_hostname = EDP_CONFIG.get('server_hostname', '')
        if not server_hostname:
            return {'upstream': [], 'downstream': []}
        
        # Extract workspace URL
        if 'azuredatabricks.net' in server_hostname:
            workspace_url = f"https://{server_hostname}"
        else:
            workspace_url = f"https://{server_hostname}"
        
        # Get access token (try Azure AD first, then fallback)
        access_token = None
        if EDP_CONFIG.get('use_azure_ad'):
            try:
                from azure.identity import DefaultAzureCredential
                credential = DefaultAzureCredential()
                token_response = credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default")
                access_token = token_response.token
            except:
                pass
        
        if not access_token and EDP_CONFIG.get('access_token'):
            access_token = EDP_CONFIG['access_token']
        
        if not access_token:
            return {'upstream': [], 'downstream': []}
        
        # Call Unity Catalog Lineage API
        # API endpoint: GET /api/2.1/unity-catalog/lineage/table
        # Format: /api/2.1/unity-catalog/lineage/table?table_name=full_table_name
        full_table_name = f"work_dynamics.curated.{table_name}"
        api_url = f"{workspace_url}/api/2.1/unity-catalog/lineage/table"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'table_name': full_table_name
        }
        
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                lineage = {'upstream': [], 'downstream': []}
                
                # Parse upstream sources
                if 'upstreams' in data:
                    for upstream in data['upstreams']:
                        # Handle different response formats
                        table_info = None
                        if isinstance(upstream, dict):
                            if 'tableInfo' in upstream:
                                table_info = upstream['tableInfo']
                            elif 'catalog_name' in upstream:
                                table_info = upstream
                        
                        if table_info:
                            catalog = table_info.get('catalog_name', '') or table_info.get('catalog', '')
                            schema = table_info.get('schema_name', '') or table_info.get('schema', '')
                            table = table_info.get('name', '') or table_info.get('table', '')
                            if catalog and schema and table:
                                lineage['upstream'].append(f"{catalog}.{schema}.{table}")
                            elif schema and table:
                                lineage['upstream'].append(f"{schema}.{table}")
                            elif table:
                                lineage['upstream'].append(table)
                
                # Parse downstream dependencies
                if 'downstreams' in data:
                    for downstream in data['downstreams']:
                        # Handle different response formats
                        table_info = None
                        if isinstance(downstream, dict):
                            if 'tableInfo' in downstream:
                                table_info = downstream['tableInfo']
                            elif 'catalog_name' in downstream:
                                table_info = downstream
                        
                        if table_info:
                            catalog = table_info.get('catalog_name', '') or table_info.get('catalog', '')
                            schema = table_info.get('schema_name', '') or table_info.get('schema', '')
                            table = table_info.get('name', '') or table_info.get('table', '')
                            if catalog and schema and table:
                                lineage['downstream'].append(f"{catalog}.{schema}.{table}")
                            elif schema and table:
                                lineage['downstream'].append(f"{schema}.{table}")
                            elif table:
                                lineage['downstream'].append(table)
                
                return lineage
            elif response.status_code == 404:
                # Table might not have lineage or endpoint doesn't exist
                return {'upstream': [], 'downstream': []}
            else:
                # Log error but don't print for every table (too verbose)
                if response.status_code != 403:  # Permission denied is expected for some tables
                    pass  # Silent failure for REST API
                return {'upstream': [], 'downstream': []}
        except requests.exceptions.RequestException:
            # Network/connection error
            return {'upstream': [], 'downstream': []}
    except ImportError:
        # requests not installed
        return {'upstream': [], 'downstream': []}
    except Exception as e:
        # API call failed
        return {'upstream': [], 'downstream': []}

def analyze_table_dependencies():
    """Try to find dependencies using system tables and REST API"""
    dependencies = defaultdict(lambda: {'upstream': [], 'downstream': []})
    
    # First try the system table approach
    deps, success = get_lineage_from_system_table()
    if success:
        return deps
    
    # If system table doesn't work, we'll use REST API per table
    print("System table approach didn't work. Will use REST API per table if needed.")
    return dependencies

def get_view_definition(table_name):
    """Get view definition to find upstream sources"""
    upstream = []
    
    try:
        # Try to get view definition
        cols, results = execute_query(f"SHOW CREATE TABLE work_dynamics.curated.{table_name}")
        if results:
            definition = ' '.join([str(row) for row in results])
            
            # Parse for table references
            import re
            # Look for FROM/JOIN clauses
            from_matches = re.findall(r'FROM\s+([a-zA-Z0-9_\.`]+)', definition, re.IGNORECASE)
            join_matches = re.findall(r'JOIN\s+([a-zA-Z0-9_\.`]+)', definition, re.IGNORECASE)
            
            for match in from_matches + join_matches:
                # Clean up backticks and normalize
                clean_match = match.strip('`').strip()
                if clean_match and clean_match not in upstream:
                    upstream.append(clean_match)
    except Exception as e:
        # Table might not be a view, or query might not be supported
        pass
    
    return upstream

def main():
    print("=" * 80)
    print("Analyzing Lineage for work_dynamics.curated Schema")
    print("=" * 80)
    print()
    
    # Get all tables
    tables = get_all_tables()
    
    if not tables:
        print("No tables found in work_dynamics.curated")
        return
    
    # Try to get system-level dependencies
    print("\n" + "=" * 80)
    print("Querying system-level lineage information...")
    print("=" * 80)
    system_deps = analyze_table_dependencies()
    
    # Check if system table approach worked
    system_table_worked = any(
        deps['upstream'] or deps['downstream'] 
        for deps in system_deps.values()
    )
    
    # Analyze each table
    print("\n" + "=" * 80)
    print("Analyzing individual tables...")
    print("=" * 80)
    
    all_lineage = {}
    
    for i, table in enumerate(tables, 1):
        print(f"\n[{i}/{len(tables)}] Analyzing: {table}")
        
        details = get_table_details(table)
        
        # Try to get view definition for upstream sources
        upstream_from_view = get_view_definition(table)
        if upstream_from_view:
            details['upstream'].extend(upstream_from_view)
        
        # Add system-level dependencies (if system table worked)
        if system_table_worked and table in system_deps:
            details['upstream'].extend(system_deps[table]['upstream'])
            details['downstream'].extend(system_deps[table]['downstream'])
        
        # If system table didn't work, try REST API for this table
        if not system_table_worked and not details['upstream'] and not details['downstream']:
            print(f"  Trying REST API for lineage...")
            rest_lineage = get_lineage_from_rest_api(table)
            if rest_lineage['upstream'] or rest_lineage['downstream']:
                details['upstream'].extend(rest_lineage['upstream'])
                details['downstream'].extend(rest_lineage['downstream'])
                print(f"  Found {len(rest_lineage['upstream'])} upstream, {len(rest_lineage['downstream'])} downstream via REST API")
        
        # Remove duplicates
        details['upstream'] = list(set(details['upstream']))
        details['downstream'] = list(set(details['downstream']))
        
        all_lineage[table] = details
    
    # Generate report
    print("\n" + "=" * 80)
    print("Generating Lineage Report...")
    print("=" * 80)
    
    # Markdown report
    report_md = "# Lineage Analysis: work_dynamics.curated Schema\n\n"
    report_md += f"**Total Tables:** {len(tables)}\n\n"
    report_md += "---\n\n"
    
    for table, details in sorted(all_lineage.items()):
        report_md += f"## {table}\n\n"
        
        if details['description']:
            report_md += f"**Description:** {details['description']}\n\n"
        
        if details['upstream']:
            report_md += "### Upstream Sources\n\n"
            for source in sorted(details['upstream']):
                report_md += f"- `{source}`\n"
            report_md += "\n"
        else:
            report_md += "### Upstream Sources\n\n"
            report_md += "*No upstream sources identified*\n\n"
        
        if details['downstream']:
            report_md += "### Downstream Dependencies\n\n"
            for downstream in sorted(details['downstream']):
                report_md += f"- `{downstream}`\n"
            report_md += "\n"
        else:
            report_md += "### Downstream Dependencies\n\n"
            report_md += "*No downstream dependencies identified*\n\n"
        
        report_md += "---\n\n"
    
    # Save report
    with open('CURATED_SCHEMA_LINEAGE.md', 'w') as f:
        f.write(report_md)
    
    print(f"\nReport saved to: CURATED_SCHEMA_LINEAGE.md")
    
    # Also create a summary CSV
    import csv
    with open('CURATED_SCHEMA_LINEAGE.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Table', 'Upstream Sources', 'Downstream Dependencies', 'Description'])
        
        for table, details in sorted(all_lineage.items()):
            upstream_str = '; '.join(sorted(details['upstream'])) if details['upstream'] else 'None'
            downstream_str = '; '.join(sorted(details['downstream'])) if details['downstream'] else 'None'
            desc = details['description'] or 'None'
            writer.writerow([table, upstream_str, downstream_str, desc])
    
    print(f"CSV summary saved to: CURATED_SCHEMA_LINEAGE.csv")
    
    # Print summary statistics
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    tables_with_upstream = sum(1 for d in all_lineage.values() if d['upstream'])
    tables_with_downstream = sum(1 for d in all_lineage.values() if d['downstream'])
    
    print(f"Tables with identified upstream sources: {tables_with_upstream}/{len(tables)}")
    print(f"Tables with identified downstream dependencies: {tables_with_downstream}/{len(tables)}")
    
    if tables_with_upstream == 0:
        print("\n⚠️  Note: No upstream sources were identified.")
        print("This could mean:")
        print("  - Unity Catalog lineage is not enabled")
        print("  - Tables are not views (cannot parse SQL)")
        print("  - Lineage information is stored elsewhere")
        print("\nConsider:")
        print("  - Checking Databricks Unity Catalog lineage UI")
        print("  - Reviewing table/view definitions manually")
        print("  - Consulting with data engineering team")

if __name__ == "__main__":
    main()


