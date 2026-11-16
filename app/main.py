"""FastAPI application factory and runtime entry point."""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.core.config import CHROMA_DIR, DOWNLOADS_DIR, PROJECT_ROOT, UPLOADS_DIR


def create_app() -> FastAPI:
    for directory in (DOWNLOADS_DIR, UPLOADS_DIR, CHROMA_DIR):
        Path(directory).mkdir(parents=True, exist_ok=True)

    application = FastAPI(
        title="AetherAI",
        version="1.1.0",
        description="Local-first AI assistant API",
    )
    allowed_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if allowed_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
        )

    application.include_router(chat_router, prefix="/api")
    application.include_router(documents_router, prefix="/api")
    application.mount("/downloads", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")
    application.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend")), name="static")
    application.mount("/", StaticFiles(directory=str(PROJECT_ROOT / "frontend"), html=True), name="frontend")
    return application


app = create_app()
