#!/usr/bin/env python3
"""
Add Option A (Service Principal + SSL bypass) placeholder lines to .env if missing.
Run once, then replace your-tenant-id, your-client-id, your-client-secret with real values.
Does not overwrite existing values.
"""
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")

LINES_TO_ADD = [
    "",
    "# Option A: Service Principal + SSL bypass (replace placeholders with real values)",
    "AZURE_TENANT_ID=your-tenant-id",
    "AZURE_CLIENT_ID=your-client-id",
    "AZURE_CLIENT_SECRET=your-client-secret",
    "EDP_SSL_VERIFY=false",
]

def main():
    existing = set()
    if os.path.isfile(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key = line.split("=", 1)[0].strip()
                    existing.add(key)
    else:
        open(ENV_PATH, "a").close()

    keys_to_add = ["AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET", "EDP_SSL_VERIFY"]
    missing = [k for k in keys_to_add if k not in existing]
    if not missing:
        print(".env already has Option A keys. Replace their values with real credentials if needed.")
        return 0

    with open(ENV_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(LINES_TO_ADD) + "\n")
    print(f"Added Option A placeholders to {ENV_PATH}")
    print("Next: replace your-tenant-id, your-client-id, your-client-secret with real values.")
    print("Then run: python3 diagnose_edp_auth.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
