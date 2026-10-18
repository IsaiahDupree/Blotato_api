import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.youtube_test')

def test_auth_methods():
    """Test different authentication methods with the Blotato API."""
    api_key = os.getenv('BLOTATO_API_KEY')
    base_url = os.getenv('BLOTATO_API_URL', 'https://backend.blotato.com/v2')
    
    print(f"Testing authentication with base URL: {base_url}")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    
    # Define endpoints to test
    endpoints = [
        '/media',  # From the documentation
        '/health',  # Common health check endpoint
        '/',        # Root endpoint
    ]
    
    # Define different auth methods to try
    auth_methods = [
        {"name": "No Auth", "headers": {"Content-Type": "application/json"}},
        {"name": "API Key as Bearer Token", "headers": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}},
        {"name": "API Key directly", "headers": {"Authorization": f"{api_key}", "Content-Type": "application/json"}},
        {"name": "API Key as X-API-Key", "headers": {"X-API-Key": f"{api_key}", "Content-Type": "application/json"}},
        {"name": "API Key as api_key param", "params": {"api_key": api_key}, "headers": {"Content-Type": "application/json"}},
    ]
    
    for endpoint in endpoints:
        print(f"\n=== Testing endpoint: {endpoint} ===")
        
        for auth in auth_methods:
            print(f"\n-- Using {auth['name']} --")
            
            try:
                url = f"{base_url}{endpoint}"
                params = auth.get('params', {})
                
                # Try both GET and OPTIONS methods to determine accepted methods
                for method in ['GET', 'OPTIONS']:
                    try:
                        if method == 'GET':
                            response = requests.get(
                                url, 
                                headers=auth['headers'], 
                                params=params,
                                timeout=10
                            )
                        else:
                            response = requests.options(
                                url, 
                                headers=auth['headers'], 
                                params=params,
                                timeout=10
                            )
                        
                        print(f"{method} Status: {response.status_code}")
                        
                        if 'Allow' in response.headers:
                            print(f"Allowed methods: {response.headers['Allow']}")
                        
                        if response.status_code < 500:  # Don't print server error responses
                            try:
                                print(f"Response: {json.dumps(response.json(), indent=2)}")
                            except:
                                print(f"Text response: {response.text[:100]}...")
                    except Exception as e:
                        print(f"{method} request failed: {e}")
            
            except Exception as e:
                print(f"Request completely failed: {e}")
    
    print("\n=== Auth testing complete ===")

if __name__ == "__main__":
    test_auth_methods()
