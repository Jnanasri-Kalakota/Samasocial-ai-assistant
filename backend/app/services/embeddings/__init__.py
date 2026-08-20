from app.services.embeddings.base import BaseEmbeddingProvider
from app.services.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.services.embeddings.openai_provider import OpenAIEmbeddingProvider
from app.core.config import settings

def get_embedding_provider() -> BaseEmbeddingProvider:
    if settings.EMBEDDING_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return OpenAIEmbeddingProvider()
    return OllamaEmbeddingProvider()
