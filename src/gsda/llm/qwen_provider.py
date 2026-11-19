from __future__ import annotations

import re
from typing import List, Optional, Tuple

import openai
from openai import OpenAI

from gsda.config.settings import Settings
from gsda.llm.base import ChatMessage, LLMError, LLMProvider, LLMResponse


_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
MAX_CONTINUATIONS = 3
CONTINUE_PROMPT = (
    "Your previous answer was cut off. Continue exactly from where it stopped, in the same "
    "language, without repeating anything and without any introduction."
)


class QwenProvider(LLMProvider):
    """Qwen3 μέσω OpenAI-compatible API. Δεν κάνει ποτέ fallback σε mock."""

    name = "qwen"

    def __init__(self, settings: Settings, client: Optional[OpenAI] = None):
        self.settings = settings
        self.client = client or OpenAI(
            base_url=settings.base_url,
            # Το SDK απαιτεί μη κενό key· τοπικοί servers (vLLM) συνήθως δεν ελέγχουν.
            api_key=settings.api_key or "EMPTY",
            timeout=settings.timeout_seconds,
            max_retries=0,
        )

    def build_request(self, messages: List[ChatMessage]) -> dict:
        return {
            "model": self.settings.model,
            "messages": messages,
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
            # Qwen3: απενεργοποίηση thinking ώστε η απάντηση να είναι καθαρή.
            "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
        }

    def _complete(self, messages: List[ChatMessage]):
        try:
            return self.client.chat.completions.create(**self.build_request(messages))
        except openai.APITimeoutError as e:
            raise LLMError(
                f"Timeout ({self.settings.timeout_seconds:.0f}s) στο Qwen3 API {self.settings.base_url}."
            ) from e
        except openai.APIConnectionError as e:
            raise LLMError(
                f"Αποτυχία σύνδεσης με το Qwen3 API ({self.settings.base_url}). "
                "Έλεγξε ότι ο server τρέχει στον Krylov και ότι το SSH tunnel είναι ανοιχτό."
            ) from e
        except openai.APIStatusError as e:
            raise LLMError(f"Το Qwen3 API επέστρεψε σφάλμα HTTP {e.status_code}.") from e
        except openai.OpenAIError as e:
            raise LLMError(f"Σφάλμα Qwen3 API: {type(e).__name__}") from e

    @staticmethod
    def _clean(resp, strip: bool = True) -> str:
        content = (resp.choices[0].message.content or "") if resp.choices else ""
        # Αν ο server αγνοήσει το enable_thinking, αφαιρούμε το <think>…</think>.
        content = _THINK_RE.sub("", content)
        return content.strip() if strip else content

    def generate(self, messages: List[ChatMessage]) -> LLMResponse:
        resp = self._complete(messages)
        content = self._clean(resp, strip=False)
        if not content.strip():
            raise LLMError("Το Qwen3 API επέστρεψε κενή απάντηση.")

        # Αν η απάντηση κόπηκε από το όριο tokens, ζητάμε συνέχεια ώστε να μη μένει μισή.
        base = list(messages)
        for _ in range(MAX_CONTINUATIONS):
            if resp.choices[0].finish_reason != "length":
                break
            resp = self._complete(
                base + [
                    {"role": "assistant", "content": content},
                    {"role": "user", "content": CONTINUE_PROMPT},
                ]
            )
            more = self._clean(resp, strip=False)
            if not more.strip():
                break
            content += more
        return LLMResponse(content=content.strip(), provider="qwen", model=self.settings.model)

    def check_available(self) -> Tuple[bool, str]:
        try:
            models = [m.id for m in self.client.models.list().data]
        except openai.APITimeoutError:
            return False, f"Timeout προς {self.settings.base_url}"
        except openai.APIConnectionError:
            return False, f"Αδυναμία σύνδεσης με {self.settings.base_url}"
        except openai.OpenAIError as e:
            return False, f"Σφάλμα API: {type(e).__name__}"
        if self.settings.model not in models:
            return False, f"Το μοντέλο {self.settings.model} δεν βρέθηκε (διαθέσιμα: {', '.join(models) or '-'})"
        return True, f"Συνδέθηκε: {self.settings.model}"
