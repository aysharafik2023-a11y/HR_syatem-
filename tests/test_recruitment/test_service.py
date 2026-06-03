"""Tests for recruitment service layer."""

import pytest

from hr_system.recruitment.models import ApplicationStatus, JobStatus
from hr_system.recruitment.schemas import (
    ApplicationCreate,
    CandidateCreate,
    JobPostingCreate,
    JobPostingUpdate,
)
from hr_system.recruitment.service import RecruitmentService


@pytest.fixture
def service(db_session):
    return RecruitmentService(db_session)


@pytest.fixture
def sample_job(service):
    return service.create_job_posting(
        JobPostingCreate(
            title="Python Developer",
            description="Build APIs with FastAPI",
            department="Engineering",
            location="Remote",
            salary_min=80000,
            salary_max=120000,
            status=JobStatus.OPEN,
        )
    )


@pytest.fixture
def sample_candidate(service):
    return service.create_candidate(
        CandidateCreate(
            name="Test User",
            email="test@example.com",
            phone="+1111111111",
            skills="Python, SQL, FastAPI",
        )
    )


class TestJobPostings:
    def test_create_job_posting(self, service):
        job = service.create_job_posting(
            JobPostingCreate(
                title="Data Engineer",
                description="Build data pipelines",
                department="Data",
                location="NYC",
            )
        )
        assert job.id is not None
        assert job.title == "Data Engineer"
        assert job.status == JobStatus.DRAFT

    def test_get_job_posting(self, service, sample_job):
        found = service.get_job_posting(sample_job.id)
        assert found is not None
        assert found.title == sample_job.title

    def test_get_job_posting_not_found(self, service):
        assert service.get_job_posting(9999) is None

    def test_list_job_postings(self, service, sample_job):
        jobs = service.list_job_postings()
        assert len(jobs) >= 1

    def test_list_job_postings_filter_status(self, service, sample_job):
        jobs = service.list_job_postings(status="open")
        assert all(j.status == JobStatus.OPEN for j in jobs)

    def test_update_job_posting(self, service, sample_job):
        updated = service.update_job_posting(
            sample_job.id, JobPostingUpdate(title="Senior Python Developer")
        )
        assert updated is not None
        assert updated.title == "Senior Python Developer"

    def test_update_job_posting_not_found(self, service):
        result = service.update_job_posting(9999, JobPostingUpdate(title="X"))
        assert result is None

    def test_delete_job_posting(self, service, sample_job):
        assert service.delete_job_posting(sample_job.id) is True
        assert service.get_job_posting(sample_job.id) is None

    def test_delete_job_posting_not_found(self, service):
        assert service.delete_job_posting(9999) is False


class TestCandidates:
    def test_create_candidate(self, service):
        candidate = service.create_candidate(
            CandidateCreate(name="Bob", email="bob@example.com")
        )
        assert candidate.id is not None
        assert candidate.name == "Bob"

    def test_get_candidate(self, service, sample_candidate):
        found = service.get_candidate(sample_candidate.id)
        assert found is not None
        assert found.email == "test@example.com"

    def test_get_candidate_not_found(self, service):
        assert service.get_candidate(9999) is None

    def test_get_candidate_by_email(self, service, sample_candidate):
        found = service.get_candidate_by_email("test@example.com")
        assert found is not None
        assert found.name == "Test User"

    def test_get_candidate_by_email_not_found(self, service):
        assert service.get_candidate_by_email("nope@example.com") is None

    def test_list_candidates(self, service, sample_candidate):
        candidates = service.list_candidates()
        assert len(candidates) >= 1


class TestApplications:
    def test_create_application(self, service, sample_job, sample_candidate):
        app = service.create_application(
            ApplicationCreate(
                job_posting_id=sample_job.id,
                candidate_id=sample_candidate.id,
                cover_letter="I'm a great fit!",
            )
        )
        assert app is not None
        assert app.status == ApplicationStatus.APPLIED
        assert app.cover_letter == "I'm a great fit!"

    def test_create_application_invalid_job(self, service, sample_candidate):
        result = service.create_application(
            ApplicationCreate(job_posting_id=9999, candidate_id=sample_candidate.id)
        )
        assert result is None

    def test_create_application_invalid_candidate(self, service, sample_job):
        result = service.create_application(
            ApplicationCreate(job_posting_id=sample_job.id, candidate_id=9999)
        )
        assert result is None

    def test_list_applications(self, service, sample_job, sample_candidate):
        service.create_application(
            ApplicationCreate(
                job_posting_id=sample_job.id, candidate_id=sample_candidate.id
            )
        )
        apps = service.list_applications()
        assert len(apps) >= 1

    def test_list_applications_by_job(self, service, sample_job, sample_candidate):
        service.create_application(
            ApplicationCreate(
                job_posting_id=sample_job.id, candidate_id=sample_candidate.id
            )
        )
        apps = service.list_applications(job_id=sample_job.id)
        assert len(apps) == 1

    def test_update_application_status(self, service, sample_job, sample_candidate):
        app = service.create_application(
            ApplicationCreate(
                job_posting_id=sample_job.id, candidate_id=sample_candidate.id
            )
        )
        updated = service.update_application_status(app.id, ApplicationStatus.INTERVIEW)
        assert updated is not None
        assert updated.status == ApplicationStatus.INTERVIEW

    def test_update_application_status_not_found(self, service):
        result = service.update_application_status(9999, ApplicationStatus.HIRED)
        assert result is None
