"""AetherAI FastAPI application entry point."""

import os
import threading
import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.chat_routes import router as chat_router
from core.config import CHROMA_DIR, DOWNLOADS_DIR, PROJECT_ROOT, UPLOADS_DIR

for directory in (DOWNLOADS_DIR, UPLOADS_DIR, CHROMA_DIR):
    Path(directory).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AetherAI", version="1.0.0", description="Local-first AI assistant API")
allowed_origins = [origin.strip() for origin in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if origin.strip()]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware, allow_origins=allowed_origins, allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"],
    )

app.include_router(chat_router, prefix="/api")
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "frontend")), name="static")
app.mount("/", StaticFiles(directory=str(PROJECT_ROOT / "frontend"), html=True), name="frontend")


def open_ui_in_browser() -> None:
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    if os.getenv("AETHERAI_OPEN_BROWSER", "1").lower() not in {"0", "false", "no"}:
        threading.Timer(1.5, open_ui_in_browser).start()
    uvicorn.run("main:app", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")), reload=False)
