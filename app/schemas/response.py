"""Response schemas."""

from datetime import datetime

from pydantic import BaseModel


class AIResponseCreate(BaseModel):
    ticket_id: int


class ResponseUpdate(BaseModel):
    final_response: str
    is_sent: bool = False


class ResponseResponse(BaseModel):
    id: int
    ticket_id: int
    agent_id: int | None = None
    ai_generated_response: str
    final_response: str | None = None
    confidence_score: float
    is_sent: bool
    troubleshooting_steps: str | None = None
    knowledge_sources: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
