"""Tests for policy RAG API routes."""

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


class TestPolicyRoutes:
    def test_upload_policy(self, client):
        resp = client.post(
            "/policies/documents",
            json={
                "title": "Code of Conduct",
                "content": "All employees must treat each other with respect.",
                "category": "HR",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["title"] == "Code of Conduct"

    def test_list_policies(self, client):
        client.post(
            "/policies/documents",
            json={
                "title": "Policy A",
                "content": "Content A",
                "category": "General",
            },
        )
        resp = client.get("/policies/documents")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_policy(self, client):
        create_resp = client.post(
            "/policies/documents",
            json={
                "title": "Safety Policy",
                "content": "Wear helmets on site.",
                "category": "Safety",
            },
        )
        doc_id = create_resp.json()["id"]
        resp = client.get(f"/policies/documents/{doc_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Safety Policy"

    def test_get_policy_not_found(self, client):
        resp = client.get("/policies/documents/9999")
        assert resp.status_code == 404

    def test_delete_policy(self, client):
        create_resp = client.post(
            "/policies/documents",
            json={
                "title": "Temp Policy",
                "content": "Temporary.",
                "category": "Temp",
            },
        )
        doc_id = create_resp.json()["id"]
        resp = client.delete(f"/policies/documents/{doc_id}")
        assert resp.status_code == 204

    def test_query_policies(self, client):
        client.post(
            "/policies/documents",
            json={
                "title": "Leave Policy",
                "content": "Employees get 20 days annual leave.",
                "category": "HR",
            },
        )
        resp = client.post("/policies/query", json={"query": "annual leave days"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "annual leave days"
        assert "results" in data
