# Option A: Service Principal + SSL bypass (recommended for Cursor/automation)

Use this when you see **SSL: CERTIFICATE_VERIFY_FAILED** or **Operation not permitted** (e.g. when running EDP scripts from Cursor).

**Note:** If you leave the placeholder values in `.env` (your-tenant-id, your-client-id, your-client-secret), the connection will **ignore** them and use Azure CLI / Interactive Browser as before. So adding Option A lines does not break your existing working auth.

## 1. Add these to your `.env` file

Append (or add) these lines to `.env` in this project. Replace the placeholders with your real values.

```env
# Service Principal (get from IT/Databricks admin or create in Azure Portal – see AZURE_AD_SETUP.md)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Bypass SSL verification for Azure token (needed behind corporate proxy)
EDP_SSL_VERIFY=false
```

- **AZURE_TENANT_ID** – Azure AD tenant (directory) ID  
- **AZURE_CLIENT_ID** – App (client) ID of the service principal / app registration  
- **AZURE_CLIENT_SECRET** – Client secret value (create under Certificates & secrets)

If you don’t have these yet, see **AZURE_AD_SETUP.md** (Method 3: Service Principal) or ask your IT/Databricks admin.

## 2. Verify

```bash
python3 diagnose_edp_auth.py
```

You should see “Service Principal (AZURE_CLIENT_ID + SECRET + TENANT_ID)” and no SSL or permission failures.

## 3. Run EDP scripts

```bash
python3 run_closed_projects_missing_budget_by_business_line.py
# or
python3 run_budget_query_closed_by_category_with_state_using_mapping.py
```

Your existing `DATABRICKS_SERVER_HOSTNAME` and `DATABRICKS_HTTP_PATH` in `.env` stay as they are; Option A only adds the Azure SP vars and `EDP_SSL_VERIFY=false`.
