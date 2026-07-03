"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field

# --- Job Posting Schemas ---


class JobPostingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    department: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10)
    requirements: str = Field(..., min_length=10)
    preferred_skills: str | None = None
    location: str | None = None


class JobPostingUpdate(BaseModel):
    title: str | None = None
    department: str | None = None
    description: str | None = None
    requirements: str | None = None
    preferred_skills: str | None = None
    location: str | None = None
    is_active: bool | None = None


class JobPostingResponse(BaseModel):
    id: int
    title: str
    department: str
    description: str
    requirements: str
    preferred_skills: str | None
    location: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Candidate Schemas ---


class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    skills: str | None
    experience_years: float | None
    education: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., max_length=200)
    phone: str | None = None
    resume_text: str = Field(..., min_length=10)
    skills: str | None = None
    experience_years: float | None = None
    education: str | None = None


# --- Application Schemas ---


class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_posting_id: int
    match_score: float
    skill_match_score: float
    experience_match_score: float
    overall_rank: int | None
    status: str
    screening_notes: str | None
    created_at: datetime
    screened_at: datetime | None

    model_config = {"from_attributes": True}


class RankedCandidateResponse(BaseModel):
    rank: int
    candidate: CandidateResponse
    application: ApplicationResponse


class ScreeningRequest(BaseModel):
    job_posting_id: int


class ScreeningResultResponse(BaseModel):
    job_posting_id: int
    job_title: str
    total_candidates: int
    screened_count: int
    top_candidates: list[RankedCandidateResponse]


# --- Resume Upload Response ---


class ResumeUploadResponse(BaseModel):
    candidate_id: int
    name: str
    email: str
    extracted_text_preview: str
    skills_detected: list[str]
    message: str
