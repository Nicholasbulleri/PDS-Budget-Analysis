"""
JLL EDP Databricks Connection Script
Connects to JLL Enterprise Data Platform via Databricks SQL.

Auth model (aligned with Databricks OAuth pattern):
  - Browser OAuth (dev): auth_type="databricks-oauth" — connector opens browser for login.
  - Service Principal (prod/automation): Azure AD client credentials or PAT fallback.
Respects DATABRICKS_INSECURE / EDP_SSL_VERIFY to disable SSL verification.
"""

import os
import time
import webbrowser
from contextlib import contextmanager
from typing import Optional, List, Tuple

# Project root for .env
_edp_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(_edp_dir, ".env")
    try:
        load_dotenv(_env_path)
    except (PermissionError, FileNotFoundError):
        load_dotenv()
except ImportError:
    pass

# SSL: apply at import time so OAuth and token requests see it (corporate proxy)
_INSECURE = (
    os.getenv("DATABRICKS_INSECURE", "").lower() in ("true", "1", "yes")
    or os.getenv("EDP_SSL_VERIFY", "true").lower() in ("false", "0", "no")
)
_SSL_WARNING_LOGGED = False


def _configure_ssl():
    global _SSL_WARNING_LOGGED
    if not _INSECURE:
        return
    if not _SSL_WARNING_LOGGED:
        _SSL_WARNING_LOGGED = True
        print("⚠️ [EDP] SSL verification disabled (DATABRICKS_INSECURE or EDP_SSL_VERIFY=false)")
    os.environ["REQUESTS_CA_BUNDLE"] = ""
    os.environ["CURL_CA_BUNDLE"] = ""
    os.environ["PYTHONHTTPSVERIFY"] = "0"
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass
    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
    except Exception:
        pass


_configure_ssl()

# Config: prefer DATABRICKS_* names (same as reference), fall back to existing EDP names
EDP_CONFIG = {
    "server_hostname": os.getenv("DATABRICKS_SERVER_HOSTNAME") or os.getenv("DATABRICKS_HOST") or "adb-2797612873867894.14.azuredatabricks.net",
    "http_path": os.getenv("DATABRICKS_HTTP_PATH") or "/sql/1.0/warehouses/7c126f1ffa0e181e",
    "catalog": os.getenv("DATABRICKS_CATALOG", "hive_metastore"),
    "schema": os.getenv("DATABRICKS_SCHEMA", "default"),
    "insecure": _INSECURE,
    # Auth mode: "browser" (Databricks OAuth) or "service_principal" (Azure AD / token)
    "auth_mode": (os.getenv("DATABRICKS_AUTH_MODE") or os.getenv("EDP_AUTH_MODE") or "browser").strip().lower() or "browser",
    # Service principal / token
    "client_id": os.getenv("DATABRICKS_CLIENT_ID") or os.getenv("AZURE_CLIENT_ID", ""),
    "client_secret": os.getenv("DATABRICKS_CLIENT_SECRET") or os.getenv("AZURE_CLIENT_SECRET", ""),
    "tenant_id": os.getenv("AZURE_TENANT_ID", ""),
    "access_token": os.getenv("DATABRICKS_ACCESS_TOKEN", "").strip() or None,
}
# OAuth browser options (same as reference)
EDP_CONFIG["oauth_redirect_port"] = int(os.getenv("DATABRICKS_OAUTH_REDIRECT_PORT", "8030"))
EDP_CONFIG["oauth_scopes"] = ["SQL", "WORKSPACE"]
EDP_CONFIG["oauth_background_tab"] = os.getenv("DATABRICKS_OAUTH_BACKGROUND_TAB", "true").lower() in ("true", "1", "yes")
EDP_CONFIG["oauth_auto_close_tab"] = os.getenv("DATABRICKS_OAUTH_AUTO_CLOSE_TAB", "true").lower() in ("true", "1", "yes")

# OAuth callback page: auto-close tab after login (same as reference)
_OAUTH_CALLBACK_AUTO_CLOSE_TEMPLATE = """<html>
<head>
  <title>Authentication complete</title>
  <style>body { font-family: system-ui; padding: 20px; background: #f3f3f3; }</style>
  <script>
    (() => {
      const closeSoon = () => {
        try { if (window.opener && !window.opener.closed) window.opener.focus(); } catch (e) {}
        try { window.open("", "_self"); window.close(); } catch (e) {}
      };
      setTimeout(closeSoon, 25);
      setTimeout(closeSoon, 250);
      setTimeout(closeSoon, 1000);
    })();
  </script>
</head>
<body><h1>Authentication complete.</h1><p>The application received a response. This tab should close automatically.</p></body>
</html>"""

# Connection cache (re-use connection until near expiry, like reference)
_CONNECTION = None
_CONNECTION_TOKEN_EXPIRES_AT: float = 0


def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


