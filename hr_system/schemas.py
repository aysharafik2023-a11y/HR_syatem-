"""Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


class CandidateCreate(BaseModel):
    """Schema for manually creating a candidate (without file upload)."""

    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)
    phone: str | None = None
    skills: str | None = None
    experience_years: float | None = None
    education: str | None = None


class CandidateResponse(BaseModel):
    """Response schema for a candidate."""

    id: int
    name: str
    email: str
    phone: str | None
    resume_filename: str
    skills: str | None
    experience_years: float | None
    education: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobCreate(BaseModel):
    """Schema for creating a job posting."""

    title: str = Field(..., min_length=1, max_length=255)
    department: str | None = None
    description: str = Field(..., min_length=10)
    requirements: str = Field(..., min_length=10)
    preferred_skills: str | None = None
    min_experience_years: float | None = None


class JobUpdate(BaseModel):
    """Schema for updating a job posting."""

    title: str | None = None
    department: str | None = None
    description: str | None = None
    requirements: str | None = None
    preferred_skills: str | None = None
    min_experience_years: float | None = None
    is_active: bool | None = None


class JobResponse(BaseModel):
    """Response schema for a job posting."""

    id: int
    title: str
    department: str | None
    description: str
    requirements: str
    preferred_skills: str | None
    min_experience_years: float | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MatchResultResponse(BaseModel):
    """Response schema for a match result."""

    id: int
    candidate_id: int
    job_id: int
    overall_score: float
    skills_score: float
    experience_score: float
    education_score: float
    semantic_score: float
    rank: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RankedCandidateResponse(BaseModel):
    """Response schema for a ranked candidate (includes candidate info + scores)."""

    rank: int
    candidate: CandidateResponse
    overall_score: float
    skills_score: float
    experience_score: float
    education_score: float
    semantic_score: float


class ScreeningRequest(BaseModel):
    """Request to screen all candidates against a specific job."""

    job_id: int


class ScreeningResponse(BaseModel):
    """Response after screening candidates against a job."""

    job_id: int
    job_title: str
    total_candidates_screened: int
    ranked_candidates: list[RankedCandidateResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    total_candidates: int
    total_jobs: int
