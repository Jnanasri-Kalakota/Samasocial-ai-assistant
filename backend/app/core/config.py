from pydantic_settings import BaseSettings
from typing import Optional, Literal
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "SamaSocial AI Assistant"
    API_V1_PREFIX: str = "/api/v1"
    
    # Persistence Configuration
    DATABASE_TYPE: Literal["sqlite", "supabase", "postgresql"] = "sqlite"
    DATABASE_URL: str = "sqlite+aiosqlite:///./samasocial.db"
    
    # LLM Configuration
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    
    # Optional Cloud LLM Keys
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: str = "ollama"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 768
    
    # Retrieval Configuration
    TOP_K_CHUNKS: int = 4
    SIMILARITY_THRESHOLD: float = 0.25
    
    # Semantic Chunking Configuration
    # 1200 chars (~250 words) per chunk is optimal for RAG accuracy and fast ingestion
    CHUNK_SIZE: int = 1200
    CHUNK_OVERLAP: int = 200
    
    # Upload limits (50MB)
    MAX_UPLOAD_SIZE: int = 52428800
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"

settings = Settings()
