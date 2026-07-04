"""Ticket service for business logic."""

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.services.ai_client import AIClient
from app.services.classification_service import ClassificationService
from app.services.escalation_service import EscalationService

logger = get_logger(__name__)


class TicketService:
    def __init__(self, db: Session, ai_client: AIClient | None = None):
        self.db = db
        self.ticket_repo = TicketRepository(db)
        self.ai_client = ai_client
        if ai_client:
            self.classification_service = ClassificationService(ai_client)
            self.escalation_service = EscalationService(db)
        else:
            self.classification_service = None
            self.escalation_service = None

    def create_ticket(self, ticket_data: TicketCreate) -> Ticket:
        ticket = Ticket(
            customer_name=ticket_data.customer_name,
            customer_email=ticket_data.customer_email,
            subject=ticket_data.subject,
            description=ticket_data.description,
            channel=ticket_data.channel,
        )

        ticket = self.ticket_repo.create(ticket)

        if self.classification_service:
            try:
                classification = self.classification_service.classify_ticket(ticket)
                ticket.category = classification["category"]
                ticket.priority = classification["priority"]
                ticket.ai_confidence = classification["confidence"]

                sentiment = self.classification_service.analyze_sentiment(ticket)
                ticket.sentiment_score = sentiment["score"]

                ticket = self.ticket_repo.update(ticket)

                if self.escalation_service:
                    self.escalation_service.evaluate_ticket(ticket)

            except Exception as e:
                logger.error("AI classification failed", ticket_id=ticket.id, error=str(e))

        logger.info("Ticket created", ticket_id=ticket.id)
        return ticket

    def get_ticket(self, ticket_id: int) -> Ticket | None:
        return self.ticket_repo.get_by_id(ticket_id)

    def get_tickets(
        self,
        page: int = 1,
        page_size: int = 20,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        assigned_agent_id: int | None = None,
    ) -> tuple[list[Ticket], int]:
        skip = (page - 1) * page_size
        return self.ticket_repo.get_all(
            skip=skip,
            limit=page_size,
            status=status,
            priority=priority,
            assigned_agent_id=assigned_agent_id,
        )

    def update_ticket(self, ticket_id: int, update_data: TicketUpdate) -> Ticket | None:
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(ticket, field, value)

        ticket = self.ticket_repo.update(ticket)
        logger.info("Ticket updated", ticket_id=ticket_id, fields=list(update_dict.keys()))
        return ticket

    def delete_ticket(self, ticket_id: int) -> bool:
        ticket = self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            return False
        self.ticket_repo.delete(ticket)
        logger.info("Ticket deleted", ticket_id=ticket_id)
        return True

    def get_ticket_stats(self) -> dict:
        return self.ticket_repo.count_by_status()
