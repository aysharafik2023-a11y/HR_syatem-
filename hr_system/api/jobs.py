"""Job posting API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hr_system.database import get_db
from hr_system.models import JobPosting
from hr_system.schemas import JobPostingCreate, JobPostingResponse, JobPostingUpdate

router = APIRouter(prefix="/jobs", tags=["Job Postings"])


@router.post("/", response_model=JobPostingResponse, status_code=201)
def create_job_posting(job: JobPostingCreate, db: Session = Depends(get_db)):
    """Create a new job posting."""
    db_job = JobPosting(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/", response_model=list[JobPostingResponse])
def list_job_postings(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all job postings, optionally filtered by active status."""
    query = db.query(JobPosting)
    if active_only:
        query = query.filter(JobPosting.is_active.is_(True))
    return query.offset(skip).limit(limit).all()


@router.get("/{job_id}", response_model=JobPostingResponse)
def get_job_posting(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job posting by ID."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.patch("/{job_id}", response_model=JobPostingResponse)
def update_job_posting(job_id: int, update: JobPostingUpdate, db: Session = Depends(get_db)):
    """Update an existing job posting."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job_posting(job_id: int, db: Session = Depends(get_db)):
    """Delete a job posting."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    db.delete(job)
    db.commit()
