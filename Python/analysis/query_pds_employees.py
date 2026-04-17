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
Query to count employees in PDS organization
"""

from edp_connection import execute_query

# First, let's see what columns are available
print("Exploring table structure...")
print("=" * 60)

try:
    # Get a sample row to see column names
    columns, sample = execute_query("""
        SELECT * 
        FROM human_resources.analytical_consumption.jll_worker_non_sensitive
        LIMIT 1
    """)
    
    print(f"Found {len(columns)} columns in the table")
    print("\nSample columns (first 20):")
    for i, col in enumerate(columns[:20], 1):
        print(f"  {i}. {col}")
    if len(columns) > 20:
        print(f"  ... and {len(columns) - 20} more columns")
    
    print("\n" + "=" * 60)
    print("Checking for organization-related columns...")
    print("=" * 60)
    
    # Look for organization-related columns
    org_columns = [col for col in columns if 'org' in col.lower() or 'business' in col.lower() or 'unit' in col.lower() or 'pds' in col.lower()]
    if org_columns:
        print("Organization-related columns found:")
        for col in org_columns:
            print(f"  - {col}")
    else:
        print("No obvious organization columns found. Showing all columns:")
        for col in columns:
            print(f"  - {col}")
    
    print("\n" + "=" * 60)
    print("Attempting to count PDS employees...")
    print("=" * 60)
    
    # Try different possible column names for organization
    possible_queries = [
        # Try common organization column names
        """
        SELECT COUNT(*) as total_employees
        FROM human_resources.analytical_consumption.jll_worker_non_sensitive
        WHERE LOWER(organization) LIKE '%pds%'
           OR LOWER(business_unit) LIKE '%pds%'
           OR LOWER(org_name) LIKE '%pds%'
           OR LOWER(department) LIKE '%pds%'
        """,
        # Try without WHERE to get total count first
        """
        SELECT COUNT(*) as total_employees
        FROM human_resources.analytical_consumption.jll_worker_non_sensitive
        """,
    ]
    
    # First get total count
    print("\n1. Getting total employee count...")
    total_cols, total_results = execute_query("""
        SELECT COUNT(*) as total_employees
        FROM human_resources.analytical_consumption.jll_worker_non_sensitive
    """)
    print(f"Total employees in table: {total_results[0][0]:,}")
    
    # Now try to find PDS employees
    print("\n2. Searching for PDS employees...")
    
    # Get distinct values from likely organization columns
    for col in org_columns[:5]:  # Check first 5 org-related columns
        try:
            distinct_cols, distinct_results = execute_query(f"""
                SELECT DISTINCT {col}, COUNT(*) as count
                FROM human_resources.analytical_consumption.jll_worker_non_sensitive
                WHERE {col} IS NOT NULL
                GROUP BY {col}
                ORDER BY count DESC
                LIMIT 20
            """)
            print(f"\nDistinct values in '{col}':")
            for row in distinct_results:
                val = str(row[0])[:50] if row[0] else "NULL"
                print(f"  {val}: {row[1]:,} employees")
        except Exception as e:
            pass
    
    # Try to find PDS
    pds_queries = []
    for col in org_columns:
        pds_queries.append(f"LOWER({col}) LIKE '%pds%'")
    
    if pds_queries:
        where_clause = " OR ".join(pds_queries)
        pds_cols, pds_results = execute_query(f"""
            SELECT COUNT(*) as pds_employees
            FROM human_resources.analytical_consumption.jll_worker_non_sensitive
            WHERE {where_clause}
        """)
        print(f"\n{'=' * 60}")
        print(f"PDS Employees: {pds_results[0][0]:,}")
        print(f"{'=' * 60}")
    else:
        print("\nCould not find organization columns. Please check the table structure.")
        print("You may need to specify which column contains the organization information.")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

