"""Escalation repository for database operations."""

from sqlalchemy.orm import Session

from app.models.escalation import Escalation, EscalationStatus


class EscalationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, escalation_id: int) -> Escalation | None:
        return self.db.query(Escalation).filter(Escalation.id == escalation_id).first()

    def get_by_ticket_id(self, ticket_id: int) -> list[Escalation]:
        return self.db.query(Escalation).filter(Escalation.ticket_id == ticket_id).all()

    def get_pending(self) -> list[Escalation]:
        return self.db.query(Escalation).filter(Escalation.status == EscalationStatus.PENDING).all()

    def create(self, escalation: Escalation) -> Escalation:
        self.db.add(escalation)
        self.db.commit()
        self.db.refresh(escalation)
        return escalation

    def update(self, escalation: Escalation) -> Escalation:
        self.db.commit()
        self.db.refresh(escalation)
        return escalation
