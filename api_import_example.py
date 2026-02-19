#!/usr/bin/env python3
"""
Example script to connect to an API and import data
Demonstrates API authentication, data fetching, and storage
"""

import requests
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
import csv

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API Configuration
API_CONFIG = {
    "base_url": os.getenv("API_BASE_URL", "https://api.example.com/v1"),
    "api_key": os.getenv("API_KEY", ""),
    "api_secret": os.getenv("API_SECRET", ""),
    "timeout": 30,  # seconds
    "max_retries": 3,
    "retry_delay": 1,  # seconds
}

class APIClient:
    """Client for making API requests with authentication and error handling"""
    
    def __init__(self, base_url: str, api_key: str = "", api_secret: str = "", 
                 timeout: int = 30, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        # Add authentication if provided
        if api_key:
            if api_secret:
                # Basic Auth
                self.session.auth = (api_key, api_secret)
            else:
                # API Key in header
                self.session.headers['X-API-Key'] = api_key
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, 
                     data: Dict = None, json_data: Dict = None) -> requests.Response:
        """Make an API request with retry logic"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=self.timeout
                )
                response.raise_for_status()  # Raise exception for bad status codes
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = API_CONFIG["retry_delay"] * (2 ** attempt)  # Exponential backoff
                    print(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
    
    def get(self, endpoint: str, params: Dict = None) -> Dict:
        """GET request"""
        response = self._make_request('GET', endpoint, params=params)
        return response.json()
    
    def post(self, endpoint: str, data: Dict = None, json_data: Dict = None) -> Dict:
        """POST request"""
        response = self._make_request('POST', endpoint, data=data, json_data=json_data)
        return response.json()
    
    def get_paginated(self, endpoint: str, params: Dict = None, 
                     page_param: str = 'page', per_page_param: str = 'per_page',
                     per_page: int = 100) -> List[Dict]:
        """Fetch all pages of paginated data"""
        all_data = []
        page = 1
        
        if params is None:
            params = {}
        
        params[per_page_param] = per_page
        
        while True:
            params[page_param] = page
            print(f"Fetching page {page}...")
            
            response_data = self.get(endpoint, params=params)
            
            # Adjust based on API response structure
            if isinstance(response_data, list):
                items = response_data
            elif isinstance(response_data, dict):
                # Common patterns: data, results, items, records
                items = response_data.get('data', 
                         response_data.get('results', 
                         response_data.get('items',
                         response_data.get('records', []))))
            else:
                items = []
            
            if not items:
                break
            
            all_data.extend(items)
            
            # Check if there are more pages
            if isinstance(response_data, dict):
                # Common pagination indicators
                has_more = (
                    response_data.get('has_more', False) or
                    response_data.get('next', None) is not None or
                    len(items) < per_page
                )
                if not has_more:
                    break
            
            page += 1
            time.sleep(0.5)  # Rate limiting
        
        return all_data


def save_to_json(data: List[Dict], filename: str):
    """Save data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"✓ Saved {len(data)} records to {filename}")


def save_to_csv(data: List[Dict], filename: str):
    """Save data to CSV file"""
    if not data:
        print("No data to save")
        return
    
    # Get all unique keys from all records
    fieldnames = set()
    for record in data:
        fieldnames.update(record.keys())
    fieldnames = sorted(list(fieldnames))
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✓ Saved {len(data)} records to {filename}")


def save_to_database(data: List[Dict], table_name: str = "api_imports"):
    """Save data to database (example using Databricks connection)"""
    try:
        from edp_connection import connect_to_edp
        
        conn = connect_to_edp()
        cursor = conn.cursor()
        
        # Example: Insert data (adjust based on your schema)
        for record in data:
            # Convert dict to SQL insert (simplified example)
            # In practice, you'd want to use parameterized queries
            columns = ', '.join(record.keys())
            values = ', '.join([f"'{str(v).replace(chr(39), chr(39)+chr(39))}'" for v in record.values()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            
            try:
                cursor.execute(query)
            except Exception as e:
                print(f"Error inserting record: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✓ Saved {len(data)} records to database table '{table_name}'")
        
    except ImportError:
        print("Database connection not available (edp_connection not found)")
    except Exception as e:
        print(f"Error saving to database: {e}")


def main():
    """Main function demonstrating API data import"""
    print("=" * 70)
    print("API Data Import Example")
    print("=" * 70)
    print()
    
    # Initialize API client
    client = APIClient(
        base_url=API_CONFIG["base_url"],
        api_key=API_CONFIG["api_key"],
        api_secret=API_CONFIG["api_secret"],
        timeout=API_CONFIG["timeout"],
        max_retries=API_CONFIG["max_retries"]
    )
    
    # Example 1: Simple GET request
    print("Example 1: Simple GET request")
    print("-" * 70)
    try:
        # Replace with your actual API endpoint
        data = client.get("/projects", params={"limit": 10})
        print(f"Fetched data: {json.dumps(data, indent=2)[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Example 2: Paginated data fetch
    print("Example 2: Fetching paginated data")
    print("-" * 70)
    try:
        # Fetch all pages
        all_projects = client.get_paginated("/projects", per_page=50)
        print(f"Total records fetched: {len(all_projects)}")
        
        # Save to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_to_json(all_projects, f"api_data_{timestamp}.json")
        save_to_csv(all_projects, f"api_data_{timestamp}.csv")
        
        # Optionally save to database
        # save_to_database(all_projects, "api_projects")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    print("=" * 70)
    print("Import complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()


