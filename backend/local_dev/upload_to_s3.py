#!/usr/bin/env python3
"""
Upload pre-processed video to S3 for demo
"""
import os
import sys
import boto3
from dotenv import load_dotenv

# Load environment
parent_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(parent_dir, '.env'))
sys.path.insert(0, parent_dir)

from utils.transcript_extractor import get_transcript
from utils.text_processor import chunk_text
from utils.embeddings import EmbeddingGenerator
from utils.vector_store import VectorStore


def preprocess_and_upload(video_url, bucket_name):
    """Process video locally and upload to S3"""

    print("Processing video locally...")

    # Extract transcript
    transcript_result = get_transcript(video_url)
    if not transcript_result['success']:
        print(f"Error: {transcript_result['error']}")
        return

    video_id = transcript_result['video_id']
    transcript_text = transcript_result['transcript']
    print(f"✓ Transcript: {len(transcript_text)} chars")

    # Chunk
    chunks = chunk_text(transcript_text)
    print(f"✓ Chunks: {len(chunks)}")

    # Generate embeddings
    embedding_gen = EmbeddingGenerator()
    embedding_result = embedding_gen.generate_embeddings(chunks)

    if not embedding_result['success']:
        print(f"Error: {embedding_result['error']}")
        return

    embeddings = embedding_result['embeddings']
    print(f"✓ Embeddings: {len(embeddings)}")

    # Create vector store
    vector_store = VectorStore()
    vector_store.add_vectors(embeddings, chunks)
    print(f"✓ Vector store created")

    # Upload to S3
    print(f"\nUploading to S3 bucket: {bucket_name}")
    success = vector_store.save_to_s3(bucket_name, video_id)

    if success:
        print(f"\n✅ Success! Video {video_id} ready for Lambda!")
        print(f"\nNow you can chat with this video via Lambda:")
        print(f"Video ID: {video_id}")
    else:
        print("\n❌ Upload failed")


if __name__ == "__main__":
    video_url = input("Enter YouTube URL: ").strip()
    bucket_name = os.getenv('S3_BUCKET_NAME', 'single-video-twin-vectorstorebucket-xxxxxxx')

    print(f"\nUsing bucket: {bucket_name}")
    print("(Set S3_BUCKET_NAME in .env to change)\n")

    preprocess_and_upload(video_url, bucket_name)
