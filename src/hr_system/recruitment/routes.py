"""Recruitment API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hr_system.database import get_db
from hr_system.recruitment.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdateStatus,
    CandidateCreate,
    CandidateResponse,
    JobPostingCreate,
    JobPostingResponse,
    JobPostingUpdate,
)
from hr_system.recruitment.service import RecruitmentService

router = APIRouter(prefix="/recruitment", tags=["recruitment"])


def get_service(db: Session = Depends(get_db)) -> RecruitmentService:
    return RecruitmentService(db)


# --- Job Postings ---


@router.post("/jobs", response_model=JobPostingResponse, status_code=201)
def create_job(data: JobPostingCreate, service: RecruitmentService = Depends(get_service)):
    return service.create_job_posting(data)


@router.get("/jobs", response_model=list[JobPostingResponse])
def list_jobs(status: str | None = None, service: RecruitmentService = Depends(get_service)):
    return service.list_job_postings(status)


@router.get("/jobs/{job_id}", response_model=JobPostingResponse)
def get_job(job_id: int, service: RecruitmentService = Depends(get_service)):
    job = service.get_job_posting(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.patch("/jobs/{job_id}", response_model=JobPostingResponse)
def update_job(
    job_id: int, data: JobPostingUpdate, service: RecruitmentService = Depends(get_service)
):
    job = service.update_job_posting(job_id, data)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: int, service: RecruitmentService = Depends(get_service)):
    if not service.delete_job_posting(job_id):
        raise HTTPException(status_code=404, detail="Job posting not found")


# --- Candidates ---


@router.post("/candidates", response_model=CandidateResponse, status_code=201)
def create_candidate(data: CandidateCreate, service: RecruitmentService = Depends(get_service)):
    existing = service.get_candidate_by_email(data.email)
    if existing:
        raise HTTPException(status_code=409, detail="Candidate with this email already exists")
    return service.create_candidate(data)


@router.get("/candidates", response_model=list[CandidateResponse])
def list_candidates(service: RecruitmentService = Depends(get_service)):
    return service.list_candidates()


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, service: RecruitmentService = Depends(get_service)):
    candidate = service.get_candidate(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


# --- Applications ---


@router.post("/applications", response_model=ApplicationResponse, status_code=201)
def create_application(
    data: ApplicationCreate, service: RecruitmentService = Depends(get_service)
):
    application = service.create_application(data)
    if not application:
        raise HTTPException(status_code=404, detail="Job posting or candidate not found")
    return application


@router.get("/applications", response_model=list[ApplicationResponse])
def list_applications(
    job_id: int | None = None, service: RecruitmentService = Depends(get_service)
):
    return service.list_applications(job_id)


@router.patch("/applications/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    data: ApplicationUpdateStatus,
    service: RecruitmentService = Depends(get_service),
):
    application = service.update_application_status(application_id, data.status)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application
