from typing import List, Tuple
from app.repositories.chunk_repo import ChunkRepository
from app.services.embeddings.base import BaseEmbeddingProvider
from app.models.chunk import DocumentChunk
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self, chunk_repo: ChunkRepository, embedding_provider: BaseEmbeddingProvider):
        self.chunk_repo = chunk_repo
        self.embedding_provider = embedding_provider

    async def retrieve_context(
        self,
        session_id: str,
        query: str,
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Retrieves top relevant chunks for a user query scoped to the current session.
        """
        k = top_k or settings.TOP_K_CHUNKS
        thresh = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD
        
        query_embedding = await self.embedding_provider.embed_query(query)
        if not query_embedding:
            logger.warning("Empty query embedding generated.")
            return []

        results = await self.chunk_repo.search_similar_chunks(
            session_id=session_id,
            query_embedding=query_embedding,
            top_k=k,
            similarity_threshold=thresh
        )
        return results
