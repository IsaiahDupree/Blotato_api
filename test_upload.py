import os
import json
import time
import argparse
from dotenv import load_dotenv
from blotato_api_client import BlotoApiClient

# Load environment variables
load_dotenv('.env.youtube_test')

def test_video_upload(client, video_path=None):
    """Test video upload functionality.
    
    Args:
        client: BlotoApiClient instance
        video_path: Path to video file or URL
    """
    if not video_path:
        video_path = os.getenv('VIDEO_PATH')
        if not video_path:
            print("ERROR: No video path provided. Set VIDEO_PATH in .env.youtube_test or pass as argument.")
            return False
    
    print(f"Testing upload with video: {video_path}")
    
    # Upload the video
    response = client.upload_video(
        video_path=video_path,
        title=f"Test Upload - {time.strftime('%Y-%m-%d %H:%M:%S')}",
        description="This is a test upload from the Blotato API client",
        tags=["test", "api", "blotato"]
    )
    
    if not response:
        print("Upload failed")
        return False
    
    print(f"Upload initiated: {json.dumps(response, indent=2)}")
    
    # If the API returns an upload ID, we can check the status
    if "id" in response:
        upload_id = response["id"]
        print(f"Checking status for upload ID: {upload_id}")
        
        # Check status a few times
        for i in range(3):
            time.sleep(2)  # Wait 2 seconds between checks
            print(f"Status check #{i+1}...")
            status = client.check_upload_status(upload_id)
            if status:
                print(f"Upload status: {json.dumps(status, indent=2)}")
            else:
                print("Failed to get upload status")
    
    return True

def test_get_accounts(client):
    """Test fetching user accounts.
    
    Args:
        client: BlotoApiClient instance
    """
    print("Fetching user accounts...")
    accounts = client.get_user_accounts()
    
    if not accounts:
        print("Failed to fetch accounts")
        return False
    
    print(f"Accounts: {json.dumps(accounts, indent=2)}")
    return True

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description='Test the Blotato API')
    parser.add_argument('--mock', action='store_true', help='Use mock server')
    parser.add_argument('--base-url', type=str, help='Base URL for the API')
    parser.add_argument('--api-key', type=str, help='API key for authentication')
    parser.add_argument('--video-path', type=str, help='Path to video file or URL')
    args = parser.parse_args()
    
    if args.mock:
        # Check if Flask is installed
        try:
            import subprocess
            import sys
            
            print("Starting mock server...")
            # Start the mock server in a separate process
            server_process = subprocess.Popen(
                [sys.executable, 'mock_blotato_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give the server a moment to start
            time.sleep(2)
            
            # Use localhost for the base URL
            base_url = 'http://localhost:8000/api'
        except ImportError:
            print("Flask is required for mock server. Install with: pip install flask")
            return
    else:
        # Use provided base URL or get from environment
        base_url = args.base_url or os.getenv('BLOTATO_API_URL')
    
    # Use provided API key or get from environment
    api_key = args.api_key or os.getenv('BLOTATO_API_KEY')
    
    # Create client
    client = BlotoApiClient(api_key=api_key, base_url=base_url)
    
    print("\n=== Testing Blotato API ===")
    print(f"Using {'mock' if args.mock else 'real'} server")
    print(f"Base URL: {client.base_url}")
    print()
    
    try:
        # Test get accounts
        print("\n--- Testing Get Accounts ---")
        test_get_accounts(client)
        
        # Test video upload
        print("\n--- Testing Video Upload ---")
        test_video_upload(client, args.video_path)
        
        print("\n=== Tests complete ===")
    finally:
        if args.mock:
            print("Shutting down mock server...")
            server_process.terminate()

if __name__ == "__main__":
    main()
