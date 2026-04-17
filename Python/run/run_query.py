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
Run a SQL query against Databricks
"""

import sys
from edp_connection import execute_query

def run_query(query):
    """Execute a query and display results"""
    try:
        print("Executing query...")
        print("=" * 60)
        print(query)
        print("=" * 60)
        print()
        
        columns, results = execute_query(query)
        
        if not results:
            print("No results returned.")
            return
        
        # Print results in transposed format (one column)
        for i, row in enumerate(results, 1):
            print(f"{'=' * 60}")
            print(f"Row {i} of {len(results)}")
            print(f"{'=' * 60}")
            print()
            
            # Transpose: each field on its own line
            for col, val in zip(columns, row):
                # Format the value - handle None, long strings, etc.
                if val is None:
                    val_str = "NULL"
                elif isinstance(val, str) and len(val) > 100:
                    val_str = val[:100] + "... (truncated)"
                else:
                    val_str = str(val)
                
                print(f"{col:50} | {val_str}")
            
            print()
        
        print(f"{'=' * 60}")
        print(f"Total rows: {len(results)}")
        print(f"{'=' * 60}")
        
    except Exception as e:
        print(f"Error executing query: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Query from command line argument
        query = " ".join(sys.argv[1:])
    else:
        # Default query from user
        query = """
        SELECT * 
        FROM work_dynamics.curated_consumption.vw_ingenious_project
        WHERE sourceprojectid LIKE 'AMP25002376'
        """
    
    run_query(query)

