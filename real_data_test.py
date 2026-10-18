import os
import sys
import time
import json
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from blotato_client import BlotatoClient

# Load environment variables
load_dotenv('.env.youtube_test')

def test_media_upload(client):
    """Test uploading media to Blotato API.
    
    Args:
        client: BlotatoClient instance
    
    Returns:
        bool: True if test passed, False otherwise
    """
    print("\n=== Testing Media Upload ===")
    
    # Get media URL from environment or use a default sample image
    media_url = os.getenv('MEDIA_URL', 'https://sample-videos.com/img/Sample-jpg-image-100kb.jpg')
    print(f"Testing media upload with URL: {media_url}")
    
    # Upload the media
    uploaded_url = client.upload_media(media_url)
    
    if not uploaded_url:
        print("❌ Media upload test failed")
        return False
    
    print(f"✅ Media uploaded successfully: {uploaded_url}")
    return uploaded_url

def test_youtube_video_upload(client):
    """Test uploading and publishing a YouTube video.
    
    Args:
        client: BlotatoClient instance
    
    Returns:
        bool: True if test passed, False otherwise
    """
    print("\n=== Testing YouTube Video Upload ===")
    
    # Get account ID and video URL from environment
    account_id = os.getenv('YOUTUBE_ACCOUNT_ID')
    if not account_id:
        print("❌ YOUTUBE_ACCOUNT_ID environment variable is required")
        return False
    
    video_url = os.getenv('VIDEO_PATH')
    if not video_url:
        print("❌ VIDEO_PATH environment variable is required")
        return False
    
    print(f"Testing YouTube video upload with account ID: {account_id}")
    print(f"Video URL: {video_url}")
    
    # Generate a test title with timestamp to avoid duplicates
    title = f"Test Video Upload - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    description = "This is a test video upload from the Blotato API client"
    
    # Publish the YouTube video
    response = client.publish_youtube_video(
        account_id=account_id,
        video_url=video_url,
        title=title,
        description=description,
        privacy_status="private",  # Set to private for testing
        should_notify_subscribers=False
    )
    
    if not response:
        print("❌ YouTube video upload test failed")
        return False
    
    print(f"✅ YouTube video uploaded successfully: {json.dumps(response, indent=2)}")
    return True

def test_twitter_thread(client):
    """Test publishing a Twitter thread.
    
    Args:
        client: BlotatoClient instance
    
    Returns:
        bool: True if test passed, False otherwise
    """
    print("\n=== Testing Twitter Thread ===")
    
    # Get account ID from environment or use a sample
    account_id = os.getenv('TWITTER_ACCOUNT_ID')
    if not account_id:
        print("⚠️ TWITTER_ACCOUNT_ID not provided, skipping Twitter thread test")
        return False
    
    print(f"Testing Twitter thread with account ID: {account_id}")
    
    # Create sample content for the thread
    main_tweet = f"This is a test tweet from the Blotato API client - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    replies = [
        "This is the second tweet in the thread with more details.",
        "And this is the third tweet to conclude the thread. #testing #blotato"
    ]
    
    # Scheduled time (10 minutes from now)
    scheduled_time = (datetime.now() + timedelta(minutes=10)).isoformat() + "Z"
    
    # Publish the Twitter thread
    response = client.publish_twitter_thread(
        account_id=account_id,
        main_tweet=main_tweet,
        replies=replies,
        scheduled_time=scheduled_time
    )
    
    if not response:
        print("❌ Twitter thread test failed")
        return False
    
    print(f"✅ Twitter thread scheduled successfully: {json.dumps(response, indent=2)}")
    return True

