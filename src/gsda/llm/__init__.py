from __future__ import annotations

from gsda.config.settings import Settings
from gsda.llm.base import LLMError, LLMProvider, LLMResponse
from gsda.llm.mock_provider import MockProvider
from gsda.llm.qwen_provider import QwenProvider


def create_provider(settings: Settings) -> LLMProvider:
    if settings.provider == "mock":
        return MockProvider()
    if settings.provider in ("qwen", "qwen3", "openai"):
        return QwenProvider(settings)
    raise LLMError(f"Άγνωστος LLM_PROVIDER: {settings.provider!r} (έγκυρα: mock, qwen)")


__all__ = ["create_provider", "LLMError", "LLMProvider", "LLMResponse", "MockProvider", "QwenProvider"]
