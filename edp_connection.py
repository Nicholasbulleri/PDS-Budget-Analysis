"""
JLL EDP Databricks Connection Script
Connects to JLL Enterprise Data Platform via Databricks SQL
"""

import os
from typing import Optional, List, Tuple

# Load .env from project root (directory containing this file) so cwd doesn't matter
_edp_dir = os.path.dirname(os.path.abspath(__file__))
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(_edp_dir, ".env")
    try:
        load_dotenv(_env_path)
    except (PermissionError, FileNotFoundError):
        load_dotenv()
except ImportError:
    pass

# Apply SSL verification bypass at import time so Azure token requests see it (corporate proxy)
if os.getenv("EDP_SSL_VERIFY", "true").lower() in ("false", "0", "no"):
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

# Databricks connection configuration
# Update these with your EDP Databricks credentials
# For JLL, we use Azure AD authentication (not personal access tokens)
EDP_CONFIG = {
    "server_hostname": os.getenv("DATABRICKS_SERVER_HOSTNAME", "adb-2797612873867894.14.azuredatabricks.net"),
    "http_path": os.getenv("DATABRICKS_HTTP_PATH", "/sql/1.0/warehouses/7c126f1ffa0e181e"),
    "catalog": os.getenv("DATABRICKS_CATALOG", "hive_metastore"),  # or specific catalog name
    "schema": os.getenv("DATABRICKS_SCHEMA", "default"),  # or specific schema name
    # Azure AD authentication (required for JLL)
    "use_azure_ad": os.getenv("DATABRICKS_USE_AZURE_AD", "true").lower() == "true",  # Default to true for JLL
    "azure_client_id": os.getenv("AZURE_CLIENT_ID", ""),
    "azure_client_secret": os.getenv("AZURE_CLIENT_SECRET", ""),
    "azure_tenant_id": os.getenv("AZURE_TENANT_ID", ""),
    # Fallback: Personal access token (if available, but typically not used at JLL)
    "access_token": os.getenv("DATABRICKS_ACCESS_TOKEN", ""),
}

def connect_databricks():
    """Connect to Databricks using databricks-sql-connector"""
    try:
        from databricks import sql
        
        connection_params = {
            "server_hostname": EDP_CONFIG["server_hostname"],
            "http_path": EDP_CONFIG["http_path"],
            "catalog": EDP_CONFIG["catalog"],
            "schema": EDP_CONFIG["schema"],
        }
        
        # Use Azure AD authentication (default for JLL)
        if EDP_CONFIG["use_azure_ad"]:
            try:
                from azure.identity import ClientSecretCredential, DefaultAzureCredential, InteractiveBrowserCredential
                
                # Try multiple authentication methods
                credential = None
                # Placeholder values from setup_option_a_env.py / .env.example – treat as "not set"
                _sp_placeholders = ("your-tenant-id", "your-client-id", "your-client-secret", "")
                _has_real_sp = (
                    EDP_CONFIG["azure_client_id"] and EDP_CONFIG["azure_client_id"] not in _sp_placeholders
                    and EDP_CONFIG["azure_client_secret"] and EDP_CONFIG["azure_client_secret"] not in _sp_placeholders
                    and EDP_CONFIG["azure_tenant_id"] and EDP_CONFIG["azure_tenant_id"] not in _sp_placeholders
                )
                # Method 1: Service Principal (Client ID/Secret) - for automated scripts
                if _has_real_sp:
                    credential = ClientSecretCredential(
                        tenant_id=EDP_CONFIG["azure_tenant_id"],
                        client_id=EDP_CONFIG["azure_client_id"],
                        client_secret=EDP_CONFIG["azure_client_secret"]
                    )
                    print("Using Azure AD Service Principal authentication")
                
                # Method 2: Default Azure Credential with same chain as analyze EDP / Teams agent
                # Prefer cached Azure CLI login (az login once) — exclude credentials that often
                # fail in restricted environments (VSCode, SharedTokenCache, ManagedIdentity)
                if not credential:
                    try:
                        credential = DefaultAzureCredential(
                            exclude_visual_studio_code_credential=True,
                            exclude_shared_token_cache_credential=True,
                            exclude_managed_identity_credential=True,
                        )
                        test_token = credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default")
                        print("Using Default Azure Credential (cached Azure CLI login)")
                    except Exception as e:
                        error_msg = str(e)
                        if "Operation not permitted" in error_msg or "Permission denied" in error_msg:
                            print("DefaultAzureCredential blocked by permissions, trying Interactive Browser...")
                        else:
                            print(f"DefaultAzureCredential failed: {error_msg[:120]}")
                        credential = None

                # Method 3: Interactive Browser (fallback; use once then az login cache works)
                if not credential:
                    try:
                        credential = InteractiveBrowserCredential()
                        print("Using Interactive Browser authentication - please sign in")
                    except Exception as e:
                        print(f"Interactive Browser credential failed: {e}")
                        credential = None

                if not credential:
                    raise ValueError(
                        "Azure AD authentication required but no valid method found.\n"
                        "Please provide either:\n"
                        "1. AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID (Service Principal)\n"
                        "2. Run 'az login' once, then scripts use cached Azure CLI login\n"
                        "3. Use InteractiveBrowserCredential (browser sign-in)"
                    )
                
                # Get Azure AD token for Databricks
                # Databricks Azure AD scope
                databricks_scope = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"
                token_response = credential.get_token(databricks_scope)
                connection_params["access_token"] = token_response.token
                
            except ImportError:
                print("Error: azure-identity not installed for Azure AD authentication.")
                print("Install with: pip install azure-identity")
                raise
        else:
            # Fallback: Use personal access token (if available)
            if EDP_CONFIG["access_token"]:
                connection_params["access_token"] = EDP_CONFIG["access_token"]
            else:
                raise ValueError(
                    "No authentication method configured.\n"
                    "For JLL, use Azure AD authentication by setting DATABRICKS_USE_AZURE_AD=true"
                )
        
        conn = sql.connect(**connection_params)
        return conn
    except ImportError as e:
        print("Error: databricks-sql-connector not installed.")
        print("Install with: pip install databricks-sql-connector")
        if EDP_CONFIG["use_azure_ad"]:
            print("For Azure AD: pip install azure-identity")
        raise
    except Exception as e:
        print(f"Connection error: {e}")
        err_str = str(e).lower()
        print("\nTroubleshooting:")
        if "ssl" in err_str or "certificate" in err_str:
            print("  SSL/certificate: Add EDP_SSL_VERIFY=false to .env (or install your org's CA bundle).")
        if "permission" in err_str or "operation not permitted" in err_str:
            print("  Permission: Use Service Principal in .env (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID).")
        print("  1. Run: python3 diagnose_edp_auth.py  (diagnose auth/SSL)")
        print("  2. Verify server_hostname and http_path (SQL Warehouse)")
        print("  3. For Azure AD: set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID in .env")
        print("  4. Check if SQL Warehouse is running")
        raise

