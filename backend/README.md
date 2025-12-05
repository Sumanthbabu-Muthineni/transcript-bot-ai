# Single-Video Twin - Backend

Serverless RAG application built with AWS Lambda and Python.

## Architecture

```
YouTube URL → Transcript Extraction → Text Chunking → Embeddings → FAISS Vector Store → S3
                                                                           ↓
User Question → Question Embedding → Similarity Search → Context Retrieval → LLM Answer
```

## Components

### 1. **Transcript Extraction** (`utils/transcript_extractor.py`)
- Extracts video ID from YouTube URLs
- Fetches transcript using `youtube-transcript-api`

### 2. **Text Chunking** (`utils/text_processor.py`)
- Splits transcript into ~500 token chunks
- 50 token overlap to maintain context continuity
- Sentence-boundary aware splitting

### 3. **Embeddings** (`utils/embeddings.py`)
- Uses OpenAI `text-embedding-3-small` (1536 dimensions)
- Cost: $0.02 per 1M tokens

### 4. **Vector Store** (`utils/vector_store.py`)
- FAISS (Facebook AI Similarity Search) for fast retrieval
- Cosine similarity search
- Persistence to S3 for serverless architecture

### 5. **RAG Engine** (`utils/rag_engine.py`)
- Retrieves top-3 relevant chunks
- Generates answers using GPT-3.5-turbo
- System prompt enforces "Twin" behavior (answers only from context)

## API Endpoints

### POST /ingest
Ingest a YouTube video.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:**
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "chunks_count": 42,
  "transcript_length": 15243,
  "message": "Video processed successfully"
}
```

### POST /chat
Ask questions about the video.

**Request:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "question": "What is the main topic of this video?"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "The video discusses...",
  "context_used": 3,
  "video_id": "dQw4w9WgXcQ"
}
```

## Local Development

### Prerequisites
- Python 3.11
- AWS CLI configured
- OpenAI API key

### Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. Test locally (requires local S3 mock or skip S3 operations):
```bash
python -c "from lambda_function import ingest_video; print(ingest_video({'body': '{\"url\": \"YOUR_URL\"}'}, {}))"
```

## Deployment to AWS

### Using AWS SAM (Recommended)

1. Install AWS SAM CLI:
```bash
pip install aws-sam-cli
```

2. Build:
```bash
sam build
```

3. Deploy:
```bash
sam deploy --guided
```

Enter your OpenAI API key when prompted.

4. Note the API endpoint from outputs.

### Manual Lambda Deployment

1. Create deployment package:
```bash
pip install -r requirements.txt -t package/
cp -r utils package/
cp lambda_function.py package/
cd package && zip -r ../deployment.zip . && cd ..
```

2. Create Lambda function in AWS Console:
- Runtime: Python 3.11
- Memory: 1024 MB
- Timeout: 300 seconds

3. Create S3 bucket for vector store

4. Set environment variables in Lambda

5. Create API Gateway with POST /ingest and /chat endpoints

## Cost Estimate (AWS Free Tier)

For a typical 10-minute video with 5 questions:

- **Lambda**: ~30 seconds total → Free tier covers 1M requests
- **S3 Storage**: ~5 MB per video → Free tier covers 5 GB
- **OpenAI**:
  - Embeddings: ~3000 tokens → $0.00006
  - LLM: ~5 questions × 500 tokens → $0.005
  - **Total: < $0.01**

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `S3_BUCKET_NAME` | S3 bucket for indexes | Required |
| `EMBEDDING_MODEL` | OpenAI embedding model | text-embedding-3-small |
| `LLM_MODEL` | OpenAI LLM model | gpt-3.5-turbo |
| `CHUNK_SIZE` | Tokens per chunk | 500 |
| `CHUNK_OVERLAP` | Overlap between chunks | 50 |
| `TOP_K_RESULTS` | Retrieved chunks | 3 |

## Troubleshooting

**Issue: "No transcript found"**
- Some videos have transcripts disabled
- Try a different video with captions enabled

**Issue: Lambda timeout**
- Increase timeout to 300 seconds
- Increase memory to 1024 MB (more memory = faster CPU)

**Issue: Import errors**
- Ensure all dependencies are in deployment package
- Check Python version matches (3.11)
