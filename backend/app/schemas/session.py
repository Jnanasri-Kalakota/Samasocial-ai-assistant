from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.document import DocumentResponse
from app.schemas.chat import MessageView

class SessionCreate(BaseModel):
    title: Optional[str] = "New Learning Session"

class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    document_count: int = 0

    class Config:
        from_attributes = True

class SessionDetailResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    documents: List[DocumentResponse] = []
    messages: List[MessageView] = []
