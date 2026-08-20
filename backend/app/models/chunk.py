from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json
from app.core.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}") # JSON string containing page_number, slide_number, timestamp etc.
    embedding_json = Column(Text, nullable=True) # Serialized float list [0.12, ...]
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")

    @property
    def metadata_dict(self) -> dict:
        try:
            return json.loads(self.metadata_json)
        except Exception:
            return {}

    @property
    def embedding_list(self) -> list:
        try:
            return json.loads(self.embedding_json) if self.embedding_json else []
        except Exception:
            return []
