"""Escalation model."""

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EscalationReason(str, enum.Enum):
    CRITICAL_PRIORITY = "critical_priority"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    SLA_BREACH = "sla_breach"
    MANUAL = "manual"


class EscalationStatus(str, enum.Enum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Escalation(Base):
    __tablename__ = "escalations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"), nullable=False)
    reason: Mapped[EscalationReason] = mapped_column(Enum(EscalationReason), nullable=False)
    status: Mapped[EscalationStatus] = mapped_column(
        Enum(EscalationStatus), default=EscalationStatus.PENDING
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    escalated_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notification_sent: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    ticket: Mapped["Ticket"] = relationship(back_populates="escalations")  # noqa: F821
