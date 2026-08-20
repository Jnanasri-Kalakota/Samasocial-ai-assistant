import httpx
from typing import List
from app.services.embeddings.base import BaseEmbeddingProvider
from app.core.config import settings
from app.core.exceptions import EmbeddingError
import logging

logger = logging.getLogger(__name__)

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_EMBED_MODEL

    async def embed_query(self, text: str) -> List[float]:
        res = await self.embed_documents([text])
        return res[0] if res else []

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            raise EmbeddingError("OPENAI_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "input": texts,
            "model": self.model
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                res = await client.post("https://api.openai.com/v1/embeddings", json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return [item["embedding"] for item in data["data"]]
                else:
                    raise EmbeddingError(f"OpenAI embedding error: {res.text}")
            except Exception as e:
                raise EmbeddingError(f"OpenAI embedding call failed: {str(e)}")
