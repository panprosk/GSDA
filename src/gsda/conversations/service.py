from __future__ import annotations

from typing import List, Optional

from gsda.agent.modes import get_mode
from gsda.conversations.repository import Conversation, ConversationRepository, Message
from gsda.projects.registry import get_project


class ConversationService:
    def __init__(self, repo: ConversationRepository, context_max_messages: int = 12):
        self.repo = repo
        self.context_max_messages = context_max_messages

    def new_conversation(self, project_id: str, mode_id: str) -> Conversation:
        get_project(project_id)
        get_mode(mode_id)
        return self.repo.create_conversation(project_id, mode_id)

    def get(self, conversation_id: str) -> Optional[Conversation]:
        return self.repo.get_conversation(conversation_id)

    def history(self, project_id: Optional[str] = None) -> List[Conversation]:
        return self.repo.list_conversations(project_id)

    def messages(self, conversation_id: str) -> List[Message]:
        return self.repo.get_messages(conversation_id)

    def delete(self, conversation_id: str) -> bool:
        return self.repo.delete_conversation(conversation_id)

    def recent_context(self, conversation_id: str) -> List[Message]:
        return self.repo.get_messages(conversation_id, limit=self.context_max_messages)

    def add_exchange(self, conversation_id: str, user_text: str, assistant_text: str) -> None:
        conv = self.repo.get_conversation(conversation_id)
        first = not self.repo.get_messages(conversation_id, limit=1)
        self.repo.add_message(conversation_id, "user", user_text)
        self.repo.add_message(conversation_id, "assistant", assistant_text)
        if conv and first:
            title = " ".join(user_text.split())[:60] or conv.title
            self.repo.set_title(conversation_id, title)
