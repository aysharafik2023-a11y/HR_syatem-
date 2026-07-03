"""API routes for candidate screening and ranking."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hr_system.database import get_db
from hr_system.models import Candidate, Job, MatchResult
from hr_system.schemas import (
    CandidateResponse,
    MatchResultResponse,
    RankedCandidateResponse,
    ScreeningRequest,
    ScreeningResponse,
)
from hr_system.services.matcher import match_candidate_to_job, rank_candidates

router = APIRouter(prefix="/screening", tags=["screening"])


@router.post("/run", response_model=ScreeningResponse)
def run_screening(request: ScreeningRequest, db: Session = Depends(get_db)):
    """
    Screen all candidates against a specific job.

    Computes AI-powered match scores and ranks candidates.
    Results are stored in the database for later retrieval.
    """
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    candidates = db.query(Candidate).all()
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found. Upload resumes first.")

    # Compute match scores for each candidate
    match_data = []
    for candidate in candidates:
        scores = match_candidate_to_job(
            resume_text=candidate.resume_text,
            candidate_skills=candidate.skills,
            candidate_experience_years=candidate.experience_years,
            candidate_education=candidate.education,
            job_description=job.description,
            job_requirements=job.requirements,
            job_preferred_skills=job.preferred_skills,
            job_min_experience=job.min_experience_years,
        )
        scores["candidate_id"] = candidate.id
        match_data.append(scores)

    # Rank candidates
    ranked = rank_candidates(match_data)

    # Store results in database (replace existing results for this job)
    db.query(MatchResult).filter(MatchResult.job_id == job.id).delete()

    for result in ranked:
        match_result = MatchResult(
            candidate_id=result["candidate_id"],
            job_id=job.id,
            overall_score=result["overall_score"],
            skills_score=result["skills_score"],
            experience_score=result["experience_score"],
            education_score=result["education_score"],
            semantic_score=result["semantic_score"],
            rank=result["rank"],
        )
        db.add(match_result)

    db.commit()

    # Build response
    ranked_responses = []
    for result in ranked:
        candidate = db.query(Candidate).filter(Candidate.id == result["candidate_id"]).first()
        ranked_responses.append(
            RankedCandidateResponse(
                rank=result["rank"],
                candidate=CandidateResponse.model_validate(candidate),
                overall_score=result["overall_score"],
                skills_score=result["skills_score"],
                experience_score=result["experience_score"],
                education_score=result["education_score"],
                semantic_score=result["semantic_score"],
            )
        )

    return ScreeningResponse(
        job_id=job.id,
        job_title=job.title,
        total_candidates_screened=len(ranked),
        ranked_candidates=ranked_responses,
    )


@router.get("/jobs/{job_id}/candidates", response_model=list[RankedCandidateResponse])
def get_ranked_candidates(
    job_id: int, top_n: int = 10, db: Session = Depends(get_db)
):
    """Get previously computed ranked candidates for a job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    results = (
        db.query(MatchResult)
        .filter(MatchResult.job_id == job_id)
        .order_by(MatchResult.rank)
        .limit(top_n)
        .all()
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No screening results found. Run screening first via POST /screening/run.",
        )

    ranked_responses = []
    for result in results:
        candidate = db.query(Candidate).filter(Candidate.id == result.candidate_id).first()
        ranked_responses.append(
            RankedCandidateResponse(
                rank=result.rank,
                candidate=CandidateResponse.model_validate(candidate),
                overall_score=result.overall_score,
                skills_score=result.skills_score,
                experience_score=result.experience_score,
                education_score=result.education_score,
                semantic_score=result.semantic_score,
            )
        )

    return ranked_responses


@router.get("/candidates/{candidate_id}/matches", response_model=list[MatchResultResponse])
def get_candidate_matches(candidate_id: int, db: Session = Depends(get_db)):
    """Get all match results for a specific candidate across all jobs."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    results = (
        db.query(MatchResult)
        .filter(MatchResult.candidate_id == candidate_id)
        .order_by(MatchResult.overall_score.desc())
        .all()
    )

    return results
