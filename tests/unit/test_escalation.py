"""Unit tests for escalation service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from app.models.escalation import Escalation, EscalationReason, EscalationStatus
from app.models.ticket import Ticket, TicketChannel, TicketPriority, TicketStatus
from app.services.escalation_service import EscalationService


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def escalation_service(mock_db):
    with (
        patch("app.services.escalation_service.TicketRepository") as mock_ticket_repo,
        patch("app.services.escalation_service.EscalationRepository") as mock_esc_repo,
    ):
        mock_ticket_repo_instance = MagicMock()
        mock_esc_repo_instance = MagicMock()
        mock_ticket_repo.return_value = mock_ticket_repo_instance
        mock_esc_repo.return_value = mock_esc_repo_instance
        mock_esc_repo_instance.get_by_ticket_id.return_value = []

        service = EscalationService(mock_db)
        service.ticket_repo = mock_ticket_repo_instance
        service.escalation_repo = mock_esc_repo_instance
        yield service


def _make_ticket(
    priority=TicketPriority.MEDIUM,
    sentiment=-0.2,
    status=TicketStatus.OPEN,
    hours_ago=1,
) -> Ticket:
    ticket = Ticket(
        id=1,
        customer_name="Jane Smith",
        customer_email="jane@example.com",
        subject="Test ticket",
        description="Test description",
        channel=TicketChannel.EMAIL,
        priority=priority,
        status=status,
        sentiment_score=sentiment,
        created_at=datetime.now(UTC) - timedelta(hours=hours_ago),
    )
    return ticket


def test_escalate_critical_priority(escalation_service):
    ticket = _make_ticket(priority=TicketPriority.CRITICAL)
    escalation_service.escalation_repo.create.return_value = Escalation(
        id=1,
        ticket_id=1,
        reason=EscalationReason.CRITICAL_PRIORITY,
        description="Ticket has critical priority and requires immediate attention.",
        status=EscalationStatus.PENDING,
    )

    result = escalation_service.evaluate_ticket(ticket)

    assert result is not None
    assert result.reason == EscalationReason.CRITICAL_PRIORITY


def test_escalate_negative_sentiment(escalation_service):
    ticket = _make_ticket(sentiment=-0.8)
    escalation_service.escalation_repo.create.return_value = Escalation(
        id=2,
        ticket_id=1,
        reason=EscalationReason.NEGATIVE_SENTIMENT,
        description="Customer sentiment is very negative (score: -0.80).",
        status=EscalationStatus.PENDING,
    )

    result = escalation_service.evaluate_ticket(ticket)

    assert result is not None
    assert result.reason == EscalationReason.NEGATIVE_SENTIMENT


def test_no_escalation_normal_ticket(escalation_service):
    ticket = _make_ticket(priority=TicketPriority.LOW, sentiment=0.3, hours_ago=1)

    result = escalation_service.evaluate_ticket(ticket)

    assert result is None


def test_sla_breach_escalation(escalation_service):
    ticket = _make_ticket(priority=TicketPriority.HIGH, hours_ago=50)
    escalation_service.escalation_repo.create.return_value = Escalation(
        id=3,
        ticket_id=1,
        reason=EscalationReason.SLA_BREACH,
        description="Ticket has exceeded the SLA response time.",
        status=EscalationStatus.PENDING,
    )

    result = escalation_service.evaluate_ticket(ticket)

    assert result is not None
    assert result.reason == EscalationReason.SLA_BREACH
