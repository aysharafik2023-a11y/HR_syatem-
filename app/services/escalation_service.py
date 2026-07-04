"""Escalation service for automatic ticket escalation."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.escalation import Escalation, EscalationReason, EscalationStatus
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.repositories.escalation_repository import EscalationRepository
from app.repositories.ticket_repository import TicketRepository

logger = get_logger(__name__)


class EscalationService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.ticket_repo = TicketRepository(db)
        self.escalation_repo = EscalationRepository(db)

    def evaluate_ticket(self, ticket: Ticket) -> Escalation | None:
        if ticket.priority == TicketPriority.CRITICAL:
            return self._create_escalation(
                ticket,
                EscalationReason.CRITICAL_PRIORITY,
                "Ticket has critical priority and requires immediate attention.",
            )

        if ticket.sentiment_score is not None and ticket.sentiment_score < -0.5:
            return self._create_escalation(
                ticket,
                EscalationReason.NEGATIVE_SENTIMENT,
                f"Customer sentiment is very negative (score: {ticket.sentiment_score:.2f}).",
            )

        if self._is_sla_breached(ticket):
            return self._create_escalation(
                ticket,
                EscalationReason.SLA_BREACH,
                "Ticket has exceeded the SLA response time.",
            )

        return None

    def _is_sla_breached(self, ticket: Ticket) -> bool:
        if ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            return False

        hours_open = (datetime.now(UTC) - ticket.created_at).total_seconds() / 3600

        sla_map = {
            TicketPriority.LOW: self.settings.sla_low_priority_hours,
            TicketPriority.MEDIUM: self.settings.sla_medium_priority_hours,
            TicketPriority.HIGH: self.settings.sla_high_priority_hours,
            TicketPriority.CRITICAL: self.settings.sla_critical_priority_hours,
        }

        priority = ticket.priority or TicketPriority.MEDIUM
        sla_hours = sla_map.get(priority, 24)

        return hours_open > sla_hours

    def _create_escalation(
        self,
        ticket: Ticket,
        reason: EscalationReason,
        description: str,
    ) -> Escalation:
        existing = self.escalation_repo.get_by_ticket_id(ticket.id)
        for esc in existing:
            if esc.reason == reason and esc.status == EscalationStatus.PENDING:
                return esc

        escalation = Escalation(
            ticket_id=ticket.id,
            reason=reason,
            description=description,
            status=EscalationStatus.PENDING,
        )

        ticket.status = TicketStatus.ESCALATED
        self.ticket_repo.update(ticket)

        saved = self.escalation_repo.create(escalation)
        logger.warning(
            "Ticket escalated",
            ticket_id=ticket.id,
            reason=reason.value,
            description=description,
        )

        return saved

    def acknowledge_escalation(self, escalation_id: int, manager_email: str) -> Escalation:
        escalation = self.escalation_repo.get_by_id(escalation_id)
        if not escalation:
            raise ValueError(f"Escalation {escalation_id} not found")

        escalation.status = EscalationStatus.ACKNOWLEDGED
        escalation.escalated_to = manager_email
        return self.escalation_repo.update(escalation)

    def resolve_escalation(self, escalation_id: int) -> Escalation:
        escalation = self.escalation_repo.get_by_id(escalation_id)
        if not escalation:
            raise ValueError(f"Escalation {escalation_id} not found")

        escalation.status = EscalationStatus.RESOLVED
        escalation.resolved_at = datetime.now(UTC)
        return self.escalation_repo.update(escalation)

    def check_all_open_tickets(self) -> list[Escalation]:
        escalations = []
        for priority in TicketPriority:
            sla_map = {
                TicketPriority.LOW: self.settings.sla_low_priority_hours,
                TicketPriority.MEDIUM: self.settings.sla_medium_priority_hours,
                TicketPriority.HIGH: self.settings.sla_high_priority_hours,
                TicketPriority.CRITICAL: self.settings.sla_critical_priority_hours,
            }
            hours = sla_map[priority]
            tickets = self.ticket_repo.get_unresponded_tickets(hours)
            for ticket in tickets:
                if ticket.priority == priority:
                    result = self.evaluate_ticket(ticket)
                    if result:
                        escalations.append(result)
        return escalations
