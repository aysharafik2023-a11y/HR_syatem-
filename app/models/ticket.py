"""Ticket model."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TicketCategory(StrEnum):
    BILLING = "billing"
    TECHNICAL_ISSUE = "technical_issue"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    ACCOUNT_ISSUE = "account_issue"
    GENERAL = "general"


class TicketPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_ON_CUSTOMER = "waiting_on_customer"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketChannel(StrEnum):
    WEB_PORTAL = "web_portal"
    EMAIL = "email"
    MOBILE_APP = "mobile_app"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[TicketChannel] = mapped_column(
        Enum(TicketChannel), default=TicketChannel.WEB_PORTAL
    )

    # AI-classified fields
    category: Mapped[TicketCategory | None] = mapped_column(Enum(TicketCategory), nullable=True)
    priority: Mapped[TicketPriority | None] = mapped_column(Enum(TicketPriority), nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus), default=TicketStatus.OPEN, index=True
    )
    assigned_agent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Sentiment
    sentiment_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    assigned_agent: Mapped["User | None"] = relationship(  # noqa: F821
        back_populates="assigned_tickets", foreign_keys=[assigned_agent_id]
    )
    responses: Mapped[list["Response"]] = relationship(  # noqa: F821
        back_populates="ticket", cascade="all, delete-orphan"
    )
    escalations: Mapped[list["Escalation"]] = relationship(  # noqa: F821
        back_populates="ticket", cascade="all, delete-orphan"
    )
