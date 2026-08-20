from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.repositories.base import BaseRepository
from app.models.document import Document

class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def get_by_session_id(self, session_id: str) -> List[Document]:
        result = await self.session.execute(
            select(Document)
            .where(Document.session_id == session_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_summary(self, doc_id: str, summary: str, chunk_count: int) -> Optional[Document]:
        doc = await self.get_by_id(doc_id)
        if doc:
            doc.summary = summary
            doc.chunk_count = chunk_count
            await self.session.flush()
            await self.session.refresh(doc)
        return doc
