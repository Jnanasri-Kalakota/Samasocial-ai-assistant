import httpx
import json
import os
from typing import AsyncGenerator, List, Dict, Any
from app.services.llm.base import BaseLLMProvider
from app.core.config import settings
from app.core.exceptions import LLMProviderError
import logging

logger = logging.getLogger(__name__)

class OllamaClient(BaseLLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.num_threads = max(2, os.cpu_count() or 4)

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_thread": self.num_threads,
                "num_ctx": 2048,
                "num_predict": 250
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    if response.status_code != 200:
                        err_body = await response.aread()
                        raise LLMProviderError(f"Ollama error {response.status_code}: {err_body.decode('utf-8')}")

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk_data = json.loads(line)
                            msg = chunk_data.get("message", {})
                            token = msg.get("content", "")
                            if token:
                                yield token
                            if chunk_data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            raise LLMProviderError(f"Could not connect to Ollama at {self.base_url}. Is Ollama running?")
        except Exception as e:
            if isinstance(e, LLMProviderError):
                raise e
            raise LLMProviderError(f"Ollama streaming error: {str(e)}")

    async def generate_text(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2
    ) -> str:
        collected = []
        async for token in self.generate_stream(messages, temperature):
            collected.append(token)
        return "".join(collected)
