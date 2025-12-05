#!/usr/bin/env python3
"""
Local testing script with MOCK embeddings (no OpenAI API calls)
Tests the full pipeline structure without API costs
"""
import os
import sys
import numpy as np
from dotenv import load_dotenv

# Load environment variables
# Load handled above

# Add current directory to path
parent_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(parent_dir, '.env'))
sys.path.insert(0, parent_dir)

from utils.transcript_extractor import get_transcript
from utils.text_processor import chunk_text
from utils.vector_store import VectorStore


def test_pipeline_mock(video_url: str, question: str):
    """Test the RAG pipeline with mock embeddings (no API calls)"""

    print("=" * 60)
    print("Local RAG Pipeline Test (MOCK MODE - No API costs)")
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
    print(f"  First chunk preview: {chunks[0][:100]}...")

    # Step 3: Generate MOCK embeddings (random vectors)
    print(f"\n3. Generating MOCK embeddings (no API call)...")
    dimension = 1536
    mock_embeddings = []

    # Create random embeddings for each chunk
    np.random.seed(42)  # For reproducibility
    for i in range(len(chunks)):
        # Generate random normalized vector
        embedding = np.random.randn(dimension).astype('float32')
        # Normalize to unit length
        embedding = embedding / np.linalg.norm(embedding)
        mock_embeddings.append(embedding.tolist())

    print(f"✓ Generated {len(mock_embeddings)} mock embeddings ({dimension} dimensions)")

    # Step 4: Create vector store
    print(f"\n4. Creating vector store...")
    vector_store = VectorStore()
    vector_store.add_vectors(mock_embeddings, chunks)
    print(f"✓ Vector store created with {len(chunks)} vectors")

    # Step 5: Test similarity search with mock query
    print(f"\n5. Testing similarity search...")

    # Create a mock query embedding (slightly similar to first chunk)
    query_embedding = np.random.randn(dimension).astype('float32')
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    results = vector_store.search(query_embedding.tolist(), top_k=3)
    print(f"✓ Search returned {len(results)} results")

    print(f"\n6. Top 3 relevant chunks for question: '{question}'")
    print("-" * 60)
    for i, result in enumerate(results, 1):
        print(f"\nChunk {i} (similarity: {result['score']:.4f}):")
        print(f"{result['text'][:200]}...")

    # Step 6: Mock RAG answer
    print(f"\n" + "=" * 60)
    print("MOCK ANSWER (In real mode, GPT would analyze these chunks)")
    print("=" * 60)
    print(f"\nBased on the transcript, the content discusses:")
    print(f"[This would be GPT's answer based on the {len(results)} retrieved chunks]")

    print(f"\n✓ Context chunks: {len(results)}")
    print(f"✓ Video ID: {video_id}")

    print("\n" + "=" * 60)
    print("✅ Pipeline Test Complete (Mock Mode)")
    print("=" * 60)
    print("\nNote: This test used random embeddings instead of OpenAI API.")
    print("Once you have OpenAI credits, run local_test.py for the real test.")


def main():
    """Interactive test menu"""

    print("\n🎬 YouTube RAG Pipeline - Mock Test (No API Costs)")
    print("=" * 60)

    # Get video URL
    video_url = input(f"\nEnter YouTube URL: ").strip()
    if not video_url:
        print("❌ URL required")
        return

    # Get question
    default_question = "What is this video about?"
    question = input(f"Enter your question (or press Enter for default): ").strip()
    if not question:
        question = default_question

    # Run test
    test_pipeline_mock(video_url, question)


if __name__ == "__main__":
    main()
