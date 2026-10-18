from flask import Flask, request, jsonify
import uuid
import time
import os

app = Flask(__name__)

# In-memory storage for our mock data
uploads = {}
accounts = [
    {
        "id": 228,
        "name": "Test YouTube Account",
        "platform": "youtube",
        "status": "active"
    }
]

@app.route('/api/blotato/upload', methods=['POST'])
def upload_video():
    """Mock endpoint to simulate video upload."""
    # Check authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Get JSON data
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ['title', 'account_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create a mock upload
    upload_id = str(uuid.uuid4())
    uploads[upload_id] = {
        "id": upload_id,
        "title": data.get('title'),
        "description": data.get('description', ''),
        "tags": data.get('tags', []),
        "video_url": data.get('video_url'),
        "account_id": data.get('account_id'),
        "status": "processing",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "progress": 0
    }
    
    # Return the upload info
    return jsonify({
        "id": upload_id,
        "status": "processing",
        "message": "Upload started successfully"
    })

@app.route('/api/blotato/uploads/<upload_id>', methods=['GET'])
def get_upload_status(upload_id):
    """Mock endpoint to get upload status."""
    # Check authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Check if upload exists
    if upload_id not in uploads:
        return jsonify({"error": "Upload not found"}), 404
    
    # Update progress (simulate processing)
    upload = uploads[upload_id]
    if upload['status'] == 'processing':
        upload['progress'] += 25
        if upload['progress'] >= 100:
            upload['status'] = 'completed'
            upload['progress'] = 100
    
    return jsonify(upload)

@app.route('/api/youtube/accounts', methods=['GET'])
def get_accounts():
    """Mock endpoint to get user accounts."""
    # Check authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify(accounts)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting mock Blotato API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
