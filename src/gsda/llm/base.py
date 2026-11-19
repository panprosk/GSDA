from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Tuple

ChatMessage = Dict[str, str]


class LLMError(Exception):
    """Σφάλμα provider με μήνυμα κατάλληλο για εμφάνιση στον χρήστη."""


@dataclass(frozen=True)
class LLMResponse:
    content: str
    provider: str
    model: str
    is_mock: bool = False


class LLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, messages: List[ChatMessage]) -> LLMResponse:
        """Στέλνει messages (role/content) και επιστρέφει την απάντηση."""

    def check_available(self) -> Tuple[bool, str]:
        return True, "OK"
