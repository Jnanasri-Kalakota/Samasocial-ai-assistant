from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime
import json
from app.repositories.base import BaseRepository
from app.models.session import Session
from app.models.message import Message

class SessionRepository(BaseRepository[Session]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Session)

    async def get_with_relations(self, session_id: str) -> Optional[Session]:
        result = await self.session.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def list_sessions(self, limit: int = 50) -> List[Session]:
        result = await self.session.execute(
            select(Session).order_by(Session.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[dict]] = None
    ) -> Message:
        msg = Message(
            session_id=session_id,
            role=role,
            content=content,
            citations_json=json.dumps(citations or [])
        )
        self.session.add(msg)
        
        # Touch session updated_at
        session = await self.get_by_id(session_id)
        if session:
            session.updated_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(msg)
        return msg

    async def get_messages(self, session_id: str, limit: int = 100) -> List[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
