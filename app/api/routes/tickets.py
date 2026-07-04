"""Ticket management API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.audit import log_action
from app.middleware.auth import get_current_user
from app.models.ticket import TicketPriority, TicketStatus
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketListResponse, TicketResponse, TicketUpdate
from app.services.ai_client import get_ai_client
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        ai_client = get_ai_client()
    except Exception:
        ai_client = None

    service = TicketService(db, ai_client)
    ticket = service.create_ticket(ticket_data)
    log_action(db, current_user.id, "create", "ticket", ticket.id)
    return ticket


@router.get("", response_model=TicketListResponse)
def list_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: TicketStatus | None = Query(None, alias="status"),
    priority: TicketPriority | None = None,
    assigned_agent_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TicketService(db)
    tickets, total = service.get_tickets(
        page=page,
        page_size=page_size,
        status=status_filter,
        priority=priority,
        assigned_agent_id=assigned_agent_id,
    )
    return TicketListResponse(tickets=tickets, total=total, page=page, page_size=page_size)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TicketService(db)
    ticket = service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TicketService(db)
    ticket = service.update_ticket(ticket_id, update_data)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    log_action(db, current_user.id, "update", "ticket", ticket_id)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TicketService(db)
    if not service.delete_ticket(ticket_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    log_action(db, current_user.id, "delete", "ticket", ticket_id)


@router.get("/stats/summary")
def get_ticket_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TicketService(db)
    return service.get_ticket_stats()
