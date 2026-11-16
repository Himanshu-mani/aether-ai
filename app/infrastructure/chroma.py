"""ChromaDB vector-store adapter."""
from langchain_community.vectorstores import Chroma
from app.core.config import CHROMA_DIR
from app.llms.factory import get_embeddings


def get_vector_store() -> Chroma:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma(persist_directory=str(CHROMA_DIR), embedding_function=get_embeddings())
