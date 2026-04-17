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
Test different IP address formats for AWS database connection
"""

import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    "port": 3306,
    "database": "jll_jll",
    "user": "jll_uat_readonly",
    "password": "dJQD]p?~@Um}Wzg3yw",
}

# Possible IP address variations to try
possible_hosts = [
    "10.3.26.237",      # Most likely - removing "1" and "0" from start
    "110.3.26.237",     # Removing just "1"
    "10.3.26.237.220",  # Original with dot separation
    "1103.26.237.220",  # Original (invalid but let's try)
    "10.26.237.220",    # Removing "3"
    "103.26.237.220",   # Removing first "1"
]

print("Testing AWS Database Connection with Different IP Formats")
print("=" * 60)
print(f"Database: {DB_CONFIG['database']}")
print(f"User: {DB_CONFIG['user']}")
print(f"Port: {DB_CONFIG['port']}")
print("=" * 60)
print()

for host in possible_hosts:
    print(f"Trying host: {host}...", end=" ")
    try:
        connection = mysql.connector.connect(
            host=host,
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            connect_timeout=5
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION(), DATABASE(), USER()")
            result = cursor.fetchone()
            
            print("✓ SUCCESS!")
            print(f"  MySQL Version: {result[0]}")
            print(f"  Database: {result[1]}")
            print(f"  User: {result[2]}")
            
            # Get table count
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"  Tables found: {len(tables)}")
            
            cursor.close()
            connection.close()
            print(f"\n✓ Working host: {host}")
            break
    except Error as e:
        error_msg = str(e)
        if "Unknown MySQL server host" in error_msg:
            print("✗ Host not found")
        elif "Access denied" in error_msg:
            print("✗ Access denied (host might be correct but credentials/whitelist issue)")
        elif "timed out" in error_msg.lower():
            print("✗ Connection timeout (host might be correct but not accessible)")
        else:
            print(f"✗ Error: {error_msg[:60]}")
    except Exception as e:
        print(f"✗ Error: {str(e)[:60]}")
    print()

print("\n" + "=" * 60)
print("Connection test complete")

