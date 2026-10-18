import os
import requests
import json
from dotenv import load_dotenv
import time
from typing import List, Dict, Any, Optional, Union

# Load environment variables
load_dotenv('.env.youtube_test')

class BlotatoClient:
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
        
        # Print the first and last few characters of the API key for debugging
        key_preview = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***masked***"
        print(f"Using API key: {key_preview}")
        
        # Try to get base URL from environment, or use default
        self.base_url = base_url or os.getenv('BLOTATO_API_URL', 'https://backend.blotato.com/v2')
        print(f"Using API base URL: {self.base_url}")
        
        # Try different authorization formats (API may not use Bearer prefix)
        self.headers = {
            "Authorization": self.api_key,  # Try without Bearer prefix
            "Content-Type": "application/json"
        }
    
    def upload_media(self, media_url: str) -> Optional[str]:
        """Upload media to Blotato API.
        
        Args:
            media_url (str): URL of the media to upload
            
        Returns:
            str: The URL of the uploaded media or None if upload failed
        """
        endpoint = f"{self.base_url}/media"
        
        payload = {
            "url": media_url
        }
        
        try:
            print(f"Uploading media from: {media_url}")
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=60)
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
            
            if response.status_code == 401:
                # Try with Bearer prefix if first attempt failed
                self.headers["Authorization"] = f"Bearer {self.api_key}"
                print("Retrying with Bearer prefix...")
                response = requests.post(endpoint, headers=self.headers, json=payload, timeout=60)
                print(f"Second attempt status code: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"Media uploaded successfully: {result['url']}")
                return result['url']
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Upload media request failed: {e}")
            return None
    
    def publish_post(self, 
                    account_id: str, 
                    content_text: str, 
                    platform: str,
                    target_type: str,
                    media_urls: List[str] = None,
                    additional_posts: List[Dict] = None,
                    target_params: Dict = None,
                    scheduled_time: str = None) -> Optional[Dict]:
        """Publish a post to a social media platform.
        
        Args:
            account_id (str): The account ID to publish from
            content_text (str): The text content of the post
            platform (str): The platform to publish to (twitter, youtube, etc.)
            target_type (str): The target type for publishing
            media_urls (List[str], optional): URLs of media to attach to the post
            additional_posts (List[Dict], optional): Additional posts for threads
            target_params (Dict, optional): Additional parameters for the target
            scheduled_time (str, optional): ISO 8601 timestamp for scheduled posting
            
        Returns:
            Dict: The response from the API or None if publish failed
        """
        endpoint = f"{self.base_url}/posts"
        
        # Build the post object
        content = {
            "text": content_text,
            "mediaUrls": media_urls or [],
            "platform": platform
        }
        
        # Add additional posts if provided
        if additional_posts:
            content["additionalPosts"] = additional_posts
        
        # Build the target object
        target = {"targetType": target_type}
        
        # Add target parameters if provided
        if target_params:
            target.update(target_params)
        
        # Build the request payload
        payload = {
            "post": {
                "accountId": account_id,
                "content": content,
                "target": target
            }
        }
        
        # Add scheduled time if provided
        if scheduled_time:
            payload["scheduledTime"] = scheduled_time
        
        try:
            print(f"Publishing post to {platform} via {target_type}")
            print(f"Request payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=60)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"Post published successfully: {json.dumps(result, indent=2)}")
                return result
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Publish post request failed: {e}")
            return None
    
    def publish_youtube_video(self, 
                             account_id: str,
                             video_url: str,
                             title: str,
                             description: str = "",
                             privacy_status: str = "private",
                             should_notify_subscribers: bool = False,
                             scheduled_time: str = None) -> Optional[Dict]:
        """Publish a video to YouTube.
        
        Args:
            account_id (str): The YouTube account ID
            video_url (str): URL of the video to publish
            title (str): Title of the YouTube video
            description (str, optional): Description for the video
            privacy_status (str, optional): Privacy status (private, public, unlisted)
            should_notify_subscribers (bool, optional): Whether to notify subscribers
            scheduled_time (str, optional): ISO 8601 timestamp for scheduled posting
            
        Returns:
            Dict: The response from the API or None if publish failed
        """
        # First, upload the video URL to get a Blotato media URL
        blotato_media_url = self.upload_media(video_url)
        
        if not blotato_media_url:
            print("Failed to upload video")
            return None
        
        # Build YouTube-specific target parameters
        target_params = {
            "title": title,
            "privacyStatus": privacy_status,
            "shouldNotifySubscribers": should_notify_subscribers
        }
        
        # Publish the video
        return self.publish_post(
            account_id=account_id,
            content_text=description,
            platform="youtube",
            target_type="youtube",
            media_urls=[blotato_media_url],
            target_params=target_params,
            scheduled_time=scheduled_time
        )
    
    def publish_twitter_thread(self,
                              account_id: str,
                              main_tweet: str,
                              replies: List[str],
                              media_urls: List[str] = None,
                              scheduled_time: str = None) -> Optional[Dict]:
        """Publish a Twitter thread.
        
        Args:
            account_id (str): The Twitter account ID
            main_tweet (str): Content of the main tweet
            replies (List[str]): Content of the reply tweets
            media_urls (List[str], optional): URLs of media to attach to the main tweet
            scheduled_time (str, optional): ISO 8601 timestamp for scheduled posting
            
        Returns:
            Dict: The response from the API or None if publish failed
        """
        # Process the media URLs if provided
        processed_media_urls = []
        if media_urls:
            for url in media_urls:
                processed_url = self.upload_media(url)
                if processed_url:
                    processed_media_urls.append(processed_url)
        
        # Build additional posts for the thread
        additional_posts = []
        for reply in replies:
            additional_posts.append({
                "text": reply,
                "mediaUrls": []
            })
        
        # Publish the thread
        return self.publish_post(
            account_id=account_id,
            content_text=main_tweet,
            platform="twitter",
            target_type="twitter",
            media_urls=processed_media_urls,
            additional_posts=additional_posts,
            scheduled_time=scheduled_time
        )
