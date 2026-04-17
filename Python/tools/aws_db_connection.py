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
AWS MySQL Database Connection Script
Connects to AWS MySQL database server
"""

import os
from typing import Optional, List, Tuple

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    try:
        load_dotenv()
    except (PermissionError, FileNotFoundError):
        pass
except ImportError:
    pass

# AWS Database connection configuration
AWS_DB_CONFIG = {
    "host": os.getenv("AWS_DB_HOST", "1103.26.237.220"),
    "port": int(os.getenv("AWS_DB_PORT", "3306")),
    "database": os.getenv("AWS_DB_NAME", "jll_jll"),
    "user": os.getenv("AWS_DB_USER", "jll_uat_readonly"),
    "password": os.getenv("AWS_DB_PASSWORD", "dJQD]p?~@Um}Wzg3yw"),
}

def connect_aws_db():
    """Connect to AWS MySQL database"""
    try:
        # Try mysql-connector-python first (official MySQL connector)
        try:
            import mysql.connector
            from mysql.connector import Error
            
            connection = mysql.connector.connect(
                host=AWS_DB_CONFIG["host"],
                port=AWS_DB_CONFIG["port"],
                database=AWS_DB_CONFIG["database"],
                user=AWS_DB_CONFIG["user"],
                password=AWS_DB_CONFIG["password"],
                connect_timeout=10,
                autocommit=False
            )
            
            if connection.is_connected():
                print("✓ Connected to AWS MySQL database using mysql-connector-python")
                return connection
                
        except ImportError:
            # Fallback to pymysql
            try:
                import pymysql
                
                connection = pymysql.connect(
                    host=AWS_DB_CONFIG["host"],
                    port=AWS_DB_CONFIG["port"],
                    database=AWS_DB_CONFIG["database"],
                    user=AWS_DB_CONFIG["user"],
                    password=AWS_DB_CONFIG["password"],
                    connect_timeout=10,
                    autocommit=False
                )
                
                print("✓ Connected to AWS MySQL database using pymysql")
                return connection
                
            except ImportError:
                raise ImportError(
                    "No MySQL connector found. Install one of:\n"
                    "  pip install mysql-connector-python\n"
                    "  pip install pymysql"
                )
                
    except Exception as e:
        error_msg = str(e)
        print(f"✗ Connection failed: {error_msg}")
        print("\nTroubleshooting:")
        print("1. Verify the IP address and port are correct")
        print("2. Check if your IP is whitelisted in AWS security groups")
        print("3. Verify database credentials are correct")
        print("4. Check network connectivity to the database server")
        raise

def connect_to_aws_db():
    """Main connection function - connects to AWS MySQL database"""
    return connect_aws_db()

def test_connection():
    """Test the AWS database connection"""
    try:
        conn = connect_to_aws_db()
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT VERSION(), DATABASE(), USER()")
        result = cursor.fetchone()
        
        print(f"✓ Connection successful!")
        print(f"MySQL Version: {result[0]}")
        print(f"Database: {result[1]}")
        print(f"User: {result[2]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False

def execute_query(query: str, fetch_all: bool = True) -> Optional[Tuple[List[str], List[Tuple]]]:
    """
    Execute a SQL query and return results
    
    Args:
        query: SQL query string
        fetch_all: If True, fetch all results; if False, just execute (for DDL/DML)
    
    Returns:
        Tuple of (columns, results) if fetch_all=True, None otherwise
    """
    try:
        conn = connect_to_aws_db()
        cursor = conn.cursor()
        cursor.execute(query)
        
        if fetch_all:
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            cursor.close()
            conn.close()
            return columns, results
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return None
    except Exception as e:
        print(f"Query execution error: {e}")
        raise

def list_tables() -> List[str]:
    """List all tables in the database"""
    query = "SHOW TABLES"
    columns, results = execute_query(query)
    
    tables = []
    if results:
        for row in results:
            if len(row) > 0:
                tables.append(row[0])
    
    return tables

def describe_table(table_name: str) -> List[Tuple]:
    """Get table schema/description"""
    query = f"DESCRIBE {table_name}"
    columns, results = execute_query(query)
    return results

def get_table_info(table_name: str) -> dict:
    """Get detailed information about a table"""
    try:
        conn = connect_to_aws_db()
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute(f"DESCRIBE {table_name}")
        columns_info = cursor.fetchall()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        # Get table creation info
        cursor.execute(f"SHOW CREATE TABLE {table_name}")
        create_table = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "table_name": table_name,
            "columns": columns_info,
            "row_count": row_count,
            "create_statement": create_table[1] if create_table else None
        }
    except Exception as e:
        print(f"Error getting table info: {e}")
        raise

if __name__ == "__main__":
    print("AWS MySQL Database Connection")
    print("=" * 50)
    print(f"Host: {AWS_DB_CONFIG['host']}")
    print(f"Port: {AWS_DB_CONFIG['port']}")
    print(f"Database: {AWS_DB_CONFIG['database']}")
    print(f"User: {AWS_DB_CONFIG['user']}")
    print("=" * 50)
    
    # Test connection
    if test_connection():
        print("\n✓ Ready to query AWS database!")
        print("\nExample usage:")
        print("  from aws_db_connection import execute_query")
        print("  columns, results = execute_query('SELECT * FROM your_table LIMIT 10')")
        print("\nAvailable functions:")
        print("  - connect_to_aws_db() - Get connection object")
        print("  - execute_query(query) - Execute SQL query")
        print("  - list_tables() - List all tables")
        print("  - describe_table(table_name) - Get table schema")
        print("  - get_table_info(table_name) - Get detailed table info")

