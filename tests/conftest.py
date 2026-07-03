"""Test fixtures and configuration."""

import pytest
from fastapi.testclient import TestClient
from hr_system.app import app
from hr_system.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use in-memory SQLite for tests
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
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


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
