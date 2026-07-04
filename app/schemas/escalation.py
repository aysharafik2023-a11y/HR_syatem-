"""Escalation schemas."""

from datetime import datetime

from pydantic import BaseModel

from app.models.escalation import EscalationReason, EscalationStatus


class EscalationCreate(BaseModel):
    ticket_id: int
    reason: EscalationReason
    description: str


class EscalationResponse(BaseModel):
    id: int
    ticket_id: int
    reason: EscalationReason
    status: EscalationStatus
    description: str
    escalated_to: str | None = None
    notification_sent: bool
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = {"from_attributes": True}
