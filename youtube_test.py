import os
import requests
import json
import time
from datetime import datetime

"""
Focused YouTube testing script for Blotato API
"""

# Constants
API_KEY = "blt_KjB6F/g4oS6jGydJxzv137UH9dsLcrER/6YT3Vok/yg="
BASE_URL = "https://backend.blotato.com/v2"
YOUTUBE_ACCOUNT_ID = "228"
VIDEO_PATH = r"C:\Users\Isaia\OneDrive\Documents\Coding\Blotato_api\7429779620297231647_Save.mp4"

def upload_to_youtube():
    """
    Test direct YouTube upload using Blotato API
    """
    print("=== Testing YouTube Upload ===")
    print(f"Account ID: {YOUTUBE_ACCOUNT_ID}")
    print(f"Video file: {VIDEO_PATH}")
    
    # Verify video file exists
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video file not found: {VIDEO_PATH}")
        return
    
    # 1. First upload the media
    print("\n1. Uploading media file...")
    media_url = upload_media()
    
    if not media_url:
        print("❌ Media upload failed. Cannot proceed with YouTube publishing.")
        return
    
    # 2. Now publish to YouTube
    print("\n2. Publishing to YouTube...")
    title = f"Test Upload - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    description = "This is an automated test upload via the Blotato API"
    
    # Create the YouTube post
    post_result = create_youtube_post(media_url, title, description)
    
    if post_result:
        print("✅ YouTube upload test completed successfully!")
        return post_result
    else:
        print("❌ YouTube upload test failed.")
        return None

def upload_media():
    """
    Upload media to Blotato API
    """
    print("--- Media Upload ---")
    
    # Try different authentication methods
    auth_headers = [
        {"Authorization": f"Bearer {API_KEY}"},
        {"Authorization": API_KEY},
        {"X-API-Key": API_KEY}
    ]
    
    # First try with URL method
    for auth in auth_headers:
        try:
            # Try with public URL first
            test_url = "https://sample-videos.com/img/Sample-jpg-image-100kb.jpg"
            print(f"Testing with URL: {test_url}")
            
            headers = {**auth, "Content-Type": "application/json"}
            print(f"Using headers: {headers}")
            
            url_payload = {"url": test_url}
            
            response = requests.post(
                f"{BASE_URL}/media", 
                headers=headers,
                json=url_payload,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                return result.get('url')
            
        except Exception as e:
            print(f"Error: {e}")
    
    # If URL method fails, try with multipart upload
    print("\nTrying multipart form upload...")
    
    for auth in auth_headers:
        try:
            with open(VIDEO_PATH, 'rb') as file:
                files = {
                    'file': (os.path.basename(VIDEO_PATH), file, 'video/mp4')
                }
                
                response = requests.post(
                    f"{BASE_URL}/media",
                    headers=auth,  # No content-type for multipart
                    files=files,
                    timeout=120
                )
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return result.get('url')
                
        except Exception as e:
            print(f"Error: {e}")
    
    # If all attempts fail, try with pre-signed URL if available in the error response
    print("\nChecking for pre-signed URL in error response...")
    return None

def create_youtube_post(media_url, title, description):
    """
    Create YouTube post with the uploaded media
    
    Per documentation:
    - POST to /posts
    - post object with accountId, content, and target
    - content object with text, mediaUrls, and platform
    - target object with targetType and additional fields based on platform
    
    For YouTube, target requires:
    - targetType: 'youtube'
    - title: string
    - privacyStatus: 'private' | 'public' | 'unlisted'
    - shouldNotifySubscribers: boolean
    """
    print("--- YouTube Post Creation ---")
    print(f"Media URL: {media_url}")
    print(f"Title: {title}")
    
    # Try different authentication methods
    auth_headers = [
        {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        {"Authorization": API_KEY, "Content-Type": "application/json"},
        {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    ]
    
    # Build the payload according to exact documentation structure
    payload = {
        "post": {
            "accountId": YOUTUBE_ACCOUNT_ID,
            "content": {
                "text": description,
                "mediaUrls": [media_url] if media_url else [],
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
    
    # Optional: Schedule for future time (ISO 8601 format)
    # payload["scheduledTime"] = "2025-03-16T00:00:00Z" 
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    endpoint = f"{BASE_URL}/posts"
    print(f"Endpoint: {endpoint}")
    
    for auth in auth_headers:
        try:
            print(f"\nUsing auth: {auth}")
            
            response = requests.post(
                endpoint,
                headers=auth,
                json=payload,
                timeout=60
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"Success! Response: {json.dumps(result, indent=2)}")
                return result
            elif response.status_code == 401:
                print("Authentication failed with this method")
            else:
                print(f"Request failed with status {response.status_code}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    return None

def attempt_direct_url_upload():
    """
    Attempt a direct URL-based YouTube upload as a fallback
    
    Although this isn't in the documentation, we can try a simplified approach
    that might work with some APIs.
    """
    print("\n=== Attempting Alternative YouTube Post Structure ===")
    
    # Use the standard posts endpoint
    endpoint = f"{BASE_URL}/posts"
    
    auth_headers = [
        {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        {"Authorization": API_KEY, "Content-Type": "application/json"},
        {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    ]
    
    # Simplify the payload structure
    payload = {
        "post": {
            "accountId": YOUTUBE_ACCOUNT_ID,
            "content": {
                "text": "This is a direct upload test to YouTube via Blotato API",
                "mediaUrls": ["https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"],
                "platform": "youtube"
            },
            "target": {
                "targetType": "youtube",
                "title": f"Alternative Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "privacyStatus": "private",
                "shouldNotifySubscribers": False
            }
        }
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    for auth in auth_headers:
        try:
            print(f"\nUsing auth: {auth}")
            
            response = requests.post(
                endpoint,
                headers=auth,
                json=payload,
                timeout=60
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code in [200, 201]:
                return response.json()
            
        except Exception as e:
            print(f"Error: {e}")
    
    return None

def main():
    """Main function"""
    print(f"=== Blotato API YouTube Test ===")
    print(f"Testing with API: {BASE_URL}")
    
    # Try the regular upload flow first
    result = upload_to_youtube()
    
    # If that fails, try alternative approach
    if not result:
        result = attempt_direct_url_upload()
    
    # Final result
    if result:
        print("\n✅ YouTube test completed successfully!")
        print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print("\n❌ All YouTube upload attempts failed.")

if __name__ == "__main__":
    main()
