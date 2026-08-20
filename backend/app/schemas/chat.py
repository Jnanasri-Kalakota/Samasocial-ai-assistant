from pydantic import BaseModel
from typing import Optional, List
from app.schemas.citation import CitationItem

class ChatRequest(BaseModel):
    session_id: str
    message: str
    simple_terms: bool = False # Flag for "explain in simple terms" mode

class MessageView(BaseModel):
    id: str
    role: str
    content: str
    citations: List[CitationItem] = []
    created_at: str

class ChatStreamChunk(BaseModel):
    event: str # 'token', 'citation', 'done', 'error'
    data: str
    citations: Optional[List[CitationItem]] = None
