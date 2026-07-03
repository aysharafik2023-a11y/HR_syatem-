"""API routes for resume upload and candidate management."""

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from hr_system.database import get_db
from hr_system.models import Candidate
from hr_system.schemas import CandidateResponse
from hr_system.services.resume_parser import parse_resume

router = APIRouter(prefix="/resumes", tags=["resumes"])

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


@router.post("/upload", response_model=CandidateResponse, status_code=201)
def upload_resume(file: UploadFile, db: Session = Depends(get_db)):
    """Upload a resume file, parse it, and create a candidate record."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Save file to disk
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        parsed = parse_resume(file_path)
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Failed to parse resume: {e}")

    if not parsed["text"].strip():
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="Could not extract text from resume.")

    email = parsed["email"]
    if not email:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail="Could not extract email from resume. Please ensure it contains an email.",
        )

    # Check if candidate already exists
    existing = db.query(Candidate).filter(Candidate.email == email).first()
    if existing:
        # Update existing candidate
        existing.name = parsed["name"]
        existing.phone = parsed["phone"]
        existing.resume_text = parsed["text"]
        existing.resume_filename = file.filename
        existing.skills = parsed["skills"]
        existing.experience_years = parsed["experience_years"]
        existing.education = parsed["education"]
        db.commit()
        db.refresh(existing)
        return existing

    candidate = Candidate(
        name=parsed["name"],
        email=email,
        phone=parsed["phone"],
        resume_text=parsed["text"],
        resume_filename=file.filename,
        skills=parsed["skills"],
        experience_years=parsed["experience_years"],
        education=parsed["education"],
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post("/upload/batch", response_model=list[CandidateResponse], status_code=201)
def upload_resumes_batch(files: list[UploadFile], db: Session = Depends(get_db)):
    """Upload multiple resume files at once."""
    results = []
    errors = []

    for file in files:
        if not file.filename:
            errors.append("File with no filename skipped.")
            continue

        suffix = Path(file.filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            errors.append(f"Skipped {file.filename}: unsupported format.")
            continue

        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            parsed = parse_resume(file_path)
        except Exception:
            errors.append(f"Failed to parse {file.filename}")
            file_path.unlink(missing_ok=True)
            continue

        email = parsed["email"]
        if not email:
            errors.append(f"No email found in {file.filename}")
            continue

        existing = db.query(Candidate).filter(Candidate.email == email).first()
        if existing:
            existing.name = parsed["name"]
            existing.resume_text = parsed["text"]
            existing.resume_filename = file.filename
            existing.skills = parsed["skills"]
            existing.experience_years = parsed["experience_years"]
            existing.education = parsed["education"]
            db.commit()
            db.refresh(existing)
            results.append(existing)
        else:
            candidate = Candidate(
                name=parsed["name"],
                email=email,
                phone=parsed["phone"],
                resume_text=parsed["text"],
                resume_filename=file.filename,
                skills=parsed["skills"],
                experience_years=parsed["experience_years"],
                education=parsed["education"],
            )
            db.add(candidate)
            db.commit()
            db.refresh(candidate)
            results.append(candidate)

    if not results and errors:
        raise HTTPException(status_code=422, detail="; ".join(errors))

    return results


@router.get("/", response_model=list[CandidateResponse])
def list_candidates(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all candidates with pagination."""
    return db.query(Candidate).offset(skip).limit(limit).all()


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get a specific candidate by ID."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return candidate


@router.delete("/{candidate_id}", status_code=204)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    db.delete(candidate)
    db.commit()
