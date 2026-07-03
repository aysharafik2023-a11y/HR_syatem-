"""Resume upload and parsing API endpoints."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from hr_system.config import settings
from hr_system.database import get_db
from hr_system.matching import MatchingEngine
from hr_system.models import Candidate
from hr_system.parsers import parse_resume
from hr_system.schemas import CandidateCreate, CandidateResponse, ResumeUploadResponse

router = APIRouter(prefix="/resumes", tags=["Resumes"])
matching_engine = MatchingEngine()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile,
    candidate_name: str,
    candidate_email: str,
    candidate_phone: str | None = None,
    db: Session = Depends(get_db),
):
    """Upload and parse a resume file (PDF or DOCX).

    Extracts text, detects skills, and stores the candidate in the database.
    """
    # Validate file format
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in settings.supported_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {suffix}. Supported: {settings.supported_formats}",
        )

    # Check file size
    content = await file.read()
    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
        )

    # Check for duplicate email
    existing = db.query(Candidate).filter(Candidate.email == candidate_email).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Candidate with email {candidate_email} already exists (ID: {existing.id})",
        )

    # Save file
    file_name = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = settings.upload_path / file_name
    file_path.write_bytes(content)

    # Parse resume
    try:
        resume_text = parse_resume(file_path)
    except ValueError as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(e))

    # Extract skills and experience
    skills = matching_engine.extract_skills(resume_text)
    experience_years = matching_engine.extract_experience_years(resume_text)

    # Store candidate
    candidate = Candidate(
        name=candidate_name,
        email=candidate_email,
        phone=candidate_phone,
        resume_text=resume_text,
        resume_file_path=str(file_path),
        skills=", ".join(skills) if skills else None,
        experience_years=experience_years,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return ResumeUploadResponse(
        candidate_id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        extracted_text_preview=resume_text[:300] + "..." if len(resume_text) > 300 else resume_text,
        skills_detected=skills,
        message="Resume uploaded and parsed successfully",
    )


@router.post("/submit", response_model=CandidateResponse, status_code=201)
def submit_resume_text(candidate: CandidateCreate, db: Session = Depends(get_db)):
    """Submit a resume as plain text (for pre-parsed resumes or API integrations)."""
    existing = db.query(Candidate).filter(Candidate.email == candidate.email).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Candidate with email {candidate.email} already exists (ID: {existing.id})",
        )

    # Auto-extract skills if not provided
    skills = candidate.skills
    if not skills:
        extracted = matching_engine.extract_skills(candidate.resume_text)
        skills = ", ".join(extracted) if extracted else None

    experience_years = candidate.experience_years
    if experience_years is None:
        experience_years = matching_engine.extract_experience_years(candidate.resume_text)

    db_candidate = Candidate(
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        resume_text=candidate.resume_text,
        skills=skills,
        experience_years=experience_years,
        education=candidate.education,
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


@router.get("/", response_model=list[CandidateResponse])
def list_candidates(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all candidates."""
    return db.query(Candidate).offset(skip).limit(limit).all()


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get a specific candidate by ID."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
