"""Test fixtures and configuration."""

import pytest
from app.main import app
from fastapi.testclient import TestClient
from hr_system.app import app as hr_app
from hr_system.database import Base, get_db
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Sync fixtures for hr_system tests
TEST_DATABASE_URL = "sqlite:///./test_hr_system.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create fresh database tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Test client with overridden database dependency."""
    hr_app.dependency_overrides[get_db] = override_get_db
    with TestClient(hr_app) as c:
        yield c
    hr_app.dependency_overrides.clear()


@pytest.fixture
async def async_client():
    """Async test client for app module tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def db_session():
    """Direct database session for test setup."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_job_posting():
    """Sample job posting data."""
    return {
        "title": "Senior Python Developer",
        "department": "Engineering",
        "description": (
            "We are looking for an experienced Python developer to join our backend team. "
            "You will design and implement scalable microservices, work with databases, "
            "and collaborate with cross-functional teams."
        ),
        "requirements": (
            "5+ years of experience with Python. Strong knowledge of Django or FastAPI. "
            "Experience with PostgreSQL, Redis, and Docker. Familiarity with AWS services. "
            "Understanding of CI/CD pipelines and agile methodologies."
        ),
        "preferred_skills": "Machine learning, Kubernetes, GraphQL",
        "location": "Remote",
    }


@pytest.fixture
def sample_candidate():
    """Sample candidate data matching the senior Python role."""
    return {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1-555-0123",
        "resume_text": (
            "Jane Smith - Senior Software Engineer\n"
            "7 years of experience in software development.\n\n"
            "Skills: Python, Django, FastAPI, PostgreSQL, Redis, Docker, AWS, "
            "Kubernetes, CI/CD, Git, Linux, REST API, microservices, agile.\n\n"
            "Experience:\n"
            "- Led team of 5 developers building microservices architecture\n"
            "- Designed and implemented REST APIs serving 1M+ requests/day\n"
            "- Managed PostgreSQL databases with 100GB+ data\n"
            "- Deployed applications on AWS using Docker and Kubernetes\n\n"
            "Education: M.S. Computer Science, Stanford University"
        ),
    }
