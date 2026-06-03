"""Tests for recruitment API routes."""

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


class TestJobRoutes:
    def test_create_job(self, client):
        resp = client.post(
            "/recruitment/jobs",
            json={
                "title": "QA Engineer",
                "description": "Test all the things",
                "department": "QA",
                "location": "Remote",
                "status": "open",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "QA Engineer"
        assert data["id"] is not None

    def test_list_jobs(self, client):
        client.post(
            "/recruitment/jobs",
            json={
                "title": "Job 1",
                "description": "Desc",
                "department": "Eng",
                "location": "Remote",
            },
        )
        resp = client.get("/recruitment/jobs")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_job(self, client):
        create_resp = client.post(
            "/recruitment/jobs",
            json={
                "title": "DevOps",
                "description": "CI/CD",
                "department": "Infra",
                "location": "SF",
            },
        )
        job_id = create_resp.json()["id"]
        resp = client.get(f"/recruitment/jobs/{job_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "DevOps"

    def test_get_job_not_found(self, client):
        resp = client.get("/recruitment/jobs/9999")
        assert resp.status_code == 404

    def test_update_job(self, client):
        create_resp = client.post(
            "/recruitment/jobs",
            json={
                "title": "Engineer",
                "description": "Code",
                "department": "Eng",
                "location": "Remote",
            },
        )
        job_id = create_resp.json()["id"]
        resp = client.patch(
            f"/recruitment/jobs/{job_id}", json={"title": "Senior Engineer"}
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Senior Engineer"

    def test_delete_job(self, client):
        create_resp = client.post(
            "/recruitment/jobs",
            json={
                "title": "Temp",
                "description": "To delete",
                "department": "X",
                "location": "Y",
            },
        )
        job_id = create_resp.json()["id"]
        resp = client.delete(f"/recruitment/jobs/{job_id}")
        assert resp.status_code == 204


class TestCandidateRoutes:
    def test_create_candidate(self, client):
        resp = client.post(
            "/recruitment/candidates",
            json={"name": "Alice", "email": "alice@test.com", "skills": "Python"},
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Alice"

    def test_create_candidate_duplicate_email(self, client):
        client.post(
            "/recruitment/candidates",
            json={"name": "Bob", "email": "bob@test.com"},
        )
        resp = client.post(
            "/recruitment/candidates",
            json={"name": "Bob2", "email": "bob@test.com"},
        )
        assert resp.status_code == 409

    def test_list_candidates(self, client):
        client.post(
            "/recruitment/candidates",
            json={"name": "Carol", "email": "carol@test.com"},
        )
        resp = client.get("/recruitment/candidates")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_get_candidate_not_found(self, client):
        resp = client.get("/recruitment/candidates/9999")
        assert resp.status_code == 404


class TestApplicationRoutes:
    def _create_job_and_candidate(self, client):
        job_resp = client.post(
            "/recruitment/jobs",
            json={
                "title": "Job",
                "description": "Desc",
                "department": "Eng",
                "location": "Remote",
            },
        )
        candidate_resp = client.post(
            "/recruitment/candidates",
            json={"name": "Dave", "email": "dave@test.com"},
        )
        return job_resp.json()["id"], candidate_resp.json()["id"]

    def test_create_application(self, client):
        job_id, candidate_id = self._create_job_and_candidate(client)
        resp = client.post(
            "/recruitment/applications",
            json={"job_posting_id": job_id, "candidate_id": candidate_id},
        )
        assert resp.status_code == 201
        assert resp.json()["status"] == "applied"

    def test_create_application_invalid_ids(self, client):
        resp = client.post(
            "/recruitment/applications",
            json={"job_posting_id": 9999, "candidate_id": 9999},
        )
        assert resp.status_code == 404

    def test_update_application_status(self, client):
        job_id, candidate_id = self._create_job_and_candidate(client)
        app_resp = client.post(
            "/recruitment/applications",
            json={"job_posting_id": job_id, "candidate_id": candidate_id},
        )
        app_id = app_resp.json()["id"]
        resp = client.patch(
            f"/recruitment/applications/{app_id}/status",
            json={"status": "interview"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "interview"
