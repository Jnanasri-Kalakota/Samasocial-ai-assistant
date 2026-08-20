import httpx
import asyncio
from typing import List
from app.services.embeddings.base import BaseEmbeddingProvider
from app.core.config import settings
from app.core.exceptions import EmbeddingError
import logging

logger = logging.getLogger(__name__)

class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_EMBED_MODEL

    async def embed_query(self, text: str) -> List[float]:
        results = await self.embed_documents([text])
        return results[0] if results else []

    async def embed_documents(self, texts: List[str], batch_size: int = 50) -> List[List[float]]:
        if not texts:
            return []

        embeddings: List[List[float]] = []
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Try native batch embedding first (/api/embed)
            try:
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    res = await client.post(
                        f"{self.base_url}/api/embed",
                        json={"model": self.model, "input": batch}
                    )
                    if res.status_code == 200:
                        data = res.json()
                        batch_embs = data.get("embeddings", [])
                        embeddings.extend(batch_embs)
                    else:
                        raise Exception(f"Status {res.status_code}")
                return embeddings
            except Exception as batch_err:
                logger.warning(f"Batch embed endpoint unavailable or failed: {batch_err}. Falling back to concurrent worker pool.")

            # Fallback: High-throughput concurrent worker pool (/api/embeddings)
            sem = asyncio.Semaphore(10)
            async def embed_single(t: str) -> List[float]:
                async with sem:
                    try:
                        res = await client.post(
                            f"{self.base_url}/api/embeddings",
                            json={"model": self.model, "prompt": t}
                        )
                        if res.status_code == 200:
                            return res.json().get("embedding", [])
                    except Exception as e:
                        logger.error(f"Single chunk embedding error: {e}")
                    return []

            tasks = [embed_single(t) for t in texts]
            results = await asyncio.gather(*tasks)
            return list(results)
