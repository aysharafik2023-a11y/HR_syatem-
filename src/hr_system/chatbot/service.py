"""Chatbot service layer integrating conversation management with RAG."""

from datetime import datetime

from hr_system.chatbot.conversation import ConversationStore
from hr_system.chatbot.schemas import ChatResponse
from hr_system.policy_rag.schemas import PolicyQueryResponse


class ChatbotService:
    """Chatbot that answers HR policy questions using RAG context."""

    def __init__(self, conversation_store: ConversationStore):
        self.conversation_store = conversation_store

    def generate_response(
        self,
        user_message: str,
        rag_results: PolicyQueryResponse | None,
        conversation_id: str | None = None,
    ) -> ChatResponse:
        """Generate a chatbot response using RAG context."""
        conversation = self.conversation_store.get_or_create(conversation_id)
        conversation.add_message("user", user_message)

        # Build response from RAG results
        response_text, sources = self._build_response(user_message, rag_results)
        conversation.add_message("assistant", response_text)

        return ChatResponse(
            conversation_id=conversation.id,
            message=response_text,
            sources=sources,
            timestamp=datetime.utcnow(),
        )

    def _build_response(
        self, query: str, rag_results: PolicyQueryResponse | None
    ) -> tuple[str, list[str]]:
        """Build a response from RAG results.

        In production, this would call an LLM with the context.
        For now, it constructs a structured response from retrieved chunks.
        """
        if not rag_results or not rag_results.results:
            return (
                "I couldn't find any relevant policy information for your question. "
                "Please try rephrasing or contact HR directly.",
                [],
            )

        sources: list[str] = []
        context_parts: list[str] = []

        for chunk in rag_results.results:
            sources.append(f"{chunk.title} (relevance: {chunk.relevance_score:.2f})")
            context_parts.append(chunk.content)

        context = "\n\n".join(context_parts)
        response = (
            f"Based on our company policies, here's what I found regarding your question:\n\n"
            f"{context}\n\n"
            f"This information was sourced from: {', '.join(sources)}."
        )

        return response, sources

    def get_conversation_history(self, conversation_id: str) -> list[dict]:
        """Get conversation history as a list of dicts."""
        conversation = self.conversation_store.get_conversation(conversation_id)
        if not conversation:
            return []
        return [
            {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat()}
            for msg in conversation.get_history()
        ]
