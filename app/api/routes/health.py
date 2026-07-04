"""Health and monitoring endpoints."""

import time
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db

router = APIRouter(tags=["Health & Monitoring"])

START_TIME = time.time()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    settings = get_settings()

    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now(UTC).isoformat(),
        "environment": settings.app_env,
        "components": {
            "database": db_status,
            "api": "healthy",
        },
    }


@router.get("/metrics")
def metrics():
    uptime = time.time() - START_TIME
    return {
        "uptime_seconds": round(uptime, 2),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0",
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not ready"}, 503
