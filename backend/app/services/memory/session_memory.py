from typing import List, Dict
from app.repositories.session_repo import SessionRepository

class SessionMemoryService:
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    async def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        messages = await self.session_repo.get_messages(session_id=session_id, limit=limit)
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    async def save_message_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        citations: List[dict] = None
    ):
        await self.session_repo.add_message(session_id=session_id, role="user", content=user_message)
        await self.session_repo.add_message(
            session_id=session_id,
            role="assistant",
            content=assistant_message,
            citations=citations
        )
