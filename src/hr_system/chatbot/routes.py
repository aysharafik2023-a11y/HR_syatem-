"""Chatbot API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hr_system.chatbot.conversation import ConversationStore
from hr_system.chatbot.schemas import ChatRequest, ChatResponse
from hr_system.chatbot.service import ChatbotService
from hr_system.database import get_db
from hr_system.policy_rag.embeddings import SimpleEmbedder
from hr_system.policy_rag.service import PolicyRAGService
from hr_system.policy_rag.vector_store import VectorStore

router = APIRouter(prefix="/chat", tags=["chatbot"])

# Shared instances
_conversation_store = ConversationStore()
_vector_store = VectorStore()
_embedder = SimpleEmbedder()


def get_chatbot_service() -> ChatbotService:
    return ChatbotService(_conversation_store)


def get_rag_service(db: Session = Depends(get_db)) -> PolicyRAGService:
    return PolicyRAGService(db, _vector_store, _embedder)


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    chatbot: ChatbotService = Depends(get_chatbot_service),
    rag_service: PolicyRAGService = Depends(get_rag_service),
):
    """Send a message to the HR chatbot."""
    rag_results = rag_service.query_policies(request.message, top_k=3)
    return chatbot.generate_response(
        user_message=request.message,
        rag_results=rag_results,
        conversation_id=request.conversation_id,
    )


@router.get("/{conversation_id}/history")
def get_history(
    conversation_id: str, chatbot: ChatbotService = Depends(get_chatbot_service)
):
    """Get conversation history."""
    history = chatbot.get_conversation_history(conversation_id)
    if not history:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "messages": history}
