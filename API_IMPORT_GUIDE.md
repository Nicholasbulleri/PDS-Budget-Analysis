# API Data Import Guide

This guide shows how to use the API import script to fetch data from APIs and store it.

## Setup

1. **Install dependencies:**
   ```bash
   pip3 install -r api_import_requirements.txt
   ```

2. **Configure API credentials:**
   
   Create a `.env` file or set environment variables:
   ```env
   API_BASE_URL=https://api.example.com/v1
   API_KEY=your-api-key-here
   API_SECRET=your-api-secret-here
   ```

## Usage

### Basic Example

```python
from api_import_example import APIClient, save_to_json, save_to_csv

# Initialize client
client = APIClient(
    base_url="https://api.example.com/v1",
    api_key="your-api-key"
)

# Fetch data
data = client.get("/projects", params={"limit": 100})

# Save to file
save_to_json(data, "projects.json")
save_to_csv(data, "projects.csv")
```

### Paginated Data

```python
# Fetch all pages automatically
all_data = client.get_paginated("/projects", per_page=50)
print(f"Fetched {len(all_data)} total records")
```

### Authentication Methods

The script supports multiple authentication methods:

1. **API Key in Header:**
   ```python
   client = APIClient(base_url="...", api_key="your-key")
   ```

2. **Basic Authentication:**
   ```python
   client = APIClient(base_url="...", api_key="username", api_secret="password")
   ```

3. **Bearer Token:**
   ```python
   client.session.headers['Authorization'] = 'Bearer your-token'
   ```

## Features

- ✅ Automatic retry with exponential backoff
- ✅ Pagination support
- ✅ Error handling
- ✅ Multiple output formats (JSON, CSV, Database)
- ✅ Rate limiting protection
- ✅ Configurable timeouts

## Customization

### Custom Headers

```python
client.session.headers.update({
    'Custom-Header': 'value',
    'Authorization': 'Bearer token'
})
```

### Custom Authentication

```python
# OAuth 2.0 example
def get_oauth_token():
    # Your OAuth logic here
    return "access_token"

client.session.headers['Authorization'] = f'Bearer {get_oauth_token()}'
```

### Save to Database

```python
from api_import_example import save_to_database

# Save to Databricks (uses your edp_connection)
save_to_database(data, table_name="api_projects")
```

## Error Handling

The script includes automatic retry logic:
- Retries up to 3 times (configurable)
- Exponential backoff between retries
- Raises exception if all retries fail

## Example API Endpoints

### REST API Examples

```python
# GET request
data = client.get("/projects/123")

# GET with query parameters
data = client.get("/projects", params={"status": "active", "limit": 50})

# POST request
result = client.post("/projects", json_data={"name": "New Project"})
```

## Output Formats

1. **JSON:** Preserves nested data structure
2. **CSV:** Flat format, good for Excel/analysis
3. **Database:** Direct import to Databricks/SQL database

## Best Practices

1. **Rate Limiting:** Add delays between requests if needed
2. **Error Handling:** Always wrap API calls in try/except
3. **Data Validation:** Validate API responses before saving
4. **Incremental Updates:** Track last sync time to fetch only new data
5. **Logging:** Log API calls for debugging

## Troubleshooting

### "Connection timeout"
- Increase `timeout` in API_CONFIG
- Check network connectivity
- Verify API URL is correct

### "Authentication failed"
- Verify API key/secret are correct
- Check if token has expired
- Review API documentation for auth requirements

### "Rate limit exceeded"
- Add delays between requests: `time.sleep(1)`
- Reduce `per_page` size
- Use API's rate limit headers to pace requests


