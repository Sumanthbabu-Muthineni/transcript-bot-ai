# Single-Video Twin

Turn any YouTube video into a conversational AI. Ask questions and get answers based strictly on the video content.

## What it does

Takes a YouTube URL, extracts the transcript, and lets you chat with it. The AI only uses information from the video to answer your questions.

## Tech Stack

**Backend:**
- Python 3.11
- AWS Lambda (serverless)
- FAISS for vector search
- OpenAI for embeddings and chat

**Frontend:**
- Plain HTML/CSS/JavaScript
- No frameworks

## Project Structure

```
prismetic/
├── backend/
│   ├── lambda_function.py      # Lambda handlers
│   ├── utils/                  # Core logic
│   ├── local_dev/              # Local testing tools
│   ├── requirements.txt        # Production dependencies
│   ├── template.yaml           # AWS SAM config
│   └── .env.example
└── frontend/
    ├── index.html
    ├── script.js
    └── styles.css
```

## Local Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Test locally (optional):**
```bash
cd local_dev
pip install -r requirements-dev.txt
python3 local_test.py
# Or run with Flask server: python3 local_server.py
```

## Deployment

### Backend (AWS)

```bash
cd backend

# Install AWS SAM if needed
pip install aws-sam-cli

# Build and deploy
sam build
sam deploy --guided
```

During deployment you'll be asked for:
- Stack name (e.g., `single-video-twin`)
- AWS Region (e.g., `us-east-1`)
- OpenAI API key

After deployment, note the API Gateway URL from the outputs.

### Frontend

**Option 1 - S3:**
```bash
cd frontend
# First update script.js with your API Gateway URL
aws s3 sync . s3://your-bucket-name
```

**Option 2 - Netlify:**
- Update `script.js` with your API Gateway URL
- Drag and drop the frontend folder to Netlify

**Option 3 - Local:**
- Update `script.js` with your API Gateway URL
- Open `index.html` in your browser

## API Endpoints

### POST /ingest
Processes a YouTube video and stores the transcript.

Request:
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

Response:
```json
{
  "success": true,
  "video_id": "VIDEO_ID",
  "chunks_count": 42,
  "transcript_length": 15243
}
```

### POST /chat
Answers questions about the processed video.

Request:
```json
{
  "video_id": "VIDEO_ID",
  "question": "What is the main topic?"
}
```

Response:
```json
{
  "success": true,
  "answer": "The video discusses...",
  "context_used": 3
}
```

## How it works

1. User provides YouTube URL
2. Backend extracts transcript using `youtube-transcript-api`
3. Text is split into chunks with overlap
4. Chunks are embedded using OpenAI and stored in FAISS
5. Index is saved to S3
6. When user asks a question:
   - Question is embedded
   - Top 3 most relevant chunks are retrieved
   - GPT generates answer using only those chunks

## Environment Variables

Backend `.env`:
```
OPENAI_API_KEY=your_key_here
S3_BUCKET_NAME=your_bucket_name
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=3
```

## Cost

Typical 10-minute video + 5 questions:
- Lambda: Free tier
- S3: Free tier
- OpenAI: ~$0.005

Total: Less than $0.01 per video

## Notes

- Videos must have captions/transcripts enabled
- One video per session currently
- No authentication (suitable for POC/demo)
- Works best with TED talks and educational content

## License

MIT
