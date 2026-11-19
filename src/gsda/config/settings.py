from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Mapping, Optional


@dataclass(frozen=True)
class Settings:
    provider: str = "mock"
    base_url: str = "http://127.0.0.1:8000/v1"
    api_key: str = field(default="", repr=False)
    model: str = "Qwen/Qwen3-8B"
    timeout_seconds: float = 600.0
    max_tokens: int = 4096
    temperature: float = 0.6
    db_path: str = "data/gsda.db"
    context_max_messages: int = 12

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "Settings":
        e = os.environ if env is None else env
        d = cls()

        def get(key: str, default):
            v = e.get(key)
            return default if v is None or v == "" else v

        return cls(
            provider=str(get("LLM_PROVIDER", d.provider)).strip().lower(),
            base_url=str(get("LLM_BASE_URL", d.base_url)),
            api_key=e.get("LLM_API_KEY", "") or "",
            model=str(get("LLM_MODEL", d.model)),
            timeout_seconds=float(get("LLM_TIMEOUT_SECONDS", d.timeout_seconds)),
            max_tokens=int(get("LLM_MAX_TOKENS", d.max_tokens)),
            temperature=float(get("LLM_TEMPERATURE", d.temperature)),
            db_path=str(get("GSDA_DB_PATH", d.db_path)),
            context_max_messages=int(get("GSDA_CONTEXT_MAX_MESSAGES", d.context_max_messages)),
        )
