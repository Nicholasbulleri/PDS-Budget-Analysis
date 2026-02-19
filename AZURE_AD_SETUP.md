# Azure AD Authentication Setup for JLL Databricks

Since JLL doesn't use personal access tokens, you'll need to configure Azure AD authentication. This guide covers the different methods available.

## Authentication Methods

### Method 1: Interactive Browser (Easiest for Local Development)

**Best for:** Local development and testing

This method opens a browser window for you to sign in with your JLL credentials.

**Setup:**
1. No additional configuration needed
2. Just run: `python3 edp_connection.py`
3. A browser window will open for you to sign in
4. After signing in, you'll be connected

**Requirements:**
- You must be able to open a browser on your machine
- You'll need to sign in with your JLL Azure AD credentials

---

### Method 2: Default Azure Credential

**Best for:** When you're already logged into Azure CLI or running on Azure

This method uses your existing Azure CLI login or managed identity.

**Setup:**
1. Install Azure CLI: `brew install azure-cli` (macOS)
2. Log in: `az login`
3. Select your JLL account when prompted
4. The connection script will automatically use this credential

**Requirements:**
- Azure CLI installed and logged in
- Or running on Azure with managed identity configured

---

### Method 3: Service Principal (Client ID/Secret)

**Best for:** Automated scripts, CI/CD, production environments

This method uses a service principal with client ID and secret.

**Getting Service Principal Credentials:**

You'll need to contact your IT/Data team or Databricks administrator to get:
1. **Azure Tenant ID** - Your organization's Azure AD tenant ID
2. **Azure Client ID** - Application (client) ID of the service principal
3. **Azure Client Secret** - Secret value for the service principal

**Or create your own App Registration:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Fill in:
   - Name: e.g., "Databricks EDP Connection"
   - Supported account types: Accounts in this organizational directory only
   - Redirect URI: Leave blank (not needed for this use case)
5. Click **Register**
6. Note the **Application (client) ID** and **Directory (tenant) ID**
7. Go to **Certificates & secrets**
8. Click **New client secret**
9. Add description and expiration
10. Click **Add** and **copy the secret value** (you won't see it again!)
11. Grant API permissions:
    - Go to **API permissions**
    - Click **Add a permission**
    - Select **Azure Databricks**
    - Add **user_impersonation** permission
    - Click **Grant admin consent** (may require admin approval)

**Configuration:**

Add to your `.env` file:
```env
DATABRICKS_USE_AZURE_AD=true
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

---

## Quick Setup

### Option A: Interactive Configuration Script

Run the Azure AD-specific configuration script:
```bash
python3 configure_connection_azure.py
```

### Option B: Manual Configuration

1. **Get your Databricks connection details:**
   - Server hostname: From your Databricks workspace URL
   - HTTP path: From SQL Warehouse → Connection details

2. **Choose authentication method:**
   - **Easiest**: Use Interactive Browser (no setup needed)
   - **If using Azure CLI**: Run `az login` first
   - **For automation**: Get Service Principal credentials from IT

3. **Create `.env` file:**
   ```env
   DATABRICKS_SERVER_HOSTNAME=adb-xxxxx.azuredatabricks.net
   DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx
   DATABRICKS_USE_AZURE_AD=true
   DATABRICKS_CATALOG=hive_metastore
   DATABRICKS_SCHEMA=default
   
   # For Service Principal (if using Method 3):
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_CLIENT_SECRET=your-client-secret
   ```

4. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Test connection:**
   ```bash
   python3 edp_connection.py
   ```

---

## Troubleshooting

### "No authentication method found"
- Make sure `DATABRICKS_USE_AZURE_AD=true` in your `.env` file
- For Service Principal: Verify all three Azure credentials are set
- For Default: Make sure you're logged in with `az login`

### "Interactive browser authentication failed"
- Make sure you can open a browser
- Check if pop-ups are blocked
- Verify your JLL credentials are correct

### "Service principal authentication failed"
- Verify Tenant ID, Client ID, and Secret are correct
- Check if the service principal has proper permissions
- Ensure the secret hasn't expired
- Contact your IT team to verify the service principal is active

### "Default credential not found"
- Run `az login` to authenticate with Azure CLI
- Or configure managed identity if running on Azure
- Check if you have the right Azure subscription selected

### "Permission denied" or "Access denied"
- Verify your Azure AD account has access to Databricks
- Check if the service principal has been granted access
- Contact your Databricks administrator

---

## Security Notes

1. **Never commit `.env` file** to version control
2. **Never commit Azure secrets** in code
3. **Rotate service principal secrets** periodically
4. **Use least privilege** - only grant necessary permissions
5. **Use managed identity** when running on Azure (most secure)

---

## Need Help?

If you're having issues:
1. Check which authentication method you're using
2. Verify all required credentials are set
3. Test with Interactive Browser first (easiest)
4. Contact your Databricks administrator or IT team
5. Check Azure Portal for service principal status

