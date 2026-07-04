"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, escalations, health, knowledge_base, responses, tickets
from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="AI-powered customer support platform for SaaS companies. "
        "Automatically classifies, prioritizes, and routes support tickets "
        "while assisting agents with AI-generated responses.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    api_prefix = settings.api_prefix
    app.include_router(health.router)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(tickets.router, prefix=api_prefix)
    app.include_router(responses.router, prefix=api_prefix)
    app.include_router(escalations.router, prefix=api_prefix)
    app.include_router(knowledge_base.router, prefix=api_prefix)

    @app.get("/")
    def root():
        return {
            "name": settings.app_name,
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    return app


app = create_app()
