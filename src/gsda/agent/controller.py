from __future__ import annotations

from dataclasses import dataclass

from gsda.agent.prompts import build_system_prompt
from gsda.conversations.service import ConversationService
from gsda.llm.base import ChatMessage, LLMProvider, LLMResponse
from gsda.projects.registry import get_project


@dataclass(frozen=True)
class AgentReply:
    response: LLMResponse
    conversation_id: str


class AgentController:
    """Ανεξάρτητος από Streamlit και LLM provider. Φάση 1: χωρίς tools."""

    def __init__(self, provider: LLMProvider, conversations: ConversationService):
        self.provider = provider
        self.conversations = conversations

    def build_messages(
        self, conversation_id: str, user_text: str, language: str = "el"
    ) -> list[ChatMessage]:
        conv = self.conversations.get(conversation_id)
        if conv is None:
            raise KeyError(f"Άγνωστη συνομιλία: {conversation_id}")
        project = get_project(conv.project_id)
        system = build_system_prompt(conv.mode_id, project.context, language)
        history = self.conversations.recent_context(conversation_id)
        msgs: list[ChatMessage] = [{"role": "system", "content": system}]
        msgs += [{"role": m.role, "content": m.content} for m in history]
        msgs.append({"role": "user", "content": user_text})
        return msgs

    def handle_message(
        self, conversation_id: str, user_text: str, language: str = "el"
    ) -> AgentReply:
        """Σε LLMError δεν αποθηκεύεται τίποτα και το σφάλμα διαδίδεται στο UI."""
        messages = self.build_messages(conversation_id, user_text, language)
        response = self.provider.generate(messages)
        self.conversations.add_exchange(conversation_id, user_text, response.content)
        return AgentReply(response=response, conversation_id=conversation_id)
