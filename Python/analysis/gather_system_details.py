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
Gather detailed information about all EDP systems including table counts
"""

from edp_connection import execute_query
import json
from collections import defaultdict

def get_all_systems():
    """Get all source systems from edp_sourcesystem catalog"""
    cols, results = execute_query("SHOW SCHEMAS IN edp_sourcesystem")
    return sorted([row[0] for row in results])

def get_table_count(system_name):
    """Get table count for a system"""
    try:
        cols, tables = execute_query(f"SHOW TABLES IN edp_sourcesystem.{system_name}")
        return len(tables)
    except Exception as e:
        # Handle special cases like corrigo-staging with hyphens
        try:
            cols, tables = execute_query(f"SHOW TABLES IN edp_sourcesystem.`{system_name}`")
            return len(tables)
        except:
            return None

def gather_all_system_details():
    """Gather details for all systems"""
    print("Gathering system details...")
    systems = get_all_systems()
    
    system_details = {}
    total_checked = 0
    
    for i, system in enumerate(systems, 1):
        print(f"Checking {i}/{len(systems)}: {system}...", end=" ")
        table_count = get_table_count(system)
        system_details[system] = {
            'table_count': table_count,
            'has_tables': table_count is not None and table_count > 0
        }
        if table_count is not None:
            print(f"{table_count} tables")
            total_checked += 1
        else:
            print("Error or no tables")
    
    print(f"\nSuccessfully checked {total_checked} systems")
    
    # Save to JSON
    with open('edp_systems_details.json', 'w') as f:
        json.dump(system_details, f, indent=2)
    
    # Create summary
    systems_with_tables = {k: v for k, v in system_details.items() if v['has_tables']}
    systems_sorted = sorted(systems_with_tables.items(), key=lambda x: x[1]['table_count'] or 0, reverse=True)
    
    print("\nTop 30 systems by table count:")
    for i, (system, details) in enumerate(systems_sorted[:30], 1):
        print(f"{i:2}. {system:30} : {details['table_count']:4} tables")
    
    return system_details

if __name__ == "__main__":
    gather_all_system_details()

