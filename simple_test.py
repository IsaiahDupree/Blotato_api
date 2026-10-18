import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv('.env.youtube_test')

def test_api_connection():
    """Test a direct connection to the API to troubleshoot connectivity issues"""
    api_key = os.getenv('BLOTATO_API_KEY')
    base_url = input("Enter the Blotato API base URL (e.g., http://localhost:8000/api): ")
    
    if not base_url:
        base_url = "http://localhost:8000/api"
    
    print(f"Testing connection to: {base_url}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "/youtube/accounts",
        "/blotato/status",
        "/health"  # Many APIs have a health endpoint
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\nTrying endpoint: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status code: {response.status_code}")
            
            if response.status_code < 400:
                try:
                    print(f"Response: {json.dumps(response.json(), indent=2)}")
                except:
                    print(f"Raw response: {response.text[:200]}...")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Request failed: {e}")
    
    print("\nWhat would you like to try next?")
    print("1. Try uploading to the mock server")
    print("2. Try a different base URL")
    print("3. Exit")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        print("\nStarting mock server test...")
        from test_upload import main
        import sys
        sys.argv = [sys.argv[0], "--mock"]
        main()
    elif choice == "2":
        print("\nRestarting test with a different URL...")
        test_api_connection()

if __name__ == "__main__":
    test_api_connection()
