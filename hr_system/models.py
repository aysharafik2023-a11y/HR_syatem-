"""SQLAlchemy database models."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hr_system.database import Base


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    SCREENED = "screened"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    INTERVIEW = "interview"


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    preferred_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    applications: Mapped[list["Application"]] = relationship(back_populates="job_posting")


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resume_text: Mapped[str] = mapped_column(Text, nullable=False)
    resume_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    education: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    applications: Mapped[list["Application"]] = relationship(back_populates="candidate")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    job_posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id"), nullable=False)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    skill_match_score: Mapped[float] = mapped_column(Float, default=0.0)
    experience_match_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.PENDING
    )
    screening_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    screened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    candidate: Mapped["Candidate"] = relationship(back_populates="applications")
    job_posting: Mapped["JobPosting"] = relationship(back_populates="applications")
