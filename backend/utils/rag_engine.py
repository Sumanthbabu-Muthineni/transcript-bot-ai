"""
RAG Engine Module
Orchestrates retrieval and generation for question answering
"""
import os
from openai import OpenAI
from .embeddings import EmbeddingGenerator


class RAGEngine:
    """
    Handles RAG workflow: retrieval + generation
    """

    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        """
        Initialize with OpenAI API key for LLM
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.embedding_gen = EmbeddingGenerator(api_key=self.api_key)
        self.top_k = int(os.getenv('TOP_K_RESULTS', 3))

    def generate_answer(self, question, context_chunks):
        """
        Generate answer using retrieved context chunks
        The "Twin" aspect: System prompt instructs to answer only from context
        """
        # Combine context chunks
        context = "\n\n".join([chunk['text'] for chunk in context_chunks])

        # System prompt that creates the "Twin" behavior
        system_prompt = """You are an AI assistant that answers questions based STRICTLY on the provided video transcript context.

CRITICAL RULES:
1. ONLY use information from the context provided below
2. If the context doesn't contain the answer, say "I don't have information about that in this video"
3. Try to mimic the speaker's tone and style from the transcript
4. Keep answers concise and natural, as if the speaker is responding
5. Do NOT use external knowledge or make assumptions beyond the context

Your goal is to be a "digital twin" of the speaker in the video."""

        user_prompt = f"""Context from video transcript:
{context}

Question: {question}

Answer the question based solely on the context above. If you cannot answer from the context, say so clearly."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,  # Balanced creativity
                max_tokens=500
            )

            answer = response.choices[0].message.content

            return {
                'success': True,
                'answer': answer,
                'context_used': len(context_chunks),
                'model': self.model
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Answer generation failed: {str(e)}'
            }

    def answer_question(self, question, vector_store, video_id):
        """
        Complete RAG workflow: embed question -> retrieve context -> generate answer

        Args:
            question: User's question
            vector_store: VectorStore instance with indexed chunks
            video_id: Video identifier (for logging/tracking)

        Returns:
            dict with success, answer, context_used, and video_id
        """
        try:
            # Step 1: Generate embedding for the question
            embedding_result = self.embedding_gen.generate_single_embedding(question)

            if not embedding_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to embed question: {embedding_result.get('error', 'Unknown error')}"
                }

            query_embedding = embedding_result['embedding']

            # Step 2: Retrieve relevant chunks from vector store
            context_chunks = vector_store.search(query_embedding, top_k=self.top_k)

            if not context_chunks:
                return {
                    'success': False,
                    'error': 'No relevant context found in the video'
                }

            # Step 3: Generate answer using retrieved context
            answer_result = self.generate_answer(question, context_chunks)

            if answer_result['success']:
                answer_result['video_id'] = video_id

            return answer_result

        except Exception as e:
            return {
                'success': False,
                'error': f'RAG pipeline failed: {str(e)}'
            }
