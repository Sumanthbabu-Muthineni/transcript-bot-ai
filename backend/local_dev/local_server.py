#!/usr/bin/env python3
"""
Local development server - wraps Lambda functions in Flask
Run this to test the backend with the actual frontend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv

# Load environment variables from parent directory
parent_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(parent_dir, '.env'))

# Add parent directory to path
sys.path.insert(0, parent_dir)

# Import Lambda functions from parent directory
from lambda_function import ingest_video, chat

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend


def lambda_event_from_flask(flask_request):
    """Convert Flask request to Lambda event format"""
    return {
        'httpMethod': flask_request.method,
        'path': flask_request.path,
        'body': flask_request.get_data(as_text=True),
        'headers': dict(flask_request.headers)
    }


@app.route('/ingest', methods=['POST', 'OPTIONS'])
def ingest_endpoint():
    if request.method == 'OPTIONS':
        return '', 200

    event = lambda_event_from_flask(request)
    response = ingest_video(event, {})

    # Lambda returns body as JSON string, parse it
    import json
    body = json.loads(response.get('body', '{}'))
    return jsonify(body), response.get('statusCode', 200)


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    if request.method == 'OPTIONS':
        return '', 200

    event = lambda_event_from_flask(request)
    response = chat(event, {})

    # Lambda returns body as JSON string, parse it
    import json
    body = json.loads(response.get('body', '{}'))
    return jsonify(body), response.get('statusCode', 200)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Local Development Server")
    print("="*60)
    print(f"Server running at: http://localhost:5000")
    print(f"Ingest endpoint: http://localhost:5000/ingest")
    print(f"Chat endpoint: http://localhost:5000/chat")
    print("\nUpdate frontend script.js:")
    print("const API_BASE_URL = 'http://localhost:5000';")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")

    app.run(debug=True, port=5000)