def test_custom_post(client):
    """Test publishing a custom post to any supported platform.
    
    Args:
        client: BlotatoClient instance
        
    Returns:
        bool: True if test passed, False otherwise
    """
    print("\n=== Testing Custom Post ===")
    
    # Get platform details from user input
    print("Available platforms:")
    print("1. Twitter")
    print("2. LinkedIn")
    print("3. Facebook")
    print("4. Instagram")
    print("5. TikTok")
    print("6. Pinterest")
    print("7. Threads")
    print("8. Bluesky")
    print("9. YouTube")
    
    try:
        choice = int(input("Select platform (1-9): "))
        if choice < 1 or choice > 9:
            raise ValueError("Invalid choice")
    except ValueError:
        print("❌ Invalid selection, defaulting to Twitter")
        choice = 1
    
    platforms = [
        {"name": "twitter", "target_type": "twitter"},
        {"name": "linkedin", "target_type": "linkedin"},
        {"name": "facebook", "target_type": "facebook"},
        {"name": "instagram", "target_type": "instagram"},
        {"name": "tiktok", "target_type": "tiktok"},
        {"name": "pinterest", "target_type": "pinterest"},
        {"name": "threads", "target_type": "threads"},
        {"name": "bluesky", "target_type": "bluesky"},
        {"name": "youtube", "target_type": "youtube"}
    ]
    
    platform_info = platforms[choice - 1]
    
    # Get account ID
    account_id = input(f"Enter account ID for {platform_info['name']}: ")
    if not account_id:
        print(f"❌ Account ID is required for {platform_info['name']}")
        return False
    
    # Get content text
    content_text = input("Enter post content: ")
    if not content_text:
        content_text = f"Test post to {platform_info['name']} from Blotato API - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"Using default content: {content_text}")
    
    # Get target params based on platform
    target_params = {}
    
    if platform_info['name'] == 'facebook':
        page_id = input("Enter Facebook Page ID: ")
        if page_id:
            target_params['pageId'] = page_id
    
    elif platform_info['name'] == 'linkedin':
        page_id = input("Enter LinkedIn Page ID (optional): ")
        if page_id:
            target_params['pageId'] = page_id
    
    elif platform_info['name'] == 'pinterest':
        board_id = input("Enter Pinterest Board ID: ")
        if board_id:
            target_params['boardId'] = board_id
    
    elif platform_info['name'] == 'youtube':
        title = input("Enter YouTube video title: ")
        if not title:
            title = f"Test Video - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        target_params['title'] = title
        target_params['privacyStatus'] = 'private'
        target_params['shouldNotifySubscribers'] = False
    
    # Publish the post
    response = client.publish_post(
        account_id=account_id,
        content_text=content_text,
        platform=platform_info['name'],
        target_type=platform_info['target_type'],
        target_params=target_params
    )
    
    if not response:
        print("❌ Custom post test failed")
        return False
    
    print(f"✅ Post published successfully: {json.dumps(response, indent=2)}")
    return True

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description='Test the Blotato API with real data')
    parser.add_argument('--test-type', type=str, choices=['all', 'media', 'youtube', 'twitter', 'custom'], 
                        default='all', help='Type of test to run')
    parser.add_argument('--api-key', type=str, help='API key for authentication')
    parser.add_argument('--base-url', type=str, help='Base URL for the API')
    args = parser.parse_args()
    
    # Use provided API key or get from environment
    api_key = args.api_key or os.getenv('BLOTATO_API_KEY')
    
    # Use provided base URL or get from environment
    base_url = args.base_url or os.getenv('BLOTATO_API_URL')
    
    # Create client
    client = BlotatoClient(api_key=api_key, base_url=base_url)
    
    print("\n=== Testing Blotato API with Real Data ===")
    print(f"Base URL: {client.base_url}")
    print(f"Test type: {args.test_type}")
    print()
    
    try:
        # Run the selected test(s)
        if args.test_type in ['all', 'media']:
            uploaded_url = test_media_upload(client)
        
        if args.test_type in ['all', 'youtube']:
            test_youtube_video_upload(client)
        
        if args.test_type in ['all', 'twitter']:
            test_twitter_thread(client)
        
        if args.test_type in ['all', 'custom']:
            test_custom_post(client)
        
        print("\n=== Tests complete ===")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
