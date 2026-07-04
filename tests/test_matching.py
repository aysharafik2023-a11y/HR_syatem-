"""Tests for the AI matching engine."""

from hr_system.matching.engine import MatchingEngine


class TestMatchingEngine:
    def setup_method(self):
        self.engine = MatchingEngine()

    def test_extract_skills_python(self):
        text = "Experienced in Python, Django, and PostgreSQL with Docker containers"
        skills = self.engine.extract_skills(text)
        assert "python" in skills
        assert "django" in skills
        assert "postgresql" in skills
        assert "docker" in skills

    def test_extract_skills_empty(self):
        text = "This text has no technical skills mentioned."
        skills = self.engine.extract_skills(text)
        assert len(skills) == 0

    def test_extract_experience_years(self):
        text = "I have 5 years of experience in software development"
        years = self.engine.extract_experience_years(text)
        assert years == 5.0

    def test_extract_experience_years_plus(self):
        text = "7+ years of experience with Python and Java"
        years = self.engine.extract_experience_years(text)
        assert years == 7.0

    def test_extract_experience_years_none(self):
        text = "Fresh graduate looking for entry-level position"
        years = self.engine.extract_experience_years(text)
        assert years is None

    def test_compute_match_high_score(self):
        resume = (
            "Senior Python developer with 8 years of experience. "
            "Expert in Django, FastAPI, PostgreSQL, Redis, Docker, AWS, "
            "microservices, CI/CD, Git, and agile methodologies."
        )
        job_desc = "Looking for a senior Python developer to build microservices."
        job_req = (
            "5+ years experience with Python, Django or FastAPI, "
            "PostgreSQL, Docker, AWS, and CI/CD pipelines."
        )

        result = self.engine.compute_match(resume, job_desc, job_req)
        assert result.overall_score > 0.5
        assert result.skill_match_score > 0.5
        assert len(result.matched_skills) > 0

    def test_compute_match_low_score(self):
        resume = "Marketing specialist with 3 years in social media management and SEO."
        job_desc = "Looking for a senior Python developer to build microservices."
        job_req = "5+ years experience with Python, Django, PostgreSQL, Docker."

        result = self.engine.compute_match(resume, job_desc, job_req)
        assert result.overall_score < 0.4
        assert len(result.missing_skills) > 0

    def test_rank_candidates(self):
        resumes = [
            (1, "Python developer with Django, FastAPI, PostgreSQL, 6 years experience"),
            (2, "Marketing manager with social media expertise, 10 years experience"),
            (3, "Junior developer learning Python and JavaScript, 1 year experience"),
        ]
        job_desc = "Senior Python backend developer needed"
        job_req = "5+ years Python experience, Django, PostgreSQL, Docker"

        results = self.engine.rank_candidates(resumes, job_desc, job_req)
        assert len(results) == 3
        # Python developer should rank highest
        assert results[0][0] == 1
        # Scores should be descending
        assert results[0][1].overall_score >= results[1][1].overall_score
        assert results[1][1].overall_score >= results[2][1].overall_score
