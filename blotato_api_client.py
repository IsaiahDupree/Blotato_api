import os
import requests
import json
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('.env.youtube_test')

class BlotoApiClient:
    """Client for interacting with the Blotato API."""
    
    def __init__(self, api_key=None, base_url=None):
        """Initialize the Blotato API client.
        
        Args:
            api_key (str, optional): The API key for authentication. If not provided,
                                    it will be loaded from the environment variables.
            base_url (str, optional): Base URL for the API. If not provided,
                                    it will be loaded from environment variables or use a default.
        """
        self.api_key = api_key or os.getenv('BLOTATO_API_KEY')
        if not self.api_key:
            raise ValueError("Blotato API key is required")
        
        # Try to get base URL from environment, or use default
        self.base_url = base_url or os.getenv('BLOTATO_API_URL', 'http://localhost:8000/api')
        print(f"Using API base URL: {self.base_url}")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def upload_video(self, video_path, title, description=None, tags=None):
        """Upload a video to Blotato.
        
        Args:
            video_path (str): Path to the video file or URL
            title (str): Title of the video
            description (str, optional): Description of the video
            tags (list, optional): Tags for the video
            
        Returns:
            dict: The response from the API
        """
        # Check if video_path is a URL or local file
        if video_path.startswith('http'):
            # For URL, we'll pass the URL directly
            video_source = video_path
        else:
            # For local file, we'll need to upload it
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # This would be replaced with actual file upload logic if needed
            video_source = video_path
        
        account_id = os.getenv('YOUTUBE_ACCOUNT_ID')
        
        payload = {
            "title": title,
            "description": description or "",
            "tags": tags or [],
            "video_url": video_source if video_path.startswith('http') else None,
            "account_id": account_id
        }
        
        try:
            endpoint = f"{self.base_url}/blotato/upload"
            print(f"Sending request to: {endpoint}")
            print(f"Request payload: {json.dumps(payload, indent=2)}")
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code >= 400:
                print(f"Error {response.status_code}: {response.text}")
                return None
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def check_upload_status(self, upload_id):
        """Check the status of a video upload.
        
        Args:
            upload_id (str): The ID of the upload to check
            
        Returns:
            dict: The response from the API
        """
        try:
            endpoint = f"{self.base_url}/blotato/uploads/{upload_id}"
            print(f"Checking status at: {endpoint}")
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            
            if response.status_code >= 400:
                print(f"Error {response.status_code}: {response.text}")
                return None
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def get_user_accounts(self):
        """Get all user accounts.
        
        Returns:
            list: List of user accounts
        """
        try:
            endpoint = f"{self.base_url}/youtube/accounts"
            print(f"Fetching accounts from: {endpoint}")
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            
            if response.status_code >= 400:
                print(f"Error {response.status_code}: {response.text}")
                return None
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
