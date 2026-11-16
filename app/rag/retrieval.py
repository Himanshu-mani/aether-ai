"""Semantic retrieval over indexed user documents."""
from app.core.config import CHROMA_DIR
from app.infrastructure.chroma import get_vector_store


def query_documents(query: str, k: int = 3) -> str:
    if not CHROMA_DIR.exists() or not any(item.name != ".gitkeep" for item in CHROMA_DIR.iterdir()):
        return "No documents have been indexed yet. Upload a file first."
    try:
        results = get_vector_store().similarity_search(query, k=max(1, min(int(k), 10)))
    except Exception as exc:
        return f"Document search failed: {exc}"
    if not results:
        return "No relevant text was found in the indexed documents."
    sections = []
    for document in results:
        source = document.metadata.get("source", "uploaded document")
        sections.append(f"Source: {source}\n{document.page_content}")
    return "\n\n---\n\n".join(sections)
