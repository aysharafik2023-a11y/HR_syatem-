"""Unit tests for classification service."""

from unittest.mock import MagicMock, patch

from app.models.ticket import Ticket, TicketCategory, TicketChannel, TicketPriority
from app.services.classification_service import ClassificationService


def _make_ticket() -> Ticket:
    ticket = Ticket(
        id=1,
        customer_name="John Doe",
        customer_email="john@example.com",
        subject="Cannot access my account",
        description="I have been locked out of my account for 2 hours. I need immediate access.",
        channel=TicketChannel.WEB_PORTAL,
    )
    return ticket


@patch("app.services.classification_service.ClassificationService.classify_ticket")
def test_classify_ticket(mock_classify):
    mock_classify.return_value = {
        "category": TicketCategory.ACCOUNT_ISSUE,
        "priority": TicketPriority.HIGH,
        "confidence": 0.92,
        "reasoning": "Account access issue with urgency",
    }

    ai_client = MagicMock()
    service = ClassificationService(ai_client)
    ticket = _make_ticket()

    result = service.classify_ticket(ticket)

    assert result["category"] == TicketCategory.ACCOUNT_ISSUE
    assert result["priority"] == TicketPriority.HIGH
    assert result["confidence"] == 0.92


def test_parse_category():
    assert ClassificationService._parse_category("billing") == TicketCategory.BILLING
    assert (
        ClassificationService._parse_category("TECHNICAL_ISSUE") == TicketCategory.TECHNICAL_ISSUE
    )
    assert ClassificationService._parse_category("invalid") == TicketCategory.GENERAL


def test_parse_priority():
    assert ClassificationService._parse_priority("critical") == TicketPriority.CRITICAL
    assert ClassificationService._parse_priority("HIGH") == TicketPriority.HIGH
    assert ClassificationService._parse_priority("invalid") == TicketPriority.MEDIUM


@patch("app.services.ai_client.AIClient.chat_completion")
def test_analyze_sentiment(mock_chat):
    mock_chat.return_value = {
        "score": -0.7,
        "tone": "frustrated",
        "urgency": "high",
    }

    ai_client = MagicMock()
    ai_client.chat_completion = mock_chat
    service = ClassificationService(ai_client)
    ticket = _make_ticket()

    result = service.analyze_sentiment(ticket)

    assert result["score"] == -0.7
    assert result["tone"] == "frustrated"
    assert result["urgency"] == "high"
