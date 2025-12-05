"""
Text Processing Module
Handles chunking of transcript text for embedding
"""
import os
import tiktoken


def count_tokens(text, model="gpt-3.5-turbo"):
    """
    Count tokens in text using tiktoken
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks

    Strategy: Splits on sentence boundaries when possible to maintain context
    - chunk_size: target tokens per chunk
    - overlap: tokens to overlap between chunks (maintains context continuity)
    """
    # Split into sentences (basic approach)
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() + '.' for s in sentences if s.strip()]

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        # If adding this sentence exceeds chunk size, save current chunk
        if current_tokens + sentence_tokens > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(chunk_text)

            # Keep last few sentences for overlap
            overlap_sentences = []
            overlap_tokens = 0
            for s in reversed(current_chunk):
                s_tokens = count_tokens(s)
                if overlap_tokens + s_tokens <= overlap:
                    overlap_sentences.insert(0, s)
                    overlap_tokens += s_tokens
                else:
                    break

            current_chunk = overlap_sentences
            current_tokens = overlap_tokens

        current_chunk.append(sentence)
        current_tokens += sentence_tokens

    # Add final chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
