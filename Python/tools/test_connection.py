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
Test script for Databricks connection
This will check dependencies and test the connection
"""

import sys

def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    missing = []
    
    try:
        import dotenv
        print("✓ python-dotenv installed")
    except ImportError:
        missing.append("python-dotenv")
        print("✗ python-dotenv not installed")
    
    try:
        import databricks
        print("✓ databricks-sql-connector installed")
    except ImportError:
        missing.append("databricks-sql-connector")
        print("✗ databricks-sql-connector not installed")
    
    try:
        import azure.identity
        print("✓ azure-identity installed")
    except ImportError:
        missing.append("azure-identity")
        print("✗ azure-identity not installed")
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("Install with: pip3 install " + " ".join(missing))
        return False
    else:
        print("\n✓ All dependencies installed!")
        return True

def test_connection():
    """Test the Databricks connection"""
    print("\n" + "=" * 60)
    print("Testing Databricks Connection")
    print("=" * 60)
    
    try:
        from edp_connection import test_connection, EDP_CONFIG
        
        print(f"\nConfiguration:")
        print(f"  Server: {EDP_CONFIG['server_hostname']}")
        print(f"  HTTP Path: {EDP_CONFIG['http_path']}")
        print(f"  Catalog: {EDP_CONFIG['catalog']}")
        print(f"  Schema: {EDP_CONFIG['schema']}")
        print(f"  Auth: Azure AD (Interactive Browser)")
        print("\nAttempting connection...")
        print("(A browser window may open for authentication)\n")
        
        success = test_connection()
        
        if success:
            print("\n" + "=" * 60)
            print("✓ Connection test successful!")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("✗ Connection test failed")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your SQL Warehouse is running in Databricks")
        print("2. Check if you're connected to VPN (if required)")
        print("3. Verify server hostname and HTTP path are correct")
        print("4. Try signing in again when the browser opens")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("JLL EDP Databricks Connection Test")
    print("=" * 60)
    
    # Check dependencies first
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n⚠ Please install missing dependencies first:")
        print("   pip3 install -r requirements.txt")
        sys.exit(1)
    
    # Test connection
    success = test_connection()
    
    if success:
        print("\n🎉 You're ready to query Databricks!")
        print("\nNext steps:")
        print("  python3 example_usage.py  # See example queries")
        print("  python3 edp_connection.py  # Test connection again")
        sys.exit(0)
    else:
        sys.exit(1)


