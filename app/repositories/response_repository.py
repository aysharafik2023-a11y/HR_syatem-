"""Response repository for database operations."""

from sqlalchemy.orm import Session

from app.models.response import Response


class ResponseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, response_id: int) -> Response | None:
        return self.db.query(Response).filter(Response.id == response_id).first()

    def get_by_ticket_id(self, ticket_id: int) -> list[Response]:
        return (
            self.db.query(Response)
            .filter(Response.ticket_id == ticket_id)
            .order_by(Response.created_at.desc())
            .all()
        )

    def create(self, response: Response) -> Response:
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response

    def update(self, response: Response) -> Response:
        self.db.commit()
        self.db.refresh(response)
        return response
