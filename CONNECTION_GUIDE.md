# Databricks Connection Setup Guide

This guide will walk you through finding your Databricks connection details and configuring the connection.

## Quick Start

Run the interactive configuration script:
```bash
python3 configure_connection.py
```

This will guide you through each step. Or follow the manual steps below.

---

## Step-by-Step Instructions

### Step 1: Find Your Server Hostname

1. **Open your Databricks workspace** in a web browser
2. **Look at the URL** in your browser's address bar
3. **Copy the domain part** (everything after `https://` and before the first `/`)

**Examples:**
- URL: `https://adb-1234567890123456.7.azuredatabricks.net`
  - Server hostname: `adb-1234567890123456.7.azuredatabricks.net`

- URL: `https://your-workspace.cloud.databricks.com`
  - Server hostname: `your-workspace.cloud.databricks.com`

---

### Step 2: Find Your HTTP Path

1. In your Databricks workspace, click **"SQL Warehouses"** in the left sidebar
   - If you don't see it, you may need to switch to "SQL" persona (top left)
2. Click on your SQL Warehouse (or create one if you don't have one)
3. Click the **"Connection details"** tab
4. Find the **"HTTP path"** field
5. Copy the entire path

**Example:** `/sql/1.0/warehouses/abc123def456ghi789`

**Note:** If you don't have a SQL Warehouse:
- Click "SQL Warehouses" → "Create SQL Warehouse"
- Give it a name and configure settings
- Start the warehouse (it must be running to connect)

---

### Step 3: Get Your Access Token

1. Click your **user icon** (top right corner of Databricks)
2. Go to **"User Settings"**
3. Click the **"Access Tokens"** tab
4. Click **"Generate New Token"**
5. Fill in:
   - **Comment**: Give it a name (e.g., "EDP Connection" or "Python Script")
   - **Lifetime**: Set expiration (optional, or leave default 90 days)
6. Click **"Generate"**
7. **⚠️ COPY THE TOKEN IMMEDIATELY** - you won't be able to see it again!
8. Store it securely (we'll save it to `.env` file)

**Security Note:** 
- Tokens have the same permissions as your user account
- Don't share tokens or commit them to version control
- Regenerate tokens periodically for security

---

### Step 4: Configure Catalog and Schema (Optional)

**Catalog** and **Schema** specify which database to use by default.

- **Catalog**: Usually `hive_metastore` (default) or a Unity Catalog name
- **Schema**: Usually `default` (default) or a specific schema name

You can:
- Leave as defaults (`hive_metastore` and `default`)
- Change them later
- Override them in individual queries: `SELECT * FROM catalog.schema.table`

---

## Configuration Methods

### Method 1: Interactive Script (Easiest)

```bash
python3 configure_connection.py
```

This will guide you through all steps and create a `.env` file automatically.

### Method 2: Create .env File Manually

Create a file named `.env` in this directory:

```env
DATABRICKS_SERVER_HOSTNAME=adb-xxxxx.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx
DATABRICKS_ACCESS_TOKEN=your-token-here
DATABRICKS_CATALOG=hive_metastore
DATABRICKS_SCHEMA=default
```

Replace the values with your actual connection details.

### Method 3: Environment Variables

Set environment variables in your terminal:

```bash
export DATABRICKS_SERVER_HOSTNAME=adb-xxxxx.azuredatabricks.net
export DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx
export DATABRICKS_ACCESS_TOKEN=your-token-here
export DATABRICKS_CATALOG=hive_metastore
export DATABRICKS_SCHEMA=default
```

### Method 4: Edit edp_connection.py Directly

Edit the `EDP_CONFIG` dictionary in `edp_connection.py`:

```python
EDP_CONFIG = {
    "server_hostname": "adb-xxxxx.azuredatabricks.net",
    "http_path": "/sql/1.0/warehouses/xxxxx",
    "access_token": "your-token-here",
    "catalog": "hive_metastore",
    "schema": "default",
}
```

**Note:** This method is less secure as credentials are in code.

---

## Testing Your Connection

After configuring, test your connection:

```bash
python3 edp_connection.py
```

You should see:
```
✓ Connection successful!
Catalog: hive_metastore
Schema: default
User: your-email@jll.com
```

---

## Troubleshooting

### "Connection timeout" or "Cannot connect"
- ✅ Verify your SQL Warehouse is **running** (not stopped)
- ✅ Check if you're connected to VPN (if required by your organization)
- ✅ Verify server hostname is correct (no typos)

### "Authentication failed"
- ✅ Verify access token is correct (copy-paste carefully)
- ✅ Check if token has expired (generate a new one)
- ✅ Ensure token has proper permissions

### "Catalog not found" or "Schema not found"
- ✅ Use `list_catalogs()` to see available catalogs
- ✅ Use `list_schemas()` to see available schemas
- ✅ Default catalog is usually `hive_metastore`

### "Module not found" errors
- ✅ Install dependencies: `pip3 install -r requirements.txt`
- ✅ Make sure you're using Python 3.7+

### SSL/TLS errors
- ✅ Verify server hostname matches your workspace URL exactly
- ✅ Check if your organization requires VPN connection

---

## Security Best Practices

1. **Never commit `.env` file** to version control (it's in `.gitignore`)
2. **Never commit tokens** in code
3. **Regenerate tokens** periodically
4. **Use environment variables** or `.env` file (not hardcoded in scripts)
5. **Rotate tokens** if you suspect they're compromised

---

## Need Help?

If you're still having issues:
1. Check the error message carefully
2. Verify all connection details are correct
3. Ensure SQL Warehouse is running
4. Check if VPN is required
5. Contact your Databricks administrator if needed

