#!/usr/bin/env python3
"""
Local testing script for the RAG pipeline
Tests transcript extraction, chunking, embeddings, and chat without S3
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
# Load handled above

# Add current directory to path
parent_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(parent_dir, '.env'))
sys.path.insert(0, parent_dir)

from utils.transcript_extractor import get_transcript
from utils.text_processor import chunk_text
from utils.embeddings import EmbeddingGenerator
from utils.vector_store import VectorStore
from utils.rag_engine import RAGEngine


def test_pipeline(video_url: str, question: str):
    """Test the complete RAG pipeline locally"""

    print("=" * 60)
    print("Starting Local RAG Pipeline Test")
    print("=" * 60)

    # Step 1: Extract transcript
    print(f"\n1. Extracting transcript from: {video_url}")
    transcript_result = get_transcript(video_url)

    if not transcript_result['success']:
        print(f"❌ Error: {transcript_result['error']}")
        return

    video_id = transcript_result['video_id']
    transcript_text = transcript_result['transcript']
    print(f"✓ Transcript extracted: {len(transcript_text)} characters")
    print(f"✓ Video ID: {video_id}")

    # Step 2: Chunk text
    print(f"\n2. Chunking text...")
    chunks = chunk_text(transcript_text)
    print(f"✓ Created {len(chunks)} chunks")

    # Step 3: Generate embeddings
    print(f"\n3. Generating embeddings...")
    embedding_gen = EmbeddingGenerator()
    embedding_result = embedding_gen.generate_embeddings(chunks)

    if not embedding_result['success']:
        print(f"❌ Error: {embedding_result['error']}")
        return

    embeddings = embedding_result['embeddings']
    print(f"✓ Generated {len(embeddings)} embeddings ({embedding_result['dimension']} dimensions)")

    # Step 4: Create vector store (in-memory, no S3)
    print(f"\n4. Creating vector store...")
    vector_store = VectorStore()  # Uses default dimension=1536
    vector_store.add_vectors(embeddings, chunks)
    print(f"✓ Vector store created with {len(chunks)} vectors")

    # Step 5: Initialize RAG engine
    print(f"\n5. Initializing RAG engine...")
    rag = RAGEngine()

    # Step 6: Ask question
    print(f"\n6. Asking question: '{question}'")
    print("-" * 60)

    result = rag.answer_question(question, vector_store, video_id)

    if result['success']:
        print(f"\n✓ Answer:\n{result['answer']}")
        print(f"\n✓ Used {result['context_used']} context chunks")
    else:
        print(f"❌ Error: {result['error']}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


def main():
    """Interactive test menu"""

    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("Please set it in your .env file")
        return

    print("\n🎬 YouTube RAG Pipeline - Local Test")
    print("=" * 60)

    # Get video URL
    default_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    video_url = input(f"\nEnter YouTube URL (or press Enter for demo): ").strip()
    if not video_url:
        video_url = default_url

    # Get question
    default_question = "What is this video about?"
    question = input(f"Enter your question (or press Enter for default): ").strip()
    if not question:
        question = default_question

    # Run test
    test_pipeline(video_url, question)


if __name__ == "__main__":
    main()
