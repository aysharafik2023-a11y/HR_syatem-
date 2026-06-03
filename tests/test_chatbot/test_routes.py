"""Tests for chatbot API routes."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from hr_system.app import app
from hr_system.database import Base, get_db
from hr_system.policy_rag.models import PolicyDocument  # noqa: F401
from hr_system.recruitment.models import Application, Candidate, JobPosting  # noqa: F401


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestChatRoutes:
    def test_chat_endpoint(self, client):
        resp = client.post("/chat/", json={"message": "What is the leave policy?"})
        assert resp.status_code == 200
        data = resp.json()
        assert "conversation_id" in data
        assert "message" in data
        assert "sources" in data

    def test_chat_with_conversation_id(self, client):
        resp1 = client.post("/chat/", json={"message": "Hello"})
        conv_id = resp1.json()["conversation_id"]
        resp2 = client.post(
            "/chat/", json={"message": "Follow up", "conversation_id": conv_id}
        )
        assert resp2.status_code == 200
        assert resp2.json()["conversation_id"] == conv_id

    def test_chat_history_not_found(self, client):
        resp = client.get("/chat/nonexistent-id/history")
        assert resp.status_code == 404

    def test_chat_empty_message_rejected(self, client):
        resp = client.post("/chat/", json={"message": ""})
        assert resp.status_code == 422
