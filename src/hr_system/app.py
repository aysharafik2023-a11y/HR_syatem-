"""Main FastAPI application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from hr_system.chatbot.routes import router as chatbot_router
from hr_system.database import init_db
from hr_system.policy_rag.routes import router as policy_router
from hr_system.recruitment.routes import router as recruitment_router

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="HR System",
    description="HR System with Recruitment, Policy Analysis (RAG), and Chatbot",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recruitment_router)
app.include_router(policy_router)
app.include_router(chatbot_router)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
def serve_ui():
    return FileResponse(str(STATIC_DIR / "index.html"))
