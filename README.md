# Single-Video Twin

Chat with any YouTube video using RAG (Retrieval-Augmented Generation).

## Architecture

```
Local Processing (One-time per video)
  ├─ Extract YouTube transcript
  ├─ Generate embeddings (OpenAI)
  └─ Upload to S3
         ↓
    S3 Vector Store
         ↓
Serverless Backend (Lambda)
  ├─ Load vectors from S3
  ├─ Search relevant content
  └─ Generate answer (GPT)
         ↓
    Frontend UI
```

**Why this approach?**
As this is just for POC .Proxy services cost money. Instead, we process videos locally (no YouTube IP blocking) and upload embeddings to S3. The serverless backend handles all chat queries by loading from S3.

## Tech Stack

- Backend: Python, AWS Lambda, FAISS, OpenAI
- Frontend: HTML/CSS/JavaScript
- Storage: AWS S3

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

## Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt
pip install -r local_dev/requirements-dev.txt

# 2. Configure environment
cp .env.example .env
# Edit .env: add OPENAI_API_KEY and S3_BUCKET_NAME

# 3. Start servers
# Terminal 1
cd local_dev && python3 local_server.py

# Terminal 2
cd frontend && python3 -m http.server 8000

# 4. Open http://localhost:8000 and start processing videos!
```

## Deploy Backend to AWS

```bash
cd backend
sam build
sam deploy --guided
```

You'll get an API Gateway URL. The Lambda backend can handle chat queries but not video ingestion (YouTube blocks AWS IPs).

## How It Works

1. Extract YouTube transcript
2. Split into chunks (500 chars, 50 overlap)
3. Generate embeddings (OpenAI)
4. Store in FAISS index → Upload to S3
5. Query: Embed question → Search top 3 chunks → GPT answer

## Environment Variables

```env
OPENAI_API_KEY=sk-...
S3_BUCKET_NAME=single-video-twin-vector-store
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo
```

## Notes

- Videos need captions enabled
- Cost per video: ~$0.01 (mostly OpenAI)

## License

MIT
