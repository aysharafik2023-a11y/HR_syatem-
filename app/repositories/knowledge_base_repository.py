"""Knowledge base repository for database operations."""

from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeBaseEntry


class KnowledgeBaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, entry_id: int) -> KnowledgeBaseEntry | None:
        return self.db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.id == entry_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[KnowledgeBaseEntry]:
        return self.db.query(KnowledgeBaseEntry).offset(skip).limit(limit).all()

    def get_by_category(self, category: str) -> list[KnowledgeBaseEntry]:
        return (
            self.db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.category == category).all()
        )

    def search(self, query: str) -> list[KnowledgeBaseEntry]:
        return (
            self.db.query(KnowledgeBaseEntry)
            .filter(
                KnowledgeBaseEntry.title.ilike(f"%{query}%")
                | KnowledgeBaseEntry.content.ilike(f"%{query}%")
                | KnowledgeBaseEntry.tags.ilike(f"%{query}%")
            )
            .all()
        )

    def create(self, entry: KnowledgeBaseEntry) -> KnowledgeBaseEntry:
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def update(self, entry: KnowledgeBaseEntry) -> KnowledgeBaseEntry:
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete(self, entry: KnowledgeBaseEntry) -> None:
        self.db.delete(entry)
        self.db.commit()
