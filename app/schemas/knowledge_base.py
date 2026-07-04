"""Knowledge base schemas."""

from datetime import datetime

from pydantic import BaseModel


class KnowledgeBaseCreate(BaseModel):
    title: str
    content: str
    category: str
    tags: str | None = None


class KnowledgeBaseResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
