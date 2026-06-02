"""Policy RAG API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hr_system.database import get_db
from hr_system.policy_rag.embeddings import SimpleEmbedder
from hr_system.policy_rag.schemas import (
    PolicyDocumentCreate,
    PolicyDocumentResponse,
    PolicyQueryRequest,
    PolicyQueryResponse,
)
from hr_system.policy_rag.service import PolicyRAGService
from hr_system.policy_rag.vector_store import VectorStore

router = APIRouter(prefix="/policies", tags=["policies"])

# Shared instances (in production, use dependency injection with lifespan)
_vector_store = VectorStore()
_embedder = SimpleEmbedder()


def get_service(db: Session = Depends(get_db)) -> PolicyRAGService:
    return PolicyRAGService(db, _vector_store, _embedder)


@router.post("/documents", response_model=PolicyDocumentResponse, status_code=201)
def upload_policy(
    data: PolicyDocumentCreate, service: PolicyRAGService = Depends(get_service)
):
    return service.ingest_document(data)


@router.get("/documents", response_model=list[PolicyDocumentResponse])
def list_policies(
    category: str | None = None, service: PolicyRAGService = Depends(get_service)
):
    return service.list_documents(category)


@router.get("/documents/{doc_id}", response_model=PolicyDocumentResponse)
def get_policy(doc_id: int, service: PolicyRAGService = Depends(get_service)):
    doc = service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Policy document not found")
    return doc


@router.delete("/documents/{doc_id}", status_code=204)
def delete_policy(doc_id: int, service: PolicyRAGService = Depends(get_service)):
    if not service.delete_document(doc_id):
        raise HTTPException(status_code=404, detail="Policy document not found")


@router.post("/query", response_model=PolicyQueryResponse)
def query_policies(
    request: PolicyQueryRequest, service: PolicyRAGService = Depends(get_service)
):
    return service.query_policies(request.query, top_k=request.top_k)
