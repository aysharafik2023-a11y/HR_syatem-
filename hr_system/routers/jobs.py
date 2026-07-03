"""API routes for job description management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hr_system.database import get_db
from hr_system.models import Job
from hr_system.schemas import JobCreate, JobResponse, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """Create a new job posting."""
    job = Job(
        title=job_data.title,
        department=job_data.department,
        description=job_data.description,
        requirements=job_data.requirements,
        preferred_skills=job_data.preferred_skills,
        min_experience_years=job_data.min_experience_years,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/", response_model=list[JobResponse])
def list_jobs(
    active_only: bool = True, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    """List all job postings with optional active filter."""
    query = db.query(Job)
    if active_only:
        query = query.filter(Job.is_active == True)  # noqa: E712
    return query.offset(skip).limit(limit).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job posting by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job_data: JobUpdate, db: Session = Depends(get_db)):
    """Update an existing job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    db.delete(job)
    db.commit()
