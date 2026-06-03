"""Policy RAG Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class PolicyDocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=100)
    version: str = Field(default="1.0", max_length=20)


class PolicyDocumentResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    version: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class PolicyQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class PolicyChunk(BaseModel):
    document_id: int
    title: str
    content: str
    relevance_score: float


class PolicyQueryResponse(BaseModel):
    query: str
    results: list[PolicyChunk]
