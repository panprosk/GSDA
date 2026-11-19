from __future__ import annotations

from typing import List

from gsda.llm.base import ChatMessage, LLMProvider, LLMResponse

MOCK_BANNER = "[MOCK – όχι απάντηση Qwen3]"


class MockProvider(LLMProvider):
    name = "mock"

    def generate(self, messages: List[ChatMessage]) -> LLMResponse:
        users = [m["content"] for m in messages if m["role"] == "user"]
        last = users[-1] if users else ""
        content = (
            f"{MOCK_BANNER}\n\n"
            f"Λήφθηκε το μήνυμά σου: «{last}». "
            f"Το context περιέχει {len(users)} μήνυμα(τα) χρήστη. "
            "Αυτή είναι προσομοιωμένη απάντηση για δοκιμή του Interface."
        )
        return LLMResponse(content=content, provider="mock", model="mock", is_mock=True)
