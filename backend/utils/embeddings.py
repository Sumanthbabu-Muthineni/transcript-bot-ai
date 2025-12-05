"""
Embeddings Module
Handles creation of vector embeddings using OpenAI API
"""
import os
from openai import OpenAI


class EmbeddingGenerator:
    """
    Generates embeddings for text chunks using OpenAI's embedding models
    """

    def __init__(self, api_key=None, model="text-embedding-3-small"):
        """
        Initialize with OpenAI API key
        model options:
        - text-embedding-3-small: 1536 dimensions, $0.02/1M tokens
        - text-embedding-3-large: 3072 dimensions, $0.13/1M tokens
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def generate_embeddings(self, texts):
        """
        Generate embeddings for list of text chunks
        Returns list of embedding vectors
        """
        try:
            # OpenAI API accepts list of texts
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )

            # Extract embedding vectors
            embeddings = [item.embedding for item in response.data]

            return {
                'success': True,
                'embeddings': embeddings,
                'dimension': len(embeddings[0]) if embeddings else 0,
                'count': len(embeddings)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Embedding generation failed: {str(e)}'
            }

    def generate_single_embedding(self, text):
        """
        Generate embedding for single text
        """
        result = self.generate_embeddings([text])

        if result['success']:
            return {
                'success': True,
                'embedding': result['embeddings'][0]
            }
        return result
