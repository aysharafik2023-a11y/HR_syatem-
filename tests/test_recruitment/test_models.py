"""Tests for recruitment models."""

from hr_system.recruitment.models import (
    Application,
    ApplicationStatus,
    Candidate,
    JobPosting,
    JobStatus,
)


def test_job_status_enum_values():
    assert JobStatus.OPEN == "open"
    assert JobStatus.CLOSED == "closed"
    assert JobStatus.DRAFT == "draft"


def test_application_status_enum_values():
    assert ApplicationStatus.APPLIED == "applied"
    assert ApplicationStatus.SCREENING == "screening"
    assert ApplicationStatus.INTERVIEW == "interview"
    assert ApplicationStatus.OFFER == "offer"
    assert ApplicationStatus.HIRED == "hired"
    assert ApplicationStatus.REJECTED == "rejected"


def test_job_posting_creation(db_session):
    job = JobPosting(
        title="Software Engineer",
        description="Build great software",
        department="Engineering",
        location="Remote",
        status=JobStatus.OPEN,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    assert job.id is not None
    assert job.title == "Software Engineer"
    assert job.status == JobStatus.OPEN
    assert job.created_at is not None


def test_candidate_creation(db_session):
    candidate = Candidate(
        name="Jane Doe",
        email="jane@example.com",
        phone="+1234567890",
        skills="Python, FastAPI",
    )
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)

    assert candidate.id is not None
    assert candidate.email == "jane@example.com"


def test_application_creation(db_session):
    job = JobPosting(
        title="Backend Dev",
        description="API development",
        department="Engineering",
        location="NYC",
    )
    candidate = Candidate(name="John", email="john@test.com")
    db_session.add_all([job, candidate])
    db_session.commit()

    app = Application(
        job_posting_id=job.id,
        candidate_id=candidate.id,
        status=ApplicationStatus.APPLIED,
    )
    db_session.add(app)
    db_session.commit()
    db_session.refresh(app)

    assert app.id is not None
    assert app.job_posting_id == job.id
    assert app.candidate_id == candidate.id
    assert app.status == ApplicationStatus.APPLIED


def test_job_posting_relationship(db_session):
    job = JobPosting(
        title="ML Engineer",
        description="Machine learning",
        department="AI",
        location="SF",
    )
    candidate = Candidate(name="Alice", email="alice@test.com")
    db_session.add_all([job, candidate])
    db_session.commit()

    app = Application(job_posting_id=job.id, candidate_id=candidate.id)
    db_session.add(app)
    db_session.commit()

    db_session.refresh(job)
    assert len(job.applications) == 1
    assert job.applications[0].candidate_id == candidate.id
