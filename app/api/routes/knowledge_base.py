"""Knowledge base API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.knowledge_base import KnowledgeBaseEntry
from app.models.user import User, UserRole
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseResponse

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])


@router.post("", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry_data: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    repo = KnowledgeBaseRepository(db)
    entry = KnowledgeBaseEntry(
        title=entry_data.title,
        content=entry_data.content,
        category=entry_data.category,
        tags=entry_data.tags,
    )
    return repo.create(entry)


@router.get("", response_model=list[KnowledgeBaseResponse])
def list_entries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = KnowledgeBaseRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/search", response_model=list[KnowledgeBaseResponse])
def search_entries(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = KnowledgeBaseRepository(db)
    return repo.search(q)


@router.get("/{entry_id}", response_model=KnowledgeBaseResponse)
def get_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = KnowledgeBaseRepository(db)
    entry = repo.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    repo = KnowledgeBaseRepository(db)
    entry = repo.get_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    repo.delete(entry)
