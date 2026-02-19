# AWS Database Connection Guide

This guide explains how to connect to the AWS MySQL database server.

## Connection Details

- **Host/IP**: 1103.26.237.220
- **Port**: 3306
- **Database**: jll_jll
- **Username**: jll_uat_readonly
- **Password**: dJQD]p?~@Um}Wzg3yw

## Installation

Install the required MySQL connector:

```bash
pip install mysql-connector-python
```

Or alternatively:

```bash
pip install pymysql
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Connection Test

```bash
python3 aws_db_connection.py
```

This will test the connection and display database information.

### Using in Python Scripts

```python
from aws_db_connection import connect_to_aws_db, execute_query, list_tables

# Execute a query
columns, results = execute_query("SELECT * FROM your_table LIMIT 10")
for row in results:
    print(row)

# List all tables
tables = list_tables()
print(f"Found {len(tables)} tables")

# Get table schema
schema = describe_table("your_table")
for column in schema:
    print(column)
```

### Direct Connection

```python
from aws_db_connection import connect_to_aws_db

conn = connect_to_aws_db()
cursor = conn.cursor()
cursor.execute("SELECT * FROM your_table LIMIT 10")
results = cursor.fetchall()

for row in results:
    print(row)

cursor.close()
conn.close()
```

## Environment Variables (Optional)

You can set these environment variables instead of hardcoding credentials:

```bash
export AWS_DB_HOST="1103.26.237.220"
export AWS_DB_PORT="3306"
export AWS_DB_NAME="jll_jll"
export AWS_DB_USER="jll_uat_readonly"
export AWS_DB_PASSWORD="dJQD]p?~@Um}Wzg3yw"
```

Or create a `.env` file:

```
AWS_DB_HOST=1103.26.237.220
AWS_DB_PORT=3306
AWS_DB_NAME=jll_jll
AWS_DB_USER=jll_uat_readonly
AWS_DB_PASSWORD=dJQD]p?~@Um}Wzg3yw
```

## Available Functions

- `connect_to_aws_db()` - Returns a database connection object
- `execute_query(query, fetch_all=True)` - Execute SQL and return results
- `list_tables()` - List all tables in the database
- `describe_table(table_name)` - Get table schema
- `get_table_info(table_name)` - Get detailed table information including row count

## Security Notes

⚠️ **Important Security Considerations:**

1. **Read-Only Access**: The user `jll_uat_readonly` has read-only access, so you cannot modify data
2. **IP Whitelisting**: Make sure your IP address is whitelisted in AWS security groups
3. **Credentials**: Never commit credentials to version control
4. **Environment Variables**: Use environment variables or `.env` files for credentials in production

## Troubleshooting

### Connection Timeout

If you get a connection timeout:
- Check if your IP is whitelisted in AWS security groups
- Verify the IP address and port are correct
- Check your network/firewall settings

### Authentication Failed

If authentication fails:
- Verify the username and password are correct
- Check if the user account is active
- Ensure you're connecting to the correct database

### Module Not Found

If you get "No module named 'mysql'":
```bash
pip install mysql-connector-python
```

Or:
```bash
pip install pymysql
```

## Example Queries

```python
from aws_db_connection import execute_query

# Get all tables
columns, tables = execute_query("SHOW TABLES")
print("Tables:", tables)

# Get table structure
columns, schema = execute_query("DESCRIBE your_table_name")
print("Schema:", schema)

# Count rows
columns, count = execute_query("SELECT COUNT(*) FROM your_table_name")
print("Row count:", count[0][0])

# Select data
columns, data = execute_query("SELECT * FROM your_table_name LIMIT 10")
for row in data:
    print(row)
```

