# Connecting Power BI to Databricks

## Quick Setup Guide

### Prerequisites
- Power BI Desktop installed
- Access to Databricks workspace
- Databricks connection details (server hostname, HTTP path)

### Connection Steps

1. **Open Power BI Desktop**
   - Launch Power BI Desktop application

2. **Get Data**
   - Click **Get Data** button
   - Select **Azure** → **Azure Databricks**
   - Click **Connect**

3. **Enter Connection Details**
   - **Server Hostname**: `adb-2797612873867894.14.azuredatabricks.net`
   - **HTTP Path**: `/sql/1.0/warehouses/7c126f1ffa0e181e`
   - Click **OK**

4. **Authentication**
   - **Authentication Method**: Select **Microsoft account** (for Azure AD)
   - Click **Sign in**
   - Complete Azure AD authentication in browser
   - Click **Connect**

5. **Select Data**
   - Navigate to desired catalog (e.g., `work_dynamics`)
   - Select schema (e.g., `curated_consumption`)
   - Choose tables/views to import
   - Click **Load** or **Transform Data**

## Connection Details for JLL EDP

- **Server Hostname**: `adb-2797612873867894.14.azuredatabricks.net`
- **HTTP Path**: `/sql/1.0/warehouses/7c126f1ffa0e181e`
- **Authentication**: Microsoft account (Azure AD)

## Alternative: Direct SQL Connection

If Azure Databricks connector is not available:

1. **Get Data** → **Database** → **SQL Server database**
2. Enter connection details:
   - **Server**: `adb-2797612873867894.14.azuredatabricks.net`
   - **Database**: Leave empty or use catalog name
   - **Data Connectivity mode**: Import or DirectQuery
3. **Authentication**: Microsoft account
4. In advanced options, add: `ServerProtocol=HTTP;Path=/sql/1.0/warehouses/7c126f1ffa0e181e`

## Tips

- **DirectQuery vs Import**: 
  - Use **DirectQuery** for large datasets or real-time data
  - Use **Import** for better performance with smaller datasets
  
- **Authentication**: 
  - Azure AD authentication is required for JLL
  - You may need to sign in multiple times if session expires
  
- **Performance**:
  - Consider using DirectQuery for large tables
  - Use query folding to push transformations to Databricks
  - Filter data at source when possible

## Troubleshooting

- **Connection timeout**: Check network connectivity and firewall settings
- **Authentication errors**: Ensure Azure AD access is granted
- **Path not found**: Verify HTTP path is correct for your SQL warehouse
- **Catalog not visible**: Ensure you have access permissions to the catalog

