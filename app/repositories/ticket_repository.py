"""Ticket repository for database operations."""

from datetime import UTC

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketPriority, TicketStatus


class TicketRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return self.db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        assigned_agent_id: int | None = None,
    ) -> tuple[list[Ticket], int]:
        query = self.db.query(Ticket)

        if status:
            query = query.filter(Ticket.status == status)
        if priority:
            query = query.filter(Ticket.priority == priority)
        if assigned_agent_id:
            query = query.filter(Ticket.assigned_agent_id == assigned_agent_id)

        total = query.count()
        tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
        return tickets, total

    def create(self, ticket: Ticket) -> Ticket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def update(self, ticket: Ticket) -> Ticket:
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def delete(self, ticket: Ticket) -> None:
        self.db.delete(ticket)
        self.db.commit()

    def count_by_status(self) -> dict[str, int]:
        results = self.db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
        return {status.value: count for status, count in results}

    def get_unresponded_tickets(self, hours: int) -> list[Ticket]:
        from datetime import datetime, timedelta

        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        return (
            self.db.query(Ticket)
            .filter(
                Ticket.status == TicketStatus.OPEN,
                Ticket.created_at <= cutoff,
            )
            .all()
        )
