"""Conversation management for the chatbot."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, role: str, content: str) -> Message:
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        return msg

    def get_history(self, max_messages: int = 10) -> list[Message]:
        return self.messages[-max_messages:]

    @property
    def message_count(self) -> int:
        return len(self.messages)


class ConversationStore:
    """In-memory conversation store."""

    def __init__(self):
        self._conversations: dict[str, Conversation] = {}

    def create_conversation(self) -> Conversation:
        conv = Conversation()
        self._conversations[conv.id] = conv
        return conv

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        return self._conversations.get(conversation_id)

    def get_or_create(self, conversation_id: str | None) -> Conversation:
        if conversation_id and conversation_id in self._conversations:
            return self._conversations[conversation_id]
        return self.create_conversation()

    @property
    def count(self) -> int:
        return len(self._conversations)
