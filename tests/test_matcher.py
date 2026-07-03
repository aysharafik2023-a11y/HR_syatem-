"""Tests for AI matching engine."""


from hr_system.services.matcher import (
    compute_experience_score,
    match_candidate_to_job,
    rank_candidates,
)


def test_compute_experience_score_meets_requirement():
    """Candidate meets or exceeds requirement."""
    score = compute_experience_score(5.0, 5.0)
    assert score >= 0.9


def test_compute_experience_score_exceeds_requirement():
    """Candidate exceeds requirement."""
    score = compute_experience_score(10.0, 5.0)
    assert score >= 0.9


def test_compute_experience_score_below_requirement():
    """Candidate below requirement gets proportional score."""
    score = compute_experience_score(2.0, 5.0)
    assert 0.1 <= score < 0.9


def test_compute_experience_score_no_requirement():
    """No requirement specified gives neutral score."""
    score = compute_experience_score(5.0, None)
    assert score == 0.7


def test_compute_experience_score_unknown_candidate():
    """Unknown candidate experience gives low score."""
    score = compute_experience_score(None, 5.0)
    assert score == 0.3


def test_rank_candidates():
    """Test ranking sorts by overall_score descending."""
    results = [
        {"candidate_id": 1, "overall_score": 0.5},
        {"candidate_id": 2, "overall_score": 0.9},
        {"candidate_id": 3, "overall_score": 0.7},
    ]
    ranked = rank_candidates(results)
    assert ranked[0]["candidate_id"] == 2
    assert ranked[0]["rank"] == 1
    assert ranked[1]["candidate_id"] == 3
    assert ranked[1]["rank"] == 2
    assert ranked[2]["candidate_id"] == 1
    assert ranked[2]["rank"] == 3


def test_match_candidate_to_job():
    """Test full matching pipeline produces valid scores."""
    scores = match_candidate_to_job(
        resume_text=(
            "Experienced Python developer with 5 years of FastAPI"
            " and Django experience. Built scalable microservices."
        ),
        candidate_skills="Python, FastAPI, Django, Docker, AWS",
        candidate_experience_years=5.0,
        candidate_education="M.S. Computer Science",
        job_description="Looking for a senior Python developer to build APIs",
        job_requirements="5+ years Python, FastAPI, Docker required",
        job_preferred_skills="Kubernetes, Machine Learning",
        job_min_experience=5.0,
    )

    assert "overall_score" in scores
    assert "semantic_score" in scores
    assert "skills_score" in scores
    assert "experience_score" in scores
    assert "education_score" in scores

    # All scores should be between 0 and 1
    for key, value in scores.items():
        assert 0.0 <= value <= 1.0, f"{key} = {value} is out of range"

    # Overall should be reasonable for a good match
    assert scores["overall_score"] > 0.3
