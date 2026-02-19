# EDP connection – shared across agents

This project uses a **single Databricks/EDP connection** for all agents and scripts that query `work_dynamics.curated` (or related EDP data).

## Connection module

- **`edp_connection.py`** – shared by:
  - **Analyze EDP tables agent** (e.g. `analyze_ingenious_curated_views.py`, `analyze_curated_lineage.py`)
  - **Budget/curated query scripts** (e.g. `run_budget_query_curated.py`)

## Authentication (Azure CLI cached or Service Principal)

Auth order:

1. **Service principal** (recommended for Cursor/automation): set in `.env`:
   - `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
   - Avoids Azure CLI session writes and works when SSL is strict.
2. **Azure CLI cached**: run **`az login`** once; later runs use the cached token.
3. **Interactive browser**: used if the above are not available (can fail with SSL/certificate errors on corporate networks).

If you see **SSL: CERTIFICATE_VERIFY_FAILED** or **Operation not permitted** (e.g. in Cursor): set **`EDP_SSL_VERIFY=false`** in `.env` and use **Service Principal** (all three `AZURE_*` vars). Run **`python3 diagnose_edp_auth.py`** to confirm which method is used and what’s failing.

## Config (`.env`)

Loaded by `edp_connection` from the **project directory** (same folder as `edp_connection.py`):

- `DATABRICKS_SERVER_HOSTNAME`
- `DATABRICKS_HTTP_PATH`
- `DATABRICKS_USE_AZURE_AD=true`
- Optional: `DATABRICKS_CATALOG`, `DATABRICKS_SCHEMA`
- Optional for service principal: `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`
- **Auth/SSL issues:** `EDP_SSL_VERIFY=false` disables SSL verification for Azure token (e.g. corporate proxy). Use only in dev if needed.
- **Diagnose:** run `python3 diagnose_edp_auth.py` to see which auth method is used and why connection fails.

## Running curated queries (e.g. budget)

From this agent space, use the same connection:

```bash
# After 'az login' once (or with service principal in .env):
python3 run_budget_query_curated.py
BUDGET_QUERY_PHASE=closed python3 run_budget_query_curated.py   # Closed phase
BUDGET_QUERY_LIMIT=1000 python3 run_budget_query_curated.py    # Limit rows
```

In code: `from edp_connection import execute_query` then run SQL against `work_dynamics.curated.*`.
