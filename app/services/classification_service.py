"""AI ticket classification service."""

from app.core.logging import get_logger
from app.models.ticket import Ticket, TicketCategory, TicketPriority
from app.prompts.classification import (
    SENTIMENT_ANALYSIS_SYSTEM,
    SENTIMENT_ANALYSIS_USER,
    TICKET_CLASSIFICATION_SYSTEM,
    TICKET_CLASSIFICATION_USER,
)
from app.services.ai_client import AIClient

logger = get_logger(__name__)


class ClassificationService:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    def classify_ticket(self, ticket: Ticket) -> dict:
        user_prompt = TICKET_CLASSIFICATION_USER.format(
            subject=ticket.subject,
            description=ticket.description,
            channel=ticket.channel.value if ticket.channel else "web_portal",
            customer_name=ticket.customer_name,
        )

        result = self.ai_client.chat_completion(TICKET_CLASSIFICATION_SYSTEM, user_prompt)

        category = self._parse_category(result.get("category", "general"))
        priority = self._parse_priority(result.get("priority", "medium"))
        confidence = float(result.get("confidence", 0.5))

        logger.info(
            "Ticket classified",
            ticket_id=ticket.id,
            category=category.value,
            priority=priority.value,
            confidence=confidence,
        )

        return {
            "category": category,
            "priority": priority,
            "confidence": confidence,
            "reasoning": result.get("reasoning", ""),
        }

    def analyze_sentiment(self, ticket: Ticket) -> dict:
        user_prompt = SENTIMENT_ANALYSIS_USER.format(
            subject=ticket.subject,
            description=ticket.description,
        )

        result = self.ai_client.chat_completion(SENTIMENT_ANALYSIS_SYSTEM, user_prompt)

        score = float(result.get("score", 0.0))
        score = max(-1.0, min(1.0, score))

        logger.info(
            "Sentiment analyzed",
            ticket_id=ticket.id,
            score=score,
            tone=result.get("tone", "neutral"),
        )

        return {
            "score": score,
            "tone": result.get("tone", "neutral"),
            "urgency": result.get("urgency", "medium"),
        }

    @staticmethod
    def _parse_category(category_str: str) -> TicketCategory:
        try:
            return TicketCategory(category_str.lower().strip())
        except ValueError:
            return TicketCategory.GENERAL

    @staticmethod
    def _parse_priority(priority_str: str) -> TicketPriority:
        try:
            return TicketPriority(priority_str.lower().strip())
        except ValueError:
            return TicketPriority.MEDIUM
