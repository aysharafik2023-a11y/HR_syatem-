"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hr_system.api import jobs, resumes, screening
from hr_system.config import settings
from hr_system.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on application startup."""
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered resume screening system that reads resumes, matches them to "
        "job descriptions, ranks candidates, and provides an API for HR portals. "
        "Designed to handle 10,000+ resumes per month."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for HR portal integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(screening.router, prefix="/api/v1")


@app.get("/")
def root():
    """Health check and API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "jobs": "/api/v1/jobs",
            "resumes": "/api/v1/resumes",
            "screening": "/api/v1/screening",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}
