"""Escolha do adaptador de LLM a partir das configurações."""

from manki.config import Provider, Settings
from manki.domain.ports import LLMProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm.provider is Provider.GEMINI:
        from manki.providers.llm.gemini_provider import GeminiProvider

        return GeminiProvider(settings.llm)

    from manki.providers.llm.openai_provider import OpenAICompatibleProvider

    return OpenAICompatibleProvider(settings.llm, timeout=settings.request_timeout)
