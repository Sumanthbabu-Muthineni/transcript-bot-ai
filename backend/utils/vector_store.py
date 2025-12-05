"""
Vector Store Module
Handles FAISS index creation and similarity search
"""
import os
import pickle
import numpy as np
import faiss
import boto3
from io import BytesIO


class VectorStore:
    """
    Manages FAISS vector index for semantic search
    Supports persistence to S3 for serverless architecture
    """

    def __init__(self, dimension=1536):
        """
        dimension: embedding vector size (1536 for text-embedding-3-small)
        """
        self.dimension = dimension
        # Use IndexFlatL2 for exact cosine similarity search
        # Small datasets don't need approximate search algorithms
        self.index = faiss.IndexFlatL2(dimension)
        self.texts = []  # Store original text chunks

    def add_vectors(self, embeddings, texts):
        """
        Add embeddings and corresponding texts to index
        embeddings: list of vectors (numpy array or list)
        texts: list of original text chunks
        """
        if not embeddings or not texts:
            return False

        if len(embeddings) != len(texts):
            raise ValueError("Number of embeddings must match number of texts")

        # Convert to numpy array if needed
        embeddings_array = np.array(embeddings).astype('float32')

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(embeddings_array)

        # Add to index
        self.index.add(embeddings_array)
        self.texts.extend(texts)

        return True

    def search(self, query_embedding, top_k=3):
        """
        Search for most similar vectors
        Returns top_k most relevant text chunks
        """
        if self.index.ntotal == 0:
            return []

        # Convert and normalize query embedding
        query_array = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_array)

        # Search
        distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))

        # Return results with similarity scores
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # Valid result
                results.append({
                    'text': self.texts[idx],
                    'score': float(1 / (1 + distances[0][i])),  # Convert distance to similarity
                    'index': int(idx)
                })

        return results

    def save_to_s3(self, bucket_name, video_id):
        """
        Save index and texts to S3
        """
        try:
            s3_client = boto3.client('s3')

            # Save FAISS index
            index_buffer = BytesIO()
            faiss.write_index(self.index, faiss.BufferedIOWriter(faiss.PyCallbackIOWriter(index_buffer.write)))
            index_buffer.seek(0)

            s3_client.put_object(
                Bucket=bucket_name,
                Key=f'indexes/{video_id}/faiss.index',
                Body=index_buffer.getvalue()
            )

            # Save texts
            texts_buffer = BytesIO()
            pickle.dump(self.texts, texts_buffer)
            texts_buffer.seek(0)

            s3_client.put_object(
                Bucket=bucket_name,
                Key=f'indexes/{video_id}/texts.pkl',
                Body=texts_buffer.getvalue()
            )

            return True

        except Exception as e:
            print(f"Error saving to S3: {str(e)}")
            return False

    @classmethod
    def load_from_s3(cls, bucket_name, video_id, dimension=1536):
        """
        Load index and texts from S3
        """
        try:
            s3_client = boto3.client('s3')

            # Load FAISS index
            index_obj = s3_client.get_object(
                Bucket=bucket_name,
                Key=f'indexes/{video_id}/faiss.index'
            )
            index_buffer = BytesIO(index_obj['Body'].read())
            index = faiss.read_index(faiss.BufferedIOReader(faiss.PyCallbackIOReader(index_buffer.read)))

            # Load texts
            texts_obj = s3_client.get_object(
                Bucket=bucket_name,
                Key=f'indexes/{video_id}/texts.pkl'
            )
            texts = pickle.load(BytesIO(texts_obj['Body'].read()))

            # Create instance and restore state
            store = cls(dimension=dimension)
            store.index = index
            store.texts = texts

            return store

        except Exception as e:
            print(f"Error loading from S3: {str(e)}")
            return None
