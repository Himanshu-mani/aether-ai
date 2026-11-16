"""Document loading, chunking, and vector-store ingestion."""
from pathlib import Path
from app.infrastructure.chroma import get_vector_store
from app.rag.chunking import split_documents
from app.rag.loaders import loader_for


def process_and_store_document(file_path: str) -> str:
    path = Path(file_path)
    try:
        documents = loader_for(path).load()
        if not documents or not any(document.page_content.strip() for document in documents):
            return "Error loading file: no readable text was found in this document."
        for document in documents:
            document.metadata.setdefault("source", path.name)
        chunks = split_documents(documents)
        if not chunks:
            return "Error loading file: document did not contain any indexable text."
        get_vector_store().add_documents(chunks)
        return f"Success! Indexed {len(chunks)} chunks from {path.name}."
    except Exception as exc:
        return f"Error processing file: {exc}"
