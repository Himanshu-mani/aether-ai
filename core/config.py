import os

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "gemma4:e4b"
EMBEDDING_MODEL = "nomic-embed-text"

# Resource-aware defaults for local inference on constrained machines.
DEFAULT_NUM_CTX = 4096
MAX_WEB_SCRAPE_CONCURRENCY = 4

# Workspace paths (Files will be saved/uploaded/stored here)
DOWNLOADS_DIR = os.path.join(os.getcwd(), "workspace", "downloads")
UPLOADS_DIR = os.path.join(os.getcwd(), "workspace", "uploads")
CHROMA_DIR = os.path.join(os.getcwd(), "workspace", "chromadb_store")
