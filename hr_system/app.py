"""FastAPI application for the AI Resume Screening System."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session

from hr_system.database import get_db, init_db
from hr_system.models import Candidate, Job
from hr_system.routers import jobs, resumes, screening
from hr_system.schemas import HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize the database on application startup."""
    init_db()
    logger.info("Database initialized.")
    logger.info("AI Resume Screening System is ready.")
    yield


app = FastAPI(
    title="AI Resume Screening System",
    description=(
        "An AI-powered system that reads resumes, matches them to job descriptions, "
        "ranks candidates, and provides an API for HR portals. "
        "Processes 10,000+ resumes/month with semantic AI matching."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(screening.router)


@app.get("/", response_model=HealthResponse)
def health_check():
    """Health check endpoint with system stats."""
    db: Session = next(get_db())
    try:
        total_candidates = db.query(Candidate).count()
        total_jobs = db.query(Job).count()
    finally:
        db.close()

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        total_candidates=total_candidates,
        total_jobs=total_jobs,
    )
