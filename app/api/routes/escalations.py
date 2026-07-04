"""Escalation API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.schemas.escalation import EscalationResponse
from app.services.escalation_service import EscalationService

router = APIRouter(prefix="/escalations", tags=["Escalations"])


@router.get("", response_model=list[EscalationResponse])
def get_pending_escalations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = EscalationService(db)
    return service.escalation_repo.get_pending()


@router.get("/ticket/{ticket_id}", response_model=list[EscalationResponse])
def get_ticket_escalations(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EscalationService(db)
    return service.escalation_repo.get_by_ticket_id(ticket_id)


@router.post("/{escalation_id}/acknowledge", response_model=EscalationResponse)
def acknowledge_escalation(
    escalation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = EscalationService(db)
    try:
        return service.acknowledge_escalation(escalation_id, current_user.email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{escalation_id}/resolve", response_model=EscalationResponse)
def resolve_escalation(
    escalation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = EscalationService(db)
    try:
        return service.resolve_escalation(escalation_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/check-sla")
def check_sla_breaches(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
):
    service = EscalationService(db)
    escalations = service.check_all_open_tickets()
    return {"escalated_count": len(escalations), "escalations": escalations}
