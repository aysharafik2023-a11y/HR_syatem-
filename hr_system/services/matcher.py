"""AI-powered resume-to-job matching engine using sentence embeddings."""

import logging

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Model loaded successfully.")
    return _model


def compute_semantic_similarity(text_a: str, text_b: str) -> float:
    """Compute cosine similarity between two texts using sentence embeddings."""
    model = get_model()
    embeddings = model.encode([text_a, text_b], normalize_embeddings=True)
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(np.clip(similarity, 0.0, 1.0))


def compute_skills_score(candidate_skills: str | None, job_requirements: str) -> float:
    """Score how well candidate skills match job requirements."""
    if not candidate_skills:
        return 0.0
    return compute_semantic_similarity(candidate_skills, job_requirements)


def compute_experience_score(
    candidate_years: float | None, required_years: float | None
) -> float:
    """Score candidate experience against job requirements."""
    if required_years is None:
        return 0.7  # Neutral score when no requirement specified
    if candidate_years is None:
        return 0.3  # Low score when we can't determine experience

    if candidate_years >= required_years:
        # Full score if meets requirement, slight bonus for exceeding
        bonus = min(0.1, (candidate_years - required_years) * 0.02)
        return min(1.0, 0.9 + bonus)
    else:
        # Proportional score based on how close they are
        return max(0.1, candidate_years / required_years * 0.9)


def compute_education_score(candidate_education: str | None, job_requirements: str) -> float:
    """Score candidate education against job requirements."""
    if not candidate_education:
        return 0.3
    return compute_semantic_similarity(candidate_education, job_requirements)


def match_candidate_to_job(
    resume_text: str,
    candidate_skills: str | None,
    candidate_experience_years: float | None,
    candidate_education: str | None,
    job_description: str,
    job_requirements: str,
    job_preferred_skills: str | None,
    job_min_experience: float | None,
) -> dict[str, float]:
    """
    Compute match scores between a candidate and a job.

    Returns a dict with individual scores and an overall weighted score.
    Weights: semantic=0.35, skills=0.30, experience=0.20, education=0.15
    """
    # Full resume vs full job description semantic similarity
    job_text = f"{job_description} {job_requirements}"
    semantic_score = compute_semantic_similarity(resume_text, job_text)

    # Skills matching
    skills_target = job_preferred_skills or job_requirements
    skills_score = compute_skills_score(candidate_skills, skills_target)

    # Experience scoring
    experience_score = compute_experience_score(candidate_experience_years, job_min_experience)

    # Education scoring
    education_score = compute_education_score(candidate_education, job_requirements)

    # Weighted overall score
    overall_score = (
        semantic_score * 0.35
        + skills_score * 0.30
        + experience_score * 0.20
        + education_score * 0.15
    )

    return {
        "overall_score": round(overall_score, 4),
        "semantic_score": round(semantic_score, 4),
        "skills_score": round(skills_score, 4),
        "experience_score": round(experience_score, 4),
        "education_score": round(education_score, 4),
    }


def rank_candidates(match_results: list[dict]) -> list[dict]:
    """
    Rank candidates by overall score (descending).

    Each entry should have 'candidate_id' and score fields.
    Returns the same list with 'rank' added.
    """
    sorted_results = sorted(match_results, key=lambda x: x["overall_score"], reverse=True)
    for i, result in enumerate(sorted_results, start=1):
        result["rank"] = i
    return sorted_results
