"""Central application configuration and paths."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma2:2b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
DEFAULT_NUM_CTX = int(os.getenv("DEFAULT_NUM_CTX", "4096"))
MAX_WEB_SCRAPE_CONCURRENCY = max(1, int(os.getenv("MAX_WEB_SCRAPE_CONCURRENCY", "2")))
MAX_UPLOAD_BYTES = max(1, int(os.getenv("MAX_UPLOAD_MB", "20"))) * 1024 * 1024
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
DOWNLOADS_DIR = str(WORKSPACE_DIR / "downloads")
UPLOADS_DIR = str(WORKSPACE_DIR / "uploads")
CHROMA_DIR = str(WORKSPACE_DIR / "chromadb_store")
ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".docx", ".csv", ".xlsx", ".xls", ".txt", ".md", ".json", ".py"}
ALLOWED_DOWNLOAD_EXTENSIONS = {".pdf", ".docx", ".csv", ".txt", ".md", ".json", ".py", ".js", ".html"}
