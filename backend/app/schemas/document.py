from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class URLIngestRequest(BaseModel):
    session_id: str
    url: str

class DocumentResponse(BaseModel):
    id: str
    session_id: str
    source_type: str
    source_name: str
    source_url: Optional[str] = None
    summary: Optional[str] = None
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class SourceSummaryResponse(BaseModel):
    id: str
    source_name: str
    source_type: str
    summary: str
    chunk_count: int
