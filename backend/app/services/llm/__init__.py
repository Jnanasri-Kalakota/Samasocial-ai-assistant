from app.services.llm.base import BaseLLMProvider
from app.services.llm.ollama_client import OllamaClient
from app.services.llm.groq_client import GroqClient
from app.services.llm.openai_client import OpenAIClient
from app.services.llm.prompt_builder import PromptBuilder
from app.core.config import settings

def get_llm_provider() -> BaseLLMProvider:
    if settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
        return GroqClient()
    elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return OpenAIClient()
    return OllamaClient()
