"""Ticket schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.ticket import TicketCategory, TicketChannel, TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    subject: str
    description: str
    channel: TicketChannel = TicketChannel.WEB_PORTAL


class TicketUpdate(BaseModel):
    subject: str | None = None
    description: str | None = None
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    assigned_agent_id: int | None = None


class TicketResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    subject: str
    description: str
    channel: TicketChannel
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    ai_confidence: float | None = None
    status: TicketStatus
    assigned_agent_id: int | None = None
    sentiment_score: float | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    tickets: list[TicketResponse]
    total: int
    page: int
    page_size: int
