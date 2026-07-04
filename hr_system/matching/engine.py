"""AI-powered matching engine using TF-IDF and cosine similarity.

Designed to handle 10,000+ resumes per month efficiently without
requiring external API calls or GPU resources.
"""

import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class MatchResult:
    """Result of matching a resume against a job description."""

    overall_score: float
    skill_match_score: float
    experience_match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    notes: str


# Common technical skills for extraction
SKILL_PATTERNS = [
    "python", "java", "javascript", "typescript", "c\\+\\+", "c#", "ruby", "go", "rust",
    "swift", "kotlin", "php", "scala", "r\\b", "matlab",
    "react", "angular", "vue", "node\\.?js", "django", "flask", "fastapi", "spring",
    "express", "next\\.?js", "rails",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb",
    "cassandra", "sqlite",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd",
    "git", "linux", "nginx",
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
    "pytorch", "scikit-learn", "pandas", "numpy",
    "rest api", "graphql", "microservices", "agile", "scrum", "devops",
    "html", "css", "sass", "webpack", "babel",
    "data analysis", "data engineering", "etl", "spark", "hadoop", "airflow",
    "project management", "team leadership", "communication",
]


class MatchingEngine:
    """Matches resumes against job descriptions using TF-IDF similarity and skill extraction."""

    def __init__(self):
        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        self._skill_pattern = re.compile(
            r"\b(" + "|".join(SKILL_PATTERNS) + r")\b", re.IGNORECASE
        )

    def extract_skills(self, text: str) -> list[str]:
        """Extract technical skills from text."""
        matches = self._skill_pattern.findall(text.lower())
        return list(set(matches))

    def extract_experience_years(self, text: str) -> float | None:
        """Extract years of experience from resume text."""
        patterns = [
            r"(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)",
            r"experience[:\s]*(\d+)\+?\s*years?",
            r"(\d+)\+?\s*years?\s*(?:in|of|working)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def compute_match(self, resume_text: str, job_description: str, job_requirements: str) -> MatchResult:
        """Compute match score between a resume and job posting.

        Returns a MatchResult with scores from 0.0 to 1.0.
        """
        # Combine job description and requirements for matching
        job_text = f"{job_description} {job_requirements}"

        # TF-IDF cosine similarity for overall content match
        try:
            tfidf_matrix = self._vectorizer.fit_transform([job_text, resume_text])
            content_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except ValueError:
            content_similarity = 0.0

        # Skill-based matching
        job_skills = self.extract_skills(job_text)
        resume_skills = self.extract_skills(resume_text)

        if job_skills:
            matched_skills = [s for s in job_skills if s in resume_skills]
            missing_skills = [s for s in job_skills if s not in resume_skills]
            skill_score = len(matched_skills) / len(job_skills)
        else:
            matched_skills = []
            missing_skills = []
            skill_score = 0.5  # Neutral if no specific skills in job

        # Experience matching
        resume_years = self.extract_experience_years(resume_text)
        job_years = self.extract_experience_years(job_text)

        if resume_years is not None and job_years is not None:
            if resume_years >= job_years:
                experience_score = 1.0
            else:
                experience_score = resume_years / job_years
        elif resume_years is not None:
            experience_score = min(resume_years / 5.0, 1.0)  # Normalize to 5 years
        else:
            experience_score = 0.5  # Neutral if can't determine

        # Weighted overall score
        overall_score = (
            0.40 * content_similarity
            + 0.40 * skill_score
            + 0.20 * experience_score
        )

        # Generate notes
        notes_parts = []
        if matched_skills:
            notes_parts.append(f"Matched skills: {', '.join(matched_skills[:5])}")
        if missing_skills:
            notes_parts.append(f"Missing: {', '.join(missing_skills[:3])}")
        if resume_years is not None:
            notes_parts.append(f"Experience: {resume_years} years")

        return MatchResult(
            overall_score=round(float(overall_score), 4),
            skill_match_score=round(float(skill_score), 4),
            experience_match_score=round(float(experience_score), 4),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            notes="; ".join(notes_parts) if notes_parts else "No specific matches detected",
        )

    def rank_candidates(
        self,
        resumes: list[tuple[int, str]],
        job_description: str,
        job_requirements: str,
    ) -> list[tuple[int, MatchResult]]:
        """Rank multiple candidates against a job posting.

        Args:
            resumes: List of (candidate_id, resume_text) tuples.
            job_description: The job description text.
            job_requirements: The job requirements text.

        Returns:
            List of (candidate_id, MatchResult) sorted by overall_score descending.
        """
        results = []
        for candidate_id, resume_text in resumes:
            match_result = self.compute_match(resume_text, job_description, job_requirements)
            results.append((candidate_id, match_result))

        # Sort by overall score descending
        results.sort(key=lambda x: x[1].overall_score, reverse=True)
        return results