@contextmanager
def _browser_oauth_ux_context():
    """Optional: open auth in background tab and auto-close callback tab (same as reference)."""
    use_background = _bool_env("DATABRICKS_OAUTH_BACKGROUND_TAB", True)
    auto_close = _bool_env("DATABRICKS_OAUTH_AUTO_CLOSE_TAB", True)
    original_open_new = webbrowser.open_new
    try:
        from databricks.sql.auth.oauth_http_handler import OAuthHttpSingleRequestHandler
    except ImportError:
        OAuthHttpSingleRequestHandler = None
    original_template = getattr(OAuthHttpSingleRequestHandler, "RESPONSE_BODY_TEMPLATE", None) if OAuthHttpSingleRequestHandler else None

    try:
        if use_background:
            def _open_background(url: str):
                return webbrowser.open(url, new=2, autoraise=False)
            webbrowser.open_new = _open_background
        if auto_close and OAuthHttpSingleRequestHandler is not None:
            OAuthHttpSingleRequestHandler.RESPONSE_BODY_TEMPLATE = _OAUTH_CALLBACK_AUTO_CLOSE_TEMPLATE
        yield
    finally:
        webbrowser.open_new = original_open_new
        if OAuthHttpSingleRequestHandler is not None and original_template is not None:
            OAuthHttpSingleRequestHandler.RESPONSE_BODY_TEMPLATE = original_template


def connect_databricks():
    """Connect to Databricks using databricks-sql-connector. Uses browser OAuth or service principal/token."""
    global _CONNECTION, _CONNECTION_TOKEN_EXPIRES_AT
    try:
        from databricks import sql
    except ImportError:
        print("Error: databricks-sql-connector not installed. Install with: pip install databricks-sql-connector")
        raise

    now = time.time()
    # Re-use cached connection if still valid
    if _CONNECTION is not None and now < _CONNECTION_TOKEN_EXPIRES_AT:
        try:
            c = _CONNECTION.cursor()
            c.close()
            return _CONNECTION
        except Exception:
            _CONNECTION = None

    cfg = EDP_CONFIG
    base_params = {
        "server_hostname": cfg["server_hostname"],
        "http_path": cfg["http_path"],
        "catalog": cfg["catalog"],
        "schema": cfg["schema"],
    }
    verify_ssl = not cfg["insecure"]
    base_params["verify_ssl"] = verify_ssl
    if cfg["insecure"]:
        base_params["_tls_no_verify"] = True

    auth_mode = cfg["auth_mode"]
    # Explicit token (PAT) when set
    if cfg["access_token"]:
        base_params["access_token"] = cfg["access_token"]
        conn = sql.connect(**base_params)
        _CONNECTION = conn
        _CONNECTION_TOKEN_EXPIRES_AT = now + 3600
        return conn

    # Browser OAuth (Databricks native — same as reference; opens browser for login)
    if auth_mode == "browser":
        print("Connecting via Databricks OAuth — a browser window will open for login.")
        kwargs = {
            **base_params,
            "auth_type": "databricks-oauth",
            "oauth_redirect_port": cfg["oauth_redirect_port"],
            "oauth_scopes": cfg["oauth_scopes"],
            "verify_ssl": verify_ssl,
        }
        with _browser_oauth_ux_context():
            conn = sql.connect(**kwargs)
        _CONNECTION = conn
        _CONNECTION_TOKEN_EXPIRES_AT = now + 3600
        return conn

    # Service principal: Azure AD client credentials (no browser)
    _sp_placeholders = ("your-tenant-id", "your-client-id", "your-client-secret", "")
    has_sp = (
        cfg["client_id"] and cfg["client_id"] not in _sp_placeholders
        and cfg["client_secret"] and cfg["client_secret"] not in _sp_placeholders
    )
    if auth_mode == "service_principal" and has_sp:
        try:
            from azure.identity import ClientSecretCredential
            tenant = cfg["tenant_id"] or os.getenv("DATABRICKS_TENANT_ID", "")
            if not tenant or tenant in _sp_placeholders:
                raise ValueError("AZURE_TENANT_ID (or DATABRICKS_TENANT_ID) required for service principal.")
            cred = ClientSecretCredential(
                tenant_id=tenant,
                client_id=cfg["client_id"],
                client_secret=cfg["client_secret"],
            )
            scope = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"
            token = cred.get_token(scope)
            base_params["access_token"] = token.token
            base_params["verify_ssl"] = verify_ssl
            conn = sql.connect(**base_params)
            _CONNECTION = conn
            _CONNECTION_TOKEN_EXPIRES_AT = now + 3500  # a bit before expiry
            return conn
        except ImportError:
            print("Error: azure-identity required for service principal. Install: pip install azure-identity")
            raise
        except Exception as e:
            print(f"Service principal auth failed: {e}")
            raise

    # Fallback: try Azure AD chain (InteractiveBrowser, CLI, Default) for backward compatibility
    use_azure_ad = os.getenv("DATABRICKS_USE_AZURE_AD", "true").lower() == "true"
    if use_azure_ad:
        try:
            from azure.identity import (
                AzureCliCredential,
                ClientSecretCredential,
                DefaultAzureCredential,
                InteractiveBrowserCredential,
            )
            credential = None
            _has_sp = (
                cfg["client_id"] and cfg["client_id"] not in _sp_placeholders
                and cfg["client_secret"] and cfg["client_secret"] not in _sp_placeholders
                and cfg["tenant_id"] and cfg["tenant_id"] not in _sp_placeholders
            )
            if _has_sp:
                credential = ClientSecretCredential(
                    tenant_id=cfg["tenant_id"],
                    client_id=cfg["client_id"],
                    client_secret=cfg["client_secret"],
                )
                print("Using Azure AD Service Principal.")
            if not credential:
                try:
                    print("Opening browser for Azure AD sign-in — please complete login in the browser window.")
                    credential = InteractiveBrowserCredential()
                    credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default")
                except Exception as e:
                    if "SSL" in str(e) or "certificate" in str(e):
                        print("Interactive Browser failed (SSL). Set DATABRICKS_INSECURE=true or EDP_SSL_VERIFY=false.")
                    credential = None
            if not credential:
                try:
                    credential = AzureCliCredential()
                    credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default")
                    print("Using Azure CLI (az login).")
                except Exception:
                    credential = None
            if not credential:
                credential = DefaultAzureCredential(
                    exclude_visual_studio_code_credential=True,
                    exclude_shared_token_cache_credential=True,
                    exclude_managed_identity_credential=True,
                )
                credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default")
            scope = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"
            token_response = credential.get_token(scope)
            base_params["access_token"] = token_response.token
            base_params["verify_ssl"] = verify_ssl
            conn = sql.connect(**base_params)
            _CONNECTION = conn
            _CONNECTION_TOKEN_EXPIRES_AT = now + 3500
            return conn
        except ImportError:
            print("Error: azure-identity not installed. Install: pip install azure-identity")
            raise

    raise ValueError(
        "No authentication method available.\n"
        "  - Browser (recommended): set DATABRICKS_AUTH_MODE=browser — run script and sign in in the browser.\n"
        "  - Service principal: set DATABRICKS_AUTH_MODE=service_principal and AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET in .env.\n"
        "  - Or set DATABRICKS_ACCESS_TOKEN for a personal access token."
    )


