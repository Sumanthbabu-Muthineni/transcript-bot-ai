"""
AWS Lambda Handler
Main entry point for serverless functions
"""
import json
import os
from utils.transcript_extractor import get_transcript
from utils.text_processor import chunk_text
from utils.embeddings import EmbeddingGenerator
from utils.vector_store import VectorStore
from utils.rag_engine import RAGEngine


def get_cors_headers():
    """CORS headers for API Gateway"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }


def ingest_video(event, context):
    """
    Endpoint: POST /ingest
    Process YouTube video: extract transcript, chunk, embed, store

    Input: {"url": "https://youtube.com/watch?v=..."}
    Output: {"success": true, "video_id": "...", "chunks_count": 42}
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        video_url = body.get('url')

        if not video_url:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Video URL is required'})
            }

        # Step 1: Extract transcript
        print(f"Extracting transcript for: {video_url}")
        transcript_result = get_transcript(video_url)

        if not transcript_result['success']:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': transcript_result['error']})
            }

        video_id = transcript_result['video_id']
        transcript = transcript_result['transcript']
        print(f"Transcript extracted: {len(transcript)} characters")

        # Step 2: Chunk text
        chunk_size = int(os.getenv('CHUNK_SIZE', 500))
        chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 50))

        chunks = chunk_text(transcript, chunk_size=chunk_size, overlap=chunk_overlap)
        print(f"Text chunked into {len(chunks)} pieces")

        # Step 3: Generate embeddings
        embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
        embedder = EmbeddingGenerator(model=embedding_model)

        embeddings_result = embedder.generate_embeddings(chunks)

        if not embeddings_result['success']:
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': embeddings_result['error']})
            }

        embeddings = embeddings_result['embeddings']
        print(f"Generated {len(embeddings)} embeddings, dimension: {embeddings_result['dimension']}")

        # Step 4: Create and store vector index
        vector_store = VectorStore(dimension=embeddings_result['dimension'])
        vector_store.add_vectors(embeddings, chunks)

        # Save to S3
        bucket_name = os.getenv('S3_BUCKET_NAME')
        if bucket_name:
            success = vector_store.save_to_s3(bucket_name, video_id)
            if not success:
                print("Warning: Failed to save to S3")

        print(f"Vector store created and saved for video: {video_id}")

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'video_id': video_id,
                'chunks_count': len(chunks),
                'transcript_length': len(transcript),
                'message': 'Video processed successfully'
            })
        }

    except Exception as e:
        print(f"Error in ingest_video: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Internal error: {str(e)}'})
        }


def chat(event, context):
    """
    Endpoint: POST /chat
    Answer questions based on video transcript

    Input: {"video_id": "...", "question": "What is this video about?"}
    Output: {"success": true, "answer": "...", "context_used": 3}
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        video_id = body.get('video_id')
        question = body.get('question')

        if not video_id or not question:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'video_id and question are required'})
            }

        print(f"Processing question for video {video_id}: {question}")

        # Load vector store from S3
        bucket_name = os.getenv('S3_BUCKET_NAME')
        vector_store = VectorStore.load_from_s3(bucket_name, video_id)

        if not vector_store:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': 'Video not found. Please ingest the video first.'})
            }

        # Use RAGEngine to handle the complete RAG workflow
        llm_model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        rag_engine = RAGEngine(model=llm_model)

        answer_result = rag_engine.answer_question(question, vector_store, video_id)

        if not answer_result['success']:
            return {
                'statusCode': 500,
                'headers': get_cors_headers(),
                'body': json.dumps({'error': answer_result['error']})
            }

        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'success': True,
                'answer': answer_result['answer'],
                'context_used': answer_result['context_used'],
                'video_id': video_id
            })
        }

    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': f'Internal error: {str(e)}'})
        }


def handler(event, context):
    """
    Main Lambda handler - routes to appropriate function
    """
    # Handle OPTIONS for CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': ''
        }

    # Route based on path
    path = event.get('path', '')

    if '/ingest' in path:
        return ingest_video(event, context)
    elif '/chat' in path:
        return chat(event, context)
    else:
        return {
            'statusCode': 404,
            'headers': get_cors_headers(),
            'body': json.dumps({'error': 'Endpoint not found'})
        }
