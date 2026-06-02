"""Tests for conversation management."""

from hr_system.chatbot.conversation import Conversation, ConversationStore, Message


class TestMessage:
    def test_message_creation(self):
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.timestamp is not None


class TestConversation:
    def test_new_conversation_has_id(self):
        conv = Conversation()
        assert conv.id is not None
        assert len(conv.id) > 0

    def test_add_message(self):
        conv = Conversation()
        msg = conv.add_message("user", "Hi there")
        assert msg.role == "user"
        assert msg.content == "Hi there"
        assert conv.message_count == 1

    def test_multiple_messages(self):
        conv = Conversation()
        conv.add_message("user", "Hello")
        conv.add_message("assistant", "Hi! How can I help?")
        conv.add_message("user", "What's the leave policy?")
        assert conv.message_count == 3

    def test_get_history(self):
        conv = Conversation()
        for i in range(15):
            conv.add_message("user", f"Message {i}")
        history = conv.get_history(max_messages=10)
        assert len(history) == 10
        assert history[0].content == "Message 5"

    def test_get_history_fewer_than_max(self):
        conv = Conversation()
        conv.add_message("user", "Only one")
        history = conv.get_history(max_messages=10)
        assert len(history) == 1


class TestConversationStore:
    def test_create_conversation(self):
        store = ConversationStore()
        conv = store.create_conversation()
        assert conv.id is not None
        assert store.count == 1

    def test_get_conversation(self):
        store = ConversationStore()
        conv = store.create_conversation()
        found = store.get_conversation(conv.id)
        assert found is not None
        assert found.id == conv.id

    def test_get_conversation_not_found(self):
        store = ConversationStore()
        assert store.get_conversation("nonexistent") is None

    def test_get_or_create_existing(self):
        store = ConversationStore()
        conv = store.create_conversation()
        result = store.get_or_create(conv.id)
        assert result.id == conv.id
        assert store.count == 1

    def test_get_or_create_new(self):
        store = ConversationStore()
        result = store.get_or_create(None)
        assert result.id is not None
        assert store.count == 1

    def test_get_or_create_unknown_id(self):
        store = ConversationStore()
        result = store.get_or_create("unknown-id")
        assert result.id is not None
        assert store.count == 1
