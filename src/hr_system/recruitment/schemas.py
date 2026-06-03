"""Recruitment Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from hr_system.recruitment.models import ApplicationStatus, JobStatus


class JobPostingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=100)
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    status: JobStatus = JobStatus.DRAFT


class JobPostingUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    department: str | None = None
    location: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    status: JobStatus | None = None


class JobPostingResponse(BaseModel):
    id: int
    title: str
    description: str
    department: str
    location: str
    salary_min: int | None
    salary_max: int | None
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CandidateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = None
    resume_text: str | None = None
    skills: str | None = None


class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    resume_text: str | None
    skills: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationCreate(BaseModel):
    job_posting_id: int
    candidate_id: int
    cover_letter: str | None = None


class ApplicationUpdateStatus(BaseModel):
    status: ApplicationStatus


class ApplicationResponse(BaseModel):
    id: int
    job_posting_id: int
    candidate_id: int
    status: ApplicationStatus
    cover_letter: str | None
    applied_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
