"""Tests for chatbot service."""

import pytest

from hr_system.chatbot.conversation import ConversationStore
from hr_system.chatbot.service import ChatbotService
from hr_system.policy_rag.schemas import PolicyChunk, PolicyQueryResponse


@pytest.fixture
def chatbot_service():
    store = ConversationStore()
    return ChatbotService(store)


class TestChatbotService:
    def test_generate_response_with_rag_results(self, chatbot_service):
        rag_results = PolicyQueryResponse(
            query="leave policy",
            results=[
                PolicyChunk(
                    document_id=1,
                    title="Leave Policy",
                    content="Employees get 20 days annual leave.",
                    relevance_score=0.92,
                ),
            ],
        )
        response = chatbot_service.generate_response(
            user_message="What's the leave policy?",
            rag_results=rag_results,
        )
        assert response.conversation_id is not None
        assert "20 days" in response.message
        assert len(response.sources) == 1
        assert "Leave Policy" in response.sources[0]

    def test_generate_response_no_results(self, chatbot_service):
        rag_results = PolicyQueryResponse(query="xyz", results=[])
        response = chatbot_service.generate_response(
            user_message="Something unknown",
            rag_results=rag_results,
        )
        assert "couldn't find" in response.message
        assert response.sources == []

    def test_generate_response_none_rag(self, chatbot_service):
        response = chatbot_service.generate_response(
            user_message="Hello", rag_results=None
        )
        assert "couldn't find" in response.message

    def test_conversation_continuity(self, chatbot_service):
        rag = PolicyQueryResponse(
            query="q",
            results=[
                PolicyChunk(
                    document_id=1, title="T", content="Content", relevance_score=0.8
                )
            ],
        )
        resp1 = chatbot_service.generate_response("First message", rag)
        resp2 = chatbot_service.generate_response(
            "Second message", rag, conversation_id=resp1.conversation_id
        )
        assert resp2.conversation_id == resp1.conversation_id

    def test_get_conversation_history(self, chatbot_service):
        rag = PolicyQueryResponse(query="q", results=[])
        resp = chatbot_service.generate_response("Hello", rag)
        history = chatbot_service.get_conversation_history(resp.conversation_id)
        assert len(history) == 2  # user + assistant
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_get_conversation_history_not_found(self, chatbot_service):
        history = chatbot_service.get_conversation_history("nonexistent")
        assert history == []

    def test_multiple_rag_sources(self, chatbot_service):
        rag_results = PolicyQueryResponse(
            query="benefits",
            results=[
                PolicyChunk(
                    document_id=1,
                    title="Health Benefits",
                    content="Full medical coverage.",
                    relevance_score=0.95,
                ),
                PolicyChunk(
                    document_id=2,
                    title="Retirement Plan",
                    content="401k matching up to 6%.",
                    relevance_score=0.85,
                ),
            ],
        )
        response = chatbot_service.generate_response("Tell me about benefits", rag_results)
        assert len(response.sources) == 2
        assert "Health Benefits" in response.sources[0]
        assert "Retirement Plan" in response.sources[1]
