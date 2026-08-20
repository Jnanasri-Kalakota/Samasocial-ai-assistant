import httpx
import json
from typing import AsyncGenerator, List, Dict, Any
from app.services.llm.base import BaseLLMProvider
from app.core.config import settings
from app.core.exceptions import LLMProviderError

class OpenAIClient(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise LLMProviderError("OPENAI_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", "https://api.openai.com/v1/chat/completions", json=payload, headers=headers) as response:
                if response.status_code != 200:
                    err = await response.aread()
                    raise LLMProviderError(f"OpenAI error: {err.decode('utf-8')}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            token = delta.get("content", "")
                            if token:
                                yield token
                        except Exception:
                            continue

    async def generate_text(self, messages: List[Dict[str, str]], temperature: float = 0.2) -> str:
        collected = []
        async for token in self.generate_stream(messages, temperature):
            collected.append(token)
        return "".join(collected)
