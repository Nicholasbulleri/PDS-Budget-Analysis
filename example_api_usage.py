#!/usr/bin/env python3
"""
Practical example: Importing data from a REST API
This example shows real-world usage patterns
"""

from api_import_example import APIClient, save_to_json, save_to_csv
import json
from datetime import datetime

def example_github_api():
    """Example: Fetch GitHub repositories (public API, no auth needed)"""
    print("Example: GitHub API")
    print("=" * 70)
    
    client = APIClient(base_url="https://api.github.com")
    client.session.headers['User-Agent'] = 'DataImportScript/1.0'
    
    try:
        # Fetch repositories for a user
        repos = client.get("/users/octocat/repos", params={"per_page": 5})
        print(f"Fetched {len(repos)} repositories")
        print(f"First repo: {repos[0]['name'] if repos else 'None'}")
        
        # Save to file
        save_to_json(repos, "github_repos.json")
        
    except Exception as e:
        print(f"Error: {e}")


def example_jsonplaceholder_api():
    """Example: JSONPlaceholder API (fake REST API for testing)"""
    print("\nExample: JSONPlaceholder API")
    print("=" * 70)
    
    client = APIClient(base_url="https://jsonplaceholder.typicode.com")
    
    try:
        # Fetch posts
        posts = client.get("/posts", params={"_limit": 10})
        print(f"Fetched {len(posts)} posts")
        
        # Fetch comments for first post
        if posts:
            post_id = posts[0]['id']
            comments = client.get(f"/posts/{post_id}/comments")
            print(f"Fetched {len(comments)} comments for post {post_id}")
            
            # Combine data
            posts[0]['comments'] = comments
            
        # Save to files
        save_to_json(posts, "posts.json")
        save_to_csv(posts, "posts.csv")
        
    except Exception as e:
        print(f"Error: {e}")


def example_with_authentication():
    """Example: API with authentication (template)"""
    print("\nExample: Authenticated API")
    print("=" * 70)
    
    # Example with API key
    client = APIClient(
        base_url="https://api.example.com/v1",
        api_key="your-api-key-here"
    )
    
    try:
        # Make authenticated request
        data = client.get("/protected-endpoint")
        print(f"Fetched data: {len(data)} records")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This is a template - replace with your actual API")


def example_incremental_import():
    """Example: Incremental data import (only fetch new/updated records)"""
    print("\nExample: Incremental Import")
    print("=" * 70)
    
    client = APIClient(base_url="https://api.example.com/v1")
    
    # Load last sync timestamp
    last_sync_file = "last_sync.json"
    try:
        with open(last_sync_file, 'r') as f:
            last_sync = json.load(f)['timestamp']
    except FileNotFoundError:
        last_sync = None
    
    try:
        # Fetch only records updated since last sync
        params = {}
        if last_sync:
            params['updated_since'] = last_sync
        
        new_data = client.get("/projects", params=params)
        print(f"Fetched {len(new_data)} new/updated records")
        
        if new_data:
            # Save new data
            save_to_json(new_data, f"incremental_data_{datetime.now().strftime('%Y%m%d')}.json")
            
            # Update last sync timestamp
            with open(last_sync_file, 'w') as f:
                json.dump({'timestamp': datetime.now().isoformat()}, f)
            print("✓ Updated last sync timestamp")
        
    except Exception as e:
        print(f"Error: {e}")


def example_data_transformation():
    """Example: Transform API data before saving"""
    print("\nExample: Data Transformation")
    print("=" * 70)
    
    client = APIClient(base_url="https://api.example.com/v1")
    
    try:
        # Fetch raw data
        raw_data = client.get("/projects")
        
        # Transform data
        transformed = []
        for item in raw_data:
            transformed.append({
                'id': item.get('id'),
                'name': item.get('name', 'Unknown'),
                'status': item.get('status', 'unknown').upper(),
                'created_date': item.get('created_at', ''),
                'updated_date': item.get('updated_at', ''),
                # Add computed fields
                'is_active': item.get('status') == 'active',
                'days_since_update': (
                    (datetime.now() - datetime.fromisoformat(item.get('updated_at', '2000-01-01')))
                    .days if item.get('updated_at') else None
                )
            })
        
        print(f"Transformed {len(transformed)} records")
        save_to_csv(transformed, "transformed_data.csv")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("API Import Examples")
    print("=" * 70)
    print()
    
    # Run examples (comment out ones that require authentication)
    example_github_api()
    example_jsonplaceholder_api()
    # example_with_authentication()  # Uncomment and configure for your API
    # example_incremental_import()  # Uncomment and configure for your API
    # example_data_transformation()  # Uncomment and configure for your API
    
    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


