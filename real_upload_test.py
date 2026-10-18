import os
import sys
import json
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.youtube_test')

def upload_media_file(api_key, base_url, file_path):
    """Upload a local media file to the Blotato API.
    
    For local files, we need to:
    1. Check if the file exists
    2. Get the file data
    3. Make a multipart form data request
    
    Args:
        api_key (str): The Blotato API key
        base_url (str): The base URL for the API
        file_path (str): Path to the local file
        
    Returns:
        str or None: The URL of the uploaded media or None if upload failed
    """
    print(f"\n=== Uploading Media File: {file_path} ===")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    # Get file size
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")
    
    # Setup headers - try different auth methods
    auth_headers = [
        {"Authorization": f"Bearer {api_key}"},
        {"Authorization": api_key},
        {"X-API-Key": api_key}
    ]
    
    # Endpoint for media upload
    endpoint = f"{base_url}/media"
    
    for i, headers in enumerate(auth_headers):
        headers["Accept"] = "application/json"
        
        print(f"\nAttempt #{i+1} with auth method: {headers}")
        
        try:
            # First, try the URL-based upload method since it's simpler
            url_payload = {
                "url": f"file://{file_path}"  # Try file:// protocol
            }
            
            print(f"Trying URL-based upload with payload: {url_payload}")
            
            # Try to upload with URL method first
            url_response = requests.post(
                endpoint, 
                headers={**headers, "Content-Type": "application/json"}, 
                json=url_payload,
                timeout=60
            )
            
            print(f"URL upload status: {url_response.status_code}")
            print(f"Response: {url_response.text[:200]}")
            
            if url_response.status_code in [200, 201]:
                try:
                    result = url_response.json()
                    print(f"Media uploaded successfully via URL method: {result}")
                    return result.get('url')
                except:
                    print("Could not parse JSON response")
            
            # If URL method fails, try multipart form upload
            print("\nFalling back to multipart form upload...")
            
            with open(file_path, 'rb') as file:
                files = {
                    'file': (os.path.basename(file_path), file, 'video/mp4')
                }
                
                form_response = requests.post(
                    endpoint,
                    headers=headers,  # No content-type for multipart
                    files=files,
                    timeout=120  # Longer timeout for file upload
                )
                
                print(f"Form upload status: {form_response.status_code}")
                print(f"Response: {form_response.text[:200]}")
                
                if form_response.status_code in [200, 201]:
                    try:
                        result = form_response.json()
                        print(f"Media uploaded successfully via form: {result}")
                        return result.get('url')
                    except:
                        print("Could not parse JSON response")
        
        except Exception as e:
            print(f"Request failed: {e}")
    
    print("❌ All upload attempts failed")
    return None

def publish_to_youtube(api_key, base_url, account_id, media_url, title, description):
    """Publish a video to YouTube via the Blotato API.
    
    Args:
        api_key (str): The Blotato API key
        base_url (str): The base URL for the API
        account_id (str): The YouTube account ID
        media_url (str): The URL of the uploaded media
        title (str): The title for the YouTube video
        description (str): The description for the YouTube video
        
    Returns:
        dict or None: The response from the API or None if publish failed
    """
    print(f"\n=== Publishing to YouTube ===")
    
    # Setup headers - try different auth methods
    auth_headers = [
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        {"Authorization": api_key, "Content-Type": "application/json"},
        {"X-API-Key": api_key, "Content-Type": "application/json"}
    ]
    
    # Endpoint for post publishing
    endpoint = f"{base_url}/posts"
    
    # Build the post payload according to the API documentation
    payload = {
        "post": {
            "accountId": account_id,
            "content": {
                "text": description,
                "mediaUrls": [media_url],
                "platform": "youtube"
            },
            "target": {
                "targetType": "youtube",
                "title": title,
                "privacyStatus": "private",
                "shouldNotifySubscribers": False
            }
        }
    }
    
    print(f"Publishing with payload: {json.dumps(payload, indent=2)}")
    
    for i, headers in enumerate(auth_headers):
        print(f"\nAttempt #{i+1} with auth method: {headers}")
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code in [200, 201]:
                try:
                    result = response.json()
                    print(f"Video published successfully: {result}")
                    return result
                except:
                    print("Could not parse JSON response")
        
        except Exception as e:
            print(f"Request failed: {e}")
    
    print("❌ All publishing attempts failed")
    return None

def main():
    """Main function to run the test."""
    # Get API key from environment
    api_key = os.getenv('BLOTATO_API_KEY')
    if not api_key:
        print("❌ BLOTATO_API_KEY environment variable is required")
        sys.exit(1)
    
    # Get base URL from environment
    base_url = os.getenv('BLOTATO_API_URL')
    if not base_url:
        print("❌ BLOTATO_API_URL environment variable is required")
        sys.exit(1)
    
    # Get account ID from environment
    account_id = os.getenv('YOUTUBE_ACCOUNT_ID')
    if not account_id:
        print("❌ YOUTUBE_ACCOUNT_ID environment variable is required")
        sys.exit(1)
    
    # Get video path from environment
    video_path = os.getenv('VIDEO_PATH')
    if not video_path:
        print("❌ VIDEO_PATH environment variable is required")
        sys.exit(1)
    
    print("=== Blotato API Real Data Test ===")
    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"Base URL: {base_url}")
    print(f"Account ID: {account_id}")
    print(f"Video Path: {video_path}")
    
    # Upload the media file
    media_url = upload_media_file(api_key, base_url, video_path)
    
    if not media_url:
        print("❌ Media upload failed, cannot proceed with publishing")
        sys.exit(1)
    
    # Generate a test title with timestamp to avoid duplicates
    title = f"Test Video Upload - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    description = "This is a test video upload from the Blotato API client"
    
    # Publish to YouTube
    result = publish_to_youtube(api_key, base_url, account_id, media_url, title, description)
    
    if result:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed")

if __name__ == "__main__":
    main()
