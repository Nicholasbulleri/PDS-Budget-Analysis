"""
Example usage of the JLL EDP Databricks connection
"""

from edp_connection import (
    execute_query,
    list_catalogs,
    list_schemas,
    list_tables,
    describe_table
)

def main():
    print("JLL EDP Databricks - Example Usage\n")
    
    # Example 1: List available catalogs
    print("1. Listing available catalogs...")
    try:
        catalogs = list_catalogs()
        print(f"   Found {len(catalogs)} catalog(s):")
        for catalog in catalogs:
            print(f"   - {catalog[0]}")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Example 2: List schemas in a catalog
    print("\n2. Listing schemas in 'hive_metastore'...")
    try:
        schemas = list_schemas("hive_metastore")
        print(f"   Found {len(schemas)} schema(s):")
        for schema in schemas[:10]:  # Show first 10
            print(f"   - {schema[0]}")
        if len(schemas) > 10:
            print(f"   ... and {len(schemas) - 10} more")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Example 3: List tables in a schema
    print("\n3. Listing tables in 'default' schema...")
    try:
        tables = list_tables("hive_metastore", "default")
        print(f"   Found {len(tables)} table(s):")
        for table in tables[:10]:  # Show first 10
            print(f"   - {table[1]}")  # Table name is usually in second column
        if len(tables) > 10:
            print(f"   ... and {len(tables) - 10} more")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Example 4: Execute a simple query
    print("\n4. Executing a test query...")
    try:
        columns, results = execute_query("SELECT current_catalog(), current_schema(), current_user()")
        print(f"   Columns: {columns}")
        print(f"   Results: {results[0]}")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # Example 5: Query a specific table (uncomment and modify as needed)
    # print("\n5. Querying a specific table...")
    # try:
    #     columns, results = execute_query("""
    #         SELECT * 
    #         FROM your_catalog.your_schema.your_table 
    #         LIMIT 10
    #     """)
    #     print(f"   Columns: {columns}")
    #     print(f"   Rows returned: {len(results)}")
    #     for row in results[:5]:  # Show first 5 rows
    #         print(f"   {row}")
    # except Exception as e:
    #     print(f"   Error: {e}\n")
    
    print("\n✓ Examples complete!")

if __name__ == "__main__":
    main()

