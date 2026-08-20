from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import numpy as np
from app.repositories.base import BaseRepository
from app.models.chunk import DocumentChunk
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DocumentChunk)

    async def save_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks

    async def get_chunks_by_document_id(self, document_id: str) -> List[DocumentChunk]:
        result = await self.session.execute(
            select(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        return list(result.scalars().all())

    async def get_chunks_by_session_id(self, session_id: str) -> List[DocumentChunk]:
        result = await self.session.execute(
            select(DocumentChunk).where(DocumentChunk.session_id == session_id)
        )
        return list(result.scalars().all())

    async def search_similar_chunks(
        self,
        session_id: str,
        query_embedding: List[float],
        top_k: int = 4,
        similarity_threshold: float = 0.25
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Searches chunks belonging to session_id using vector cosine similarity.
        Works seamlessly on SQLite and Supabase / Postgres.
        """
        chunks = await self.get_chunks_by_session_id(session_id)
        if not chunks or not query_embedding:
            return []

        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []

        scored_chunks: List[Tuple[DocumentChunk, float]] = []

        for chunk in chunks:
            if not chunk.embedding_json:
                continue
            try:
                emb_list = json.loads(chunk.embedding_json)
                chunk_vec = np.array(emb_list, dtype=np.float32)
                chunk_norm = np.linalg.norm(chunk_vec)
                
                if chunk_norm > 0:
                    similarity = float(np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm))
                    if similarity >= similarity_threshold:
                        scored_chunks.append((chunk, similarity))
            except Exception as e:
                logger.warning(f"Error computing similarity for chunk {chunk.id}: {e}")
                continue

        # Sort descending by cosine similarity
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]
