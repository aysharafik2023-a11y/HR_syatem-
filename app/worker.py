"""Celery worker configuration for background tasks."""

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "support_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "check-sla-breaches": {
        "task": "app.tasks.check_sla_breaches",
        "schedule": crontab(minute="*/15"),
    },
}


@celery_app.task(name="app.tasks.classify_ticket")
def classify_ticket_task(ticket_id: int) -> dict:
    from app.database.session import SessionLocal
    from app.repositories.ticket_repository import TicketRepository
    from app.services.ai_client import AIClient
    from app.services.classification_service import ClassificationService

    db = SessionLocal()
    try:
        repo = TicketRepository(db)
        ticket = repo.get_by_id(ticket_id)
        if not ticket:
            return {"error": "Ticket not found"}

        ai_client = AIClient()
        service = ClassificationService(ai_client)
        result = service.classify_ticket(ticket)

        ticket.category = result["category"]
        ticket.priority = result["priority"]
        ticket.ai_confidence = result["confidence"]
        repo.update(ticket)

        return {"ticket_id": ticket_id, "classification": result}
    finally:
        db.close()


@celery_app.task(name="app.tasks.check_sla_breaches")
def check_sla_breaches_task() -> dict:
    from app.database.session import SessionLocal
    from app.services.escalation_service import EscalationService

    db = SessionLocal()
    try:
        service = EscalationService(db)
        escalations = service.check_all_open_tickets()
        return {"escalated_count": len(escalations)}
    finally:
        db.close()
