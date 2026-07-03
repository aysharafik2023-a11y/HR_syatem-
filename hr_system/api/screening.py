"""Screening and ranking API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from hr_system.database import get_db
from hr_system.matching import MatchingEngine
from hr_system.models import Application, ApplicationStatus, Candidate, JobPosting
from hr_system.schemas import (
    ApplicationResponse,
    RankedCandidateResponse,
    ScreeningResultResponse,
)

router = APIRouter(prefix="/screening", tags=["Screening & Ranking"])
matching_engine = MatchingEngine()


@router.post("/run/{job_id}", response_model=ScreeningResultResponse)
def run_screening(
    job_id: int,
    top_n: int = Query(default=10, ge=1, le=100, description="Number of top candidates to return"),
    db: Session = Depends(get_db),
):
    """Run AI screening for all candidates against a specific job posting.

    Matches all candidates to the job description, ranks them, and stores results.
    Returns the top N candidates with their scores.
    """
    # Get job posting
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    # Get all candidates
    candidates = db.query(Candidate).all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found in the system")

    # Prepare resume data
    resumes = [(c.id, c.resume_text) for c in candidates]

    # Run matching engine
    ranked_results = matching_engine.rank_candidates(
        resumes=resumes,
        job_description=job.description,
        job_requirements=job.requirements,
    )

    # Store/update applications with scores
    screened_count = 0
    for rank, (candidate_id, match_result) in enumerate(ranked_results, start=1):
        # Check if application already exists
        application = (
            db.query(Application)
            .filter(
                Application.candidate_id == candidate_id,
                Application.job_posting_id == job_id,
            )
            .first()
        )

        if application:
            # Update existing
            application.match_score = match_result.overall_score
            application.skill_match_score = match_result.skill_match_score
            application.experience_match_score = match_result.experience_match_score
            application.overall_rank = rank
            application.status = ApplicationStatus.SCREENED
            application.screening_notes = match_result.notes
            application.screened_at = datetime.utcnow()
        else:
            # Create new
            application = Application(
                candidate_id=candidate_id,
                job_posting_id=job_id,
                match_score=match_result.overall_score,
                skill_match_score=match_result.skill_match_score,
                experience_match_score=match_result.experience_match_score,
                overall_rank=rank,
                status=ApplicationStatus.SCREENED,
                screening_notes=match_result.notes,
                screened_at=datetime.utcnow(),
            )
            db.add(application)
        screened_count += 1

    db.commit()

    # Build response with top N candidates
    top_candidates = []
    for rank, (candidate_id, match_result) in enumerate(ranked_results[:top_n], start=1):
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        application = (
            db.query(Application)
            .filter(
                Application.candidate_id == candidate_id,
                Application.job_posting_id == job_id,
            )
            .first()
        )
        if candidate and application:
            top_candidates.append(
                RankedCandidateResponse(
                    rank=rank,
                    candidate=candidate,
                    application=application,
                )
            )

    return ScreeningResultResponse(
        job_posting_id=job_id,
        job_title=job.title,
        total_candidates=len(candidates),
        screened_count=screened_count,
        top_candidates=top_candidates,
    )


@router.get("/results/{job_id}", response_model=list[RankedCandidateResponse])
def get_screening_results(
    job_id: int,
    top_n: int = Query(default=10, ge=1, le=100),
    min_score: float = Query(default=0.0, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
):
    """Get previously computed screening results for a job posting."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    applications = (
        db.query(Application)
        .filter(
            Application.job_posting_id == job_id,
            Application.match_score >= min_score,
        )
        .order_by(Application.overall_rank)
        .limit(top_n)
        .all()
    )

    results = []
    for app in applications:
        candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
        if candidate:
            results.append(
                RankedCandidateResponse(
                    rank=app.overall_rank or 0,
                    candidate=candidate,
                    application=app,
                )
            )

    return results


@router.patch("/applications/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status: ApplicationStatus,
    db: Session = Depends(get_db),
):
    """Update the status of a candidate's application (e.g., shortlist, reject)."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = status
    db.commit()
    db.refresh(application)
    return application


@router.get("/statistics/{job_id}")
def get_screening_statistics(job_id: int, db: Session = Depends(get_db)):
    """Get screening statistics for a job posting."""
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")

    applications = (
        db.query(Application).filter(Application.job_posting_id == job_id).all()
    )

    if not applications:
        return {
            "job_id": job_id,
            "job_title": job.title,
            "total_applications": 0,
            "average_score": 0.0,
            "score_distribution": {},
            "status_breakdown": {},
        }

    scores = [app.match_score for app in applications]
    status_counts = {}
    for app in applications:
        status = app.status.value if app.status else "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1

    # Score distribution buckets
    distribution = {"0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0, "0.6-0.8": 0, "0.8-1.0": 0}
    for score in scores:
        if score < 0.2:
            distribution["0.0-0.2"] += 1
        elif score < 0.4:
            distribution["0.2-0.4"] += 1
        elif score < 0.6:
            distribution["0.4-0.6"] += 1
        elif score < 0.8:
            distribution["0.6-0.8"] += 1
        else:
            distribution["0.8-1.0"] += 1

    return {
        "job_id": job_id,
        "job_title": job.title,
        "total_applications": len(applications),
        "average_score": round(sum(scores) / len(scores), 4),
        "highest_score": round(max(scores), 4),
        "lowest_score": round(min(scores), 4),
        "score_distribution": distribution,
        "status_breakdown": status_counts,
    }
