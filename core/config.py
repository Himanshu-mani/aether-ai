import os

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "gemma4:e4b"  # 🧠 True Agentic routing with better model
EMBEDDING_MODEL = "nomic-embed-text" # Essential for RAG pipeline

# Workspace paths (Files will be saved/uploaded/stored here)
DOWNLOADS_DIR = os.path.join(os.getcwd(), "workspace", "downloads")
UPLOADS_DIR = os.path.join(os.getcwd(), "workspace", "uploads")
CHROMA_DIR = os.path.join(os.getcwd(), "workspace", "chromadb_store") # AI memory will be saved here
