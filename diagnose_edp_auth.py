#!/usr/bin/env python3
"""
Diagnose EDP/Databricks auth failures. Run from project root.

Checks:
  1. .env location and whether key vars are set (values masked)
  2. SSL connectivity to Azure (login.microsoftonline.com) – certificate errors
  3. Which auth method would be used and why others fail

After running, follow the suggested fix (e.g. set Service Principal in .env, or EDP_SSL_VERIFY=false).
"""

import os
import ssl
import sys

# Resolve project root (directory containing edp_connection.py and .env)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR
os.chdir(PROJECT_ROOT)

# Load .env from project root so we diagnose the same config the connection uses
try:
    from dotenv import load_dotenv
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.isfile(env_path):
        load_dotenv(env_path)
        print(f"[OK] Loaded .env from {env_path}")
    else:
        load_dotenv()  # current dir
        print(f"[--] No .env at {env_path} (using environment only)")
except Exception as e:
    print(f"[--] dotenv: {e}")

def mask(s):
    if not s or len(s) < 4:
        return "(empty)" if not s else "****"
    return s[:2] + "*" * (len(s) - 4) + s[-2:]

def main():
    print("EDP/Databricks auth diagnostic")
    print("=" * 60)

    # 1) Env vars
    print("\n1) Environment / .env")
    databricks_vars = [
        "DATABRICKS_SERVER_HOSTNAME",
        "DATABRICKS_HTTP_PATH",
        "DATABRICKS_USE_AZURE_AD",
        "DATABRICKS_ACCESS_TOKEN",
    ]
    azure_vars = ["AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "AZURE_TENANT_ID"]
    ssl_var = "EDP_SSL_VERIFY"
    for v in databricks_vars + azure_vars + [ssl_var]:
        val = os.getenv(v)
        if v == "DATABRICKS_ACCESS_TOKEN" or "SECRET" in v or "TOKEN" in v:
            display = "set (masked)" if val else "not set"
        elif val:
            display = mask(val) if len(val) > 8 else val
        else:
            display = "not set"
        print(f"   {v}: {display}")

    use_azure = (os.getenv("DATABRICKS_USE_AZURE_AD", "true").lower() == "true")
    has_sp = all(os.getenv(v) for v in azure_vars)
    has_token = bool(os.getenv("DATABRICKS_ACCESS_TOKEN"))

    print("\n2) Auth method that would be used")
    if not use_azure and has_token:
        print("   -> DATABRICKS_ACCESS_TOKEN (personal access token)")
    elif use_azure and has_sp:
        print("   -> Service Principal (AZURE_CLIENT_ID + SECRET + TENANT_ID)")
    elif use_azure:
        print("   -> DefaultAzureCredential (Azure CLI / Interactive Browser)")
        print("   -> Service Principal NOT configured (set AZURE_* in .env for headless/auth that works in Cursor)")
    else:
        print("   -> DATABRICKS_USE_AZURE_AD is false but no DATABRICKS_ACCESS_TOKEN set")

    # 3) SSL test to Azure
    print("\n3) SSL to login.microsoftonline.com")
    try:
        import urllib.request
        ctx = ssl.create_default_context()
        req = urllib.request.Request("https://login.microsoftonline.com/", method="HEAD")
        urllib.request.urlopen(req, timeout=10, context=ctx)
        print("   [OK] HTTPS request succeeded (no certificate error)")
    except ssl.SSLCertVerificationError as e:
        print("   [FAIL] Certificate verification failed (e.g. corporate proxy/self-signed cert)")
        print(f"          {e}")
        print("   Fix: In .env set EDP_SSL_VERIFY=false (dev/corporate only) or install your org's CA bundle.")
    except Exception as e:
        print(f"   [FAIL] {type(e).__name__}: {e}")

    # 4) Azure CLI / DefaultAzureCredential (no token request, just import and try get_token)
    print("\n4) DefaultAzureCredential (Azure CLI / env)")
    try:
        from azure.identity import DefaultAzureCredential
        cred = DefaultAzureCredential(
            exclude_visual_studio_code_credential=True,
            exclude_shared_token_cache_credential=True,
            exclude_managed_identity_credential=True,
        )
        tok = cred.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default")
        print("   [OK] Got token (Azure CLI or env credential)")
    except PermissionError as e:
        print("   [FAIL] Permission denied (e.g. Azure CLI cannot write to ~/.azure in this environment)")
        print(f"          {e}")
        print("   Fix: Use Service Principal in .env (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID).")
    except Exception as e:
        err = str(e)
        if "SSL" in err or "CERTIFICATE" in err:
            print("   [FAIL] SSL/certificate error during token request")
            print("   Fix: Set EDP_SSL_VERIFY=false in .env (or install corporate CA bundle).")
        else:
            print(f"   [FAIL] {err[:200]}")
        print("   Fix: Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID in .env for reliable auth.")

    # 5) Summary
    print("\n" + "=" * 60)
    print("Summary / recommended fix")
    if has_sp and use_azure:
        print("  Service Principal is set. If connection still fails, try EDP_SSL_VERIFY=false in .env")
    elif not has_sp and use_azure:
        print("  1) Add to .env: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID (Service Principal)")
        print("  2) If you see SSL/certificate errors, add: EDP_SSL_VERIFY=false")
    print("  Then run: python3 run_closed_projects_missing_budget_by_business_line.py (or other EDP script)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