def connect_to_edp():
    """Main entry: connect to EDP Databricks."""
    return connect_databricks()


def test_connection():
    """Test the Databricks connection."""
    try:
        conn = connect_to_edp()
        cursor = conn.cursor()
        cursor.execute("SELECT current_catalog(), current_schema(), current_user()")
        result = cursor.fetchone()
        print(f"✓ Connection successful! Catalog: {result[0]}, Schema: {result[1]}, User: {result[2]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def execute_query(query: str, fetch_all: bool = True) -> Optional[Tuple[List[str], List[Tuple]]]:
    """Execute a SQL query and return (columns, rows) or None for DDL/DML."""
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
        conn.commit()
        cursor.close()
        conn.close()
        return None
    except Exception as e:
        print(f"Query execution error: {e}")
        raise


def list_tables(catalog: Optional[str] = None, schema: Optional[str] = None) -> List[Tuple]:
    catalog = catalog or EDP_CONFIG["catalog"]
    schema = schema or EDP_CONFIG["schema"]
    cols, rows = execute_query(f"SHOW TABLES IN {catalog}.{schema}")
    return rows or []


def list_schemas(catalog: Optional[str] = None) -> List[Tuple]:
    catalog = catalog or EDP_CONFIG["catalog"]
    cols, rows = execute_query(f"SHOW SCHEMAS IN {catalog}")
    return rows or []


def list_catalogs() -> List[Tuple]:
    cols, rows = execute_query("SHOW CATALOGS")
    return rows or []


def describe_table(table_name: str, catalog: Optional[str] = None, schema: Optional[str] = None) -> List[Tuple]:
    catalog = catalog or EDP_CONFIG["catalog"]
    schema = schema or EDP_CONFIG["schema"]
    cols, rows = execute_query(f"DESCRIBE TABLE EXTENDED {catalog}.{schema}.{table_name}")
    return rows or []


if __name__ == "__main__":
    print("JLL EDP Databricks Connection")
    print("=" * 50)
    print(f"Server: {EDP_CONFIG['server_hostname']}")
    print(f"HTTP Path: {EDP_CONFIG['http_path']}")
    print(f"Auth mode: {EDP_CONFIG['auth_mode']}")
    print("=" * 50)
    if test_connection():
        print("\n✓ Ready to query Databricks!")
        print("  from edp_connection import execute_query")
        print("  columns, results = execute_query('SELECT * FROM your_table LIMIT 10')")
