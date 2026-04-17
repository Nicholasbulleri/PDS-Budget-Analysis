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
Find all database objects in curated_consumption that start with vw_ingenious
"""

from edp_connection import execute_query

def find_vw_ingenious_objects():
    """Find all objects starting with vw_ingenious"""
    print("=" * 80)
    print("Finding all objects starting with vw_ingenious in curated_consumption")
    print("=" * 80)
    print()
    
    all_objects = []
    
    # Method 1: Query information_schema
    print("Method 1: Querying information_schema...")
    try:
        cols, results = execute_query("""
            SELECT table_name, table_type
            FROM system.information_schema.tables 
            WHERE table_schema = 'curated_consumption' 
            AND table_catalog = 'work_dynamics'
            AND table_name LIKE 'vw_ingenious%'
            ORDER BY table_name
        """)
        
        for row in results:
            if hasattr(row, '__getitem__'):
                obj_name = row[0] if len(row) > 0 else None
                obj_type = row[1] if len(row) > 1 else 'UNKNOWN'
                if obj_name:
                    all_objects.append((obj_name, obj_type))
        
        print(f"Found {len(all_objects)} objects via information_schema")
    except Exception as e:
        print(f"information_schema query failed: {e}")
    
    # Method 2: SHOW TABLES
    print("\nMethod 2: Using SHOW TABLES...")
    try:
        cols, results = execute_query("SHOW TABLES IN work_dynamics.curated_consumption")
        
        tables = []
        for row in results:
            if len(row) >= 2:
                table_name = row[1] if hasattr(row, '__getitem__') else str(row)
                if table_name.startswith('vw_ingenious'):
                    tables.append(table_name)
        
        print(f"Found {len(tables)} tables/views via SHOW TABLES")
        if tables:
            print("Tables/Views found:")
            for t in sorted(tables):
                print(f"  - {t}")
    except Exception as e:
        print(f"SHOW TABLES failed: {e}")
    
    # Method 3: SHOW VIEWS (if available)
    print("\nMethod 3: Using SHOW VIEWS...")
    try:
        cols, results = execute_query("SHOW VIEWS IN work_dynamics.curated_consumption")
        
        views = []
        for row in results:
            if len(row) >= 2:
                view_name = row[1] if hasattr(row, '__getitem__') else str(row)
                if view_name.startswith('vw_ingenious'):
                    views.append(view_name)
        
        print(f"Found {len(views)} views via SHOW VIEWS")
        if views:
            print("Views found:")
            for v in sorted(views):
                print(f"  - {v}")
    except Exception as e:
        print(f"SHOW VIEWS failed: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if all_objects:
        print(f"\nTotal objects found: {len(all_objects)}")
        print("\nAll objects starting with vw_ingenious:")
        for obj_name, obj_type in sorted(all_objects):
            print(f"  {obj_name:50} ({obj_type})")
        
        # Group by type
        by_type = {}
        for obj_name, obj_type in all_objects:
            if obj_type not in by_type:
                by_type[obj_type] = []
            by_type[obj_type].append(obj_name)
        
        print("\nGrouped by type:")
        for obj_type, objects in sorted(by_type.items()):
            print(f"  {obj_type}: {len(objects)} objects")
    else:
        print("\nNo objects found starting with vw_ingenious")
    
    return all_objects

if __name__ == "__main__":
    find_vw_ingenious_objects()







