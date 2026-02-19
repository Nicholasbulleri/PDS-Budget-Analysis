# JLL EDP Databricks Connection

This project provides a Python script to connect to the JLL Enterprise Data Platform (EDP) via Databricks SQL.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Get your Databricks connection details:**
   - **Server Hostname**: Found in your Databricks workspace URL
     - Format: `adb-xxxxx.azuredatabricks.net` or `your-workspace.cloud.databricks.com`
   - **HTTP Path**: Found in SQL Warehouse connection details
     - Format: `/sql/1.0/warehouses/xxxxx`
   - **Access Token**: Personal Access Token from Databricks
     - Go to User Settings → Access Tokens → Generate New Token

3. **Configure your connection:**
   
   **Option A: Environment Variables (Recommended)**
   ```bash
   export DATABRICKS_SERVER_HOSTNAME=adb-xxxxx.azuredatabricks.net
   export DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx
   export DATABRICKS_ACCESS_TOKEN=your-token-here
   export DATABRICKS_CATALOG=hive_metastore
   export DATABRICKS_SCHEMA=default
   ```
   
   **Option B: Edit `edp_connection.py`**
   - Update the `EDP_CONFIG` dictionary with your credentials

   **Option C: Create `.env` file**
   ```env
   DATABRICKS_SERVER_HOSTNAME=adb-xxxxx.azuredatabricks.net
   DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx
   DATABRICKS_ACCESS_TOKEN=your-token-here
   DATABRICKS_CATALOG=hive_metastore
   DATABRICKS_SCHEMA=default
   ```

## Usage

### Test Connection
```bash
python3 edp_connection.py
```

### Basic Query
```python
from edp_connection import execute_query

# Execute a query
columns, results = execute_query("SELECT * FROM your_table LIMIT 10")

# Print results
for row in results:
    print(row)
```

### List Available Resources
```python
from edp_connection import list_catalogs, list_schemas, list_tables

# List catalogs
catalogs = list_catalogs()
print("Catalogs:", catalogs)

# List schemas in a catalog
schemas = list_schemas("hive_metastore")
print("Schemas:", schemas)

# List tables in a schema
tables = list_tables("hive_metastore", "default")
print("Tables:", tables)
```

### Describe Table
```python
from edp_connection import describe_table

# Get table schema
schema_info = describe_table("your_table_name")
for row in schema_info:
    print(row)
```

### Using Connection Directly
```python
from edp_connection import connect_to_edp

conn = connect_to_edp()
cursor = conn.cursor()

cursor.execute("SELECT * FROM your_table LIMIT 10")
results = cursor.fetchall()

for row in results:
    print(row)

cursor.close()
conn.close()
```

## Azure AD Authentication

If your organization uses Azure AD authentication instead of personal access tokens:

1. **Install Azure Identity package:**
   ```bash
   pip install azure-identity
   ```

2. **Set environment variables:**
   ```bash
   export DATABRICKS_USE_AZURE_AD=true
   export AZURE_CLIENT_ID=your-client-id
   export AZURE_CLIENT_SECRET=your-client-secret
   export AZURE_TENANT_ID=your-tenant-id
   ```

## Finding Your Connection Details

### Server Hostname
- Look at your Databricks workspace URL
- Example: If URL is `https://adb-1234567890123456.7.azuredatabricks.net`
- Server hostname is: `adb-1234567890123456.7.azuredatabricks.net`

### HTTP Path
1. Go to your Databricks workspace
2. Click **SQL Warehouses** in the sidebar
3. Select your warehouse
4. Click **Connection details**
5. Copy the **Server hostname** and **HTTP path**

### Access Token
1. Click your user icon (top right)
2. Go to **User Settings**
3. Click **Access Tokens**
4. Click **Generate New Token**
5. Copy the token (you won't see it again!)

## Security Notes

- **Never commit `.env` file or tokens to version control**
- Access tokens expire - regenerate as needed
- Use environment variables or secure credential storage
- Consider using Azure Key Vault for production

## Troubleshooting

### Connection Timeout
- Verify your SQL Warehouse is running (not stopped)
- Check firewall/VPN settings
- Verify server hostname is correct

### Authentication Failed
- Verify access token is valid and not expired
- Check if token has proper permissions
- For Azure AD: Verify client ID, secret, and tenant ID

### "Catalog not found" or "Schema not found"
- Verify catalog and schema names are correct
- Use `list_catalogs()` and `list_schemas()` to see available options
- Default catalog is usually `hive_metastore`

### SSL/TLS Errors
- Ensure you're using the correct server hostname
- Check if your organization requires VPN connection

## Example Queries

```python
from edp_connection import execute_query

# Query with LIMIT
columns, results = execute_query("""
    SELECT 
        column1,
        column2,
        COUNT(*) as count
    FROM your_table
    WHERE date_column >= '2024-01-01'
    GROUP BY column1, column2
    LIMIT 100
""")

# Query specific catalog/schema
columns, results = execute_query("""
    SELECT * 
    FROM catalog_name.schema_name.table_name 
    LIMIT 10
""")
```
