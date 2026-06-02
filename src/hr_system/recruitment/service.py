"""Recruitment business logic / service layer."""

from sqlalchemy.orm import Session

from hr_system.recruitment.models import Application, ApplicationStatus, Candidate, JobPosting
from hr_system.recruitment.schemas import (
    ApplicationCreate,
    CandidateCreate,
    JobPostingCreate,
    JobPostingUpdate,
)


class RecruitmentService:
    """Service layer for recruitment operations."""

    def __init__(self, db: Session):
        self.db = db

    # --- Job Postings ---

    def create_job_posting(self, data: JobPostingCreate) -> JobPosting:
        job = JobPosting(**data.model_dump())
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job_posting(self, job_id: int) -> JobPosting | None:
        return self.db.query(JobPosting).filter(JobPosting.id == job_id).first()

    def list_job_postings(self, status: str | None = None) -> list[JobPosting]:
        query = self.db.query(JobPosting)
        if status:
            query = query.filter(JobPosting.status == status)
        return query.all()

    def update_job_posting(self, job_id: int, data: JobPostingUpdate) -> JobPosting | None:
        job = self.get_job_posting(job_id)
        if not job:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job_posting(self, job_id: int) -> bool:
        job = self.get_job_posting(job_id)
        if not job:
            return False
        self.db.delete(job)
        self.db.commit()
        return True

    # --- Candidates ---

    def create_candidate(self, data: CandidateCreate) -> Candidate:
        candidate = Candidate(**data.model_dump())
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate

    def get_candidate(self, candidate_id: int) -> Candidate | None:
        return self.db.query(Candidate).filter(Candidate.id == candidate_id).first()

    def get_candidate_by_email(self, email: str) -> Candidate | None:
        return self.db.query(Candidate).filter(Candidate.email == email).first()

    def list_candidates(self) -> list[Candidate]:
        return self.db.query(Candidate).all()

    # --- Applications ---

    def create_application(self, data: ApplicationCreate) -> Application | None:
        job = self.get_job_posting(data.job_posting_id)
        candidate = self.get_candidate(data.candidate_id)
        if not job or not candidate:
            return None
        application = Application(**data.model_dump())
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_application(self, application_id: int) -> Application | None:
        return self.db.query(Application).filter(Application.id == application_id).first()

    def list_applications(self, job_id: int | None = None) -> list[Application]:
        query = self.db.query(Application)
        if job_id:
            query = query.filter(Application.job_posting_id == job_id)
        return query.all()

    def update_application_status(
        self, application_id: int, status: ApplicationStatus
    ) -> Application | None:
        application = self.get_application(application_id)
        if not application:
            return None
        application.status = status
        self.db.commit()
        self.db.refresh(application)
        return application
