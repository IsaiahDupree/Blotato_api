import os
import sys
import requests
import json
import base64
from urllib.parse import quote

"""
Direct test for Blotato API with focus on authentication
"""

# The API key needs special handling due to special characters
API_KEY = "blt_KjB6F/g4oS6jGydJxzv137UH9dsLcrER/6YT3Vok/yg="
BASE_URL = "https://backend.blotato.com/v2"
VIDEO_PATH = r"C:\Users\Isaia\OneDrive\Documents\Coding\Blotato_api\7429779620297231647_Save.mp4"

def test_auth():
    """Test authentication with various methods"""
    print("=== Testing Authentication Methods ===")
    
    # Properly URL encode the API key for use in headers
    encoded_key = quote(API_KEY)
    print(f"Original API key: {API_KEY}")
    print(f"URL-encoded API key: {encoded_key}")
    
    # Also try base64 encoding
    base64_key = base64.b64encode(API_KEY.encode()).decode()
    print(f"Base64-encoded API key: {base64_key}")
    
    # Define endpoints to test
    endpoints = [
        '/media',  # Media upload endpoint
    ]
    
    # Define different auth header combinations to try
    auth_methods = [
        {
            "name": "Bearer Token with Original Key", 
            "headers": {
                "Authorization": f"Bearer {API_KEY}", 
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Bearer Token with URL-encoded Key", 
            "headers": {
                "Authorization": f"Bearer {encoded_key}", 
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Direct API Key", 
            "headers": {
                "Authorization": API_KEY, 
                "Content-Type": "application/json"
            }
        },
        {
            "name": "X-API-Key Header", 
            "headers": {
                "X-API-Key": API_KEY, 
                "Content-Type": "application/json"
            }
        },
    ]
    
    for endpoint in endpoints:
        print(f"\n=== Testing endpoint: {endpoint} ===")
        
        for auth in auth_methods:
            print(f"\n-- Using {auth['name']} --")
            url = f"{BASE_URL}{endpoint}"
            
            # Try a simple POST request to the media endpoint
            payload = {"url": "https://sample-videos.com/img/Sample-jpg-image-100kb.jpg"}
            
            try:
                response = requests.post(url, headers=auth['headers'], json=payload, timeout=30)
                print(f"Status: {response.status_code}")
                
                try:
                    resp_text = response.text
                    print(f"Response: {resp_text[:200]}")
                    
                    # Try to parse as JSON if possible
                    if resp_text and resp_text[0] in ['{', '[']:
                        resp_json = json.loads(resp_text)
                        print(f"JSON Response: {json.dumps(resp_json, indent=2)}")
                except Exception as e:
                    print(f"Error parsing response: {e}")
            
            except Exception as e:
                print(f"Request failed: {e}")

def test_media_upload():
    """Test media upload with URL"""
    print("\n=== Testing Media Upload with URL ===")
    
    # Use the URL method with a test image
    url = f"{BASE_URL}/media"
    payload = {"url": "https://sample-videos.com/img/Sample-jpg-image-100kb.jpg"}
    
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Request failed: {e}")

def main():
    """Main function to run tests"""
    print(f"Testing Blotato API at: {BASE_URL}")
    
    # Run authentication tests first
    test_auth()
    
    # Then try specific media upload test
    test_media_upload()

if __name__ == "__main__":
    main()
