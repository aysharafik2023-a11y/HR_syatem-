"""Integration tests for ticket workflow."""

from unittest.mock import MagicMock, patch

import pytest
from app.models.ticket import TicketCategory, TicketChannel, TicketPriority, TicketStatus
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.services.ticket_service import TicketService


@pytest.fixture
def ticket_service(db_session):
    return TicketService(db_session)


def test_create_ticket_without_ai(ticket_service):
    ticket_data = TicketCreate(
        customer_name="Alice Johnson",
        customer_email="alice@example.com",
        subject="Payment failed",
        description="My credit card payment failed when trying to upgrade my plan.",
        channel=TicketChannel.WEB_PORTAL,
    )

    ticket = ticket_service.create_ticket(ticket_data)

    assert ticket.id is not None
    assert ticket.customer_name == "Alice Johnson"
    assert ticket.customer_email == "alice@example.com"
    assert ticket.subject == "Payment failed"
    assert ticket.status == TicketStatus.OPEN


def test_get_ticket(ticket_service):
    ticket_data = TicketCreate(
        customer_name="Bob Smith",
        customer_email="bob@example.com",
        subject="Feature suggestion",
        description="Can you add dark mode?",
    )
    created = ticket_service.create_ticket(ticket_data)

    retrieved = ticket_service.get_ticket(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.subject == "Feature suggestion"


def test_update_ticket(ticket_service):
    ticket_data = TicketCreate(
        customer_name="Carol White",
        customer_email="carol@example.com",
        subject="Bug in dashboard",
        description="Charts not loading.",
    )
    created = ticket_service.create_ticket(ticket_data)

    update_data = TicketUpdate(
        status=TicketStatus.IN_PROGRESS,
        priority=TicketPriority.HIGH,
        category=TicketCategory.BUG_REPORT,
    )
    updated = ticket_service.update_ticket(created.id, update_data)

    assert updated is not None
    assert updated.status == TicketStatus.IN_PROGRESS
    assert updated.priority == TicketPriority.HIGH
    assert updated.category == TicketCategory.BUG_REPORT


def test_delete_ticket(ticket_service):
    ticket_data = TicketCreate(
        customer_name="Dave Brown",
        customer_email="dave@example.com",
        subject="Test ticket",
        description="To be deleted.",
    )
    created = ticket_service.create_ticket(ticket_data)

    result = ticket_service.delete_ticket(created.id)
    assert result is True

    assert ticket_service.get_ticket(created.id) is None


def test_list_tickets_with_pagination(ticket_service):
    for i in range(5):
        ticket_data = TicketCreate(
            customer_name=f"User {i}",
            customer_email=f"user{i}@example.com",
            subject=f"Ticket {i}",
            description=f"Description {i}",
        )
        ticket_service.create_ticket(ticket_data)

    tickets, total = ticket_service.get_tickets(page=1, page_size=3)
    assert len(tickets) == 3
    assert total == 5

    tickets, total = ticket_service.get_tickets(page=2, page_size=3)
    assert len(tickets) == 2


def test_list_tickets_with_status_filter(ticket_service):
    for i in range(3):
        ticket_data = TicketCreate(
            customer_name=f"User {i}",
            customer_email=f"user{i}@example.com",
            subject=f"Ticket {i}",
            description=f"Description {i}",
        )
        ticket = ticket_service.create_ticket(ticket_data)
        if i == 0:
            ticket_service.update_ticket(ticket.id, TicketUpdate(status=TicketStatus.RESOLVED))

    tickets, total = ticket_service.get_tickets(status=TicketStatus.OPEN)
    assert total == 2


@patch("app.services.ai_client.AIClient")
def test_create_ticket_with_ai_classification(mock_ai_class, db_session):
    mock_ai = MagicMock()
    mock_ai.chat_completion.side_effect = [
        {
            "category": "billing",
            "priority": "high",
            "confidence": 0.95,
            "reasoning": "Payment related issue",
        },
        {
            "score": -0.3,
            "tone": "neutral",
            "urgency": "medium",
        },
    ]

    service = TicketService(db_session, mock_ai)
    ticket_data = TicketCreate(
        customer_name="Eve Davis",
        customer_email="eve@example.com",
        subject="Overcharged on my bill",
        description="I was charged twice for my subscription this month.",
    )

    ticket = service.create_ticket(ticket_data)

    assert ticket.category == TicketCategory.BILLING
    assert ticket.priority == TicketPriority.HIGH
    assert ticket.ai_confidence == 0.95
    assert ticket.sentiment_score == -0.3
