"""AI response generation service with RAG."""

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.response import Response
from app.models.ticket import Ticket
from app.prompts.response_generation import RESPONSE_GENERATION_SYSTEM, RESPONSE_GENERATION_USER
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.repositories.response_repository import ResponseRepository
from app.services.ai_client import AIClient

logger = get_logger(__name__)


class ResponseService:
    def __init__(self, ai_client: AIClient, db: Session):
        self.ai_client = ai_client
        self.db = db
        self.knowledge_repo = KnowledgeBaseRepository(db)
        self.response_repo = ResponseRepository(db)

    def generate_response(self, ticket: Ticket) -> Response:
        knowledge_context = self._get_relevant_knowledge(ticket)

        user_prompt = RESPONSE_GENERATION_USER.format(
            subject=ticket.subject,
            description=ticket.description,
            category=ticket.category.value if ticket.category else "general",
            priority=ticket.priority.value if ticket.priority else "medium",
            customer_name=ticket.customer_name,
            knowledge_context=knowledge_context,
        )

        result = self.ai_client.chat_completion(RESPONSE_GENERATION_SYSTEM, user_prompt)

        response = Response(
            ticket_id=ticket.id,
            ai_generated_response=result.get("response", ""),
            confidence_score=float(result.get("confidence", 0.5)),
            troubleshooting_steps=result.get("troubleshooting_steps"),
            knowledge_sources=knowledge_context[:1000] if knowledge_context else None,
        )

        saved_response = self.response_repo.create(response)

        logger.info(
            "AI response generated",
            ticket_id=ticket.id,
            response_id=saved_response.id,
            confidence=saved_response.confidence_score,
        )

        return saved_response

    def _get_relevant_knowledge(self, ticket: Ticket) -> str:
        search_terms = []
        if ticket.subject:
            search_terms.append(ticket.subject)
        if ticket.category:
            search_terms.append(ticket.category.value)

        all_results = []
        for term in search_terms:
            results = self.knowledge_repo.search(term)
            all_results.extend(results)

        seen_ids: set[int] = set()
        unique_results = []
        for entry in all_results:
            if entry.id not in seen_ids:
                seen_ids.add(entry.id)
                unique_results.append(entry)

        if not unique_results:
            return "No relevant knowledge base articles found."

        context_parts = []
        for entry in unique_results[:5]:
            context_parts.append(f"Title: {entry.title}\nContent: {entry.content[:500]}")

        return "\n\n---\n\n".join(context_parts)

    def update_response(self, response_id: int, final_response: str, agent_id: int) -> Response:
        response = self.response_repo.get_by_id(response_id)
        if not response:
            raise ValueError(f"Response {response_id} not found")

        response.final_response = final_response
        response.agent_id = agent_id
        return self.response_repo.update(response)

    def send_response(self, response_id: int) -> Response:
        response = self.response_repo.get_by_id(response_id)
        if not response:
            raise ValueError(f"Response {response_id} not found")

        content = response.final_response or response.ai_generated_response
        logger.info(
            "Sending response to customer", response_id=response_id, content_len=len(content)
        )

        response.is_sent = True
        return self.response_repo.update(response)

    def get_ticket_responses(self, ticket_id: int) -> list[Response]:
        return self.response_repo.get_by_ticket_id(ticket_id)
