"""Main FastAPI application."""

from fastapi import FastAPI

from hr_system.chatbot.routes import router as chatbot_router
from hr_system.database import init_db
from hr_system.policy_rag.routes import router as policy_router
from hr_system.recruitment.routes import router as recruitment_router

app = FastAPI(
    title="HR System",
    description="HR System with Recruitment, Policy Analysis (RAG), and Chatbot",
    version="0.1.0",
)

app.include_router(recruitment_router)
app.include_router(policy_router)
app.include_router(chatbot_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.1.0"}
