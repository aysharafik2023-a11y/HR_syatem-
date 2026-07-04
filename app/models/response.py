"""Response model."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"), nullable=False)
    agent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    ai_generated_response: Mapped[str] = mapped_column(Text, nullable=False)
    final_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    troubleshooting_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    knowledge_sources: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    ticket: Mapped["Ticket"] = relationship(back_populates="responses")  # noqa: F821
    agent: Mapped["User | None"] = relationship(back_populates="responses")  # noqa: F821
