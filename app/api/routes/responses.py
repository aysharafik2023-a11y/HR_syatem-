"""AI Response API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.response import AIResponseCreate, ResponseResponse, ResponseUpdate
from app.services.ai_client import get_ai_client
from app.services.response_service import ResponseService

router = APIRouter(prefix="/responses", tags=["AI Responses"])


@router.post("/generate", response_model=ResponseResponse, status_code=status.HTTP_201_CREATED)
def generate_response(
    request: AIResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.repositories.ticket_repository import TicketRepository

    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.get_by_id(request.ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    try:
        ai_client = get_ai_client()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service unavailable",
        )

    service = ResponseService(ai_client, db)
    response = service.generate_response(ticket)
    return response


@router.get("/ticket/{ticket_id}", response_model=list[ResponseResponse])
def get_ticket_responses(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.repositories.response_repository import ResponseRepository

    repo = ResponseRepository(db)
    return repo.get_by_ticket_id(ticket_id)


@router.put("/{response_id}", response_model=ResponseResponse)
def update_response(
    response_id: int,
    update_data: ResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.ai_client import AIClient

    service = ResponseService(AIClient(), db)
    try:
        response = service.update_response(response_id, update_data.final_response, current_user.id)
        if update_data.is_sent:
            response = service.send_response(response_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{response_id}/send", response_model=ResponseResponse)
def send_response(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.ai_client import AIClient

    service = ResponseService(AIClient(), db)
    try:
        return service.send_response(response_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