def connect_to_edp():
    """Main connection function - connects to Databricks"""
    return connect_databricks()

def test_connection():
    """Test the Databricks connection"""
    try:
        conn = connect_to_edp()
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT current_catalog(), current_schema(), current_user()")
        result = cursor.fetchone()
        
        print(f"✓ Connection successful!")
        print(f"Catalog: {result[0]}")
        print(f"Schema: {result[1]}")
        print(f"User: {result[2]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
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
        conn = connect_to_edp()
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

def list_tables(catalog: Optional[str] = None, schema: Optional[str] = None) -> List[Tuple]:
    """List tables in the specified catalog and schema"""
    catalog = catalog or EDP_CONFIG["catalog"]
    schema = schema or EDP_CONFIG["schema"]
    
    query = f"""
    SHOW TABLES IN {catalog}.{schema}
    """
    columns, results = execute_query(query)
    return results

def list_schemas(catalog: Optional[str] = None) -> List[Tuple]:
    """List schemas in the specified catalog"""
    catalog = catalog or EDP_CONFIG["catalog"]
    
    query = f"""
    SHOW SCHEMAS IN {catalog}
    """
    columns, results = execute_query(query)
    return results

def list_catalogs() -> List[Tuple]:
    """List available catalogs"""
    query = "SHOW CATALOGS"
    columns, results = execute_query(query)
    return results

def describe_table(table_name: str, catalog: Optional[str] = None, schema: Optional[str] = None) -> List[Tuple]:
    """Get table schema/description"""
    catalog = catalog or EDP_CONFIG["catalog"]
    schema = schema or EDP_CONFIG["schema"]
    
    query = f"""
    DESCRIBE TABLE EXTENDED {catalog}.{schema}.{table_name}
    """
    columns, results = execute_query(query)
    return results

if __name__ == "__main__":
    print("JLL EDP Databricks Connection")
    print("=" * 50)
    print(f"Server: {EDP_CONFIG['server_hostname']}")
    print(f"HTTP Path: {EDP_CONFIG['http_path']}")
    print(f"Catalog: {EDP_CONFIG['catalog']}")
    print(f"Schema: {EDP_CONFIG['schema']}")
    print("=" * 50)
    
    # Test connection
    if test_connection():
        print("\n✓ Ready to query Databricks!")
        print("\nExample usage:")
        print("  from edp_connection import execute_query")
        print("  columns, results = execute_query('SELECT * FROM your_table LIMIT 10')")
