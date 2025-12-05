# Local Development Tools

Tools for testing the backend locally before deployment.

## Files

- `local_server.py` - Flask server to run Lambda functions locally with frontend
- `local_test.py` - CLI test script for the RAG pipeline
- `local_test_mock.py` - Test without OpenAI API calls (uses mock embeddings)
- `requirements-dev.txt` - Dependencies for local development only

## Usage

### 1. Test with Flask Server (Full UI Testing)

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Make sure parent requirements are installed
pip install -r ../requirements.txt

# Start server
python3 local_server.py
```

Then update `frontend/script.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000';
```

Open `frontend/index.html` in browser and test!

### 2. CLI Testing (No UI)

```bash
# With real OpenAI API
python3 local_test.py

# Without API (mock mode)
python3 local_test_mock.py
```

## Notes

- These tools are for **local development only**
- Not deployed to AWS Lambda
- Flask is not needed in production
