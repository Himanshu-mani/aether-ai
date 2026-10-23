"""Document ingestion and retrieval backed by ChromaDB."""

from pathlib import Path

from langchain_community.document_loaders import (
    CSVLoader, Docx2txtLoader, PyPDFLoader, TextLoader, UnstructuredExcelLoader,
)
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import CHROMA_DIR
from core.llm_setup import get_embeddings


def _loader_for(path: Path):
    extension = path.suffix.lower()
    if extension == ".pdf":
        return PyPDFLoader(str(path))
    if extension == ".docx":
        return Docx2txtLoader(str(path))
    if extension == ".csv":
        return CSVLoader(str(path), autodetect_encoding=True)
    if extension in {".xlsx", ".xls"}:
        return UnstructuredExcelLoader(str(path))
    if extension in {".txt", ".md", ".json", ".py"}:
        return TextLoader(str(path), encoding="utf-8", autodetect_encoding=True)
    raise ValueError(f"Unsupported file type: {extension or '(no extension)'}")


def process_and_store_document(file_path: str) -> str:
    """Load a supported file, split it, and append its chunks to the vector store."""
    path = Path(file_path)
    try:
        docs = _loader_for(path).load()
        if not docs or not any(doc.page_content.strip() for doc in docs):
            return "Error loading file: no readable text was found in this document."
        for doc in docs:
            doc.metadata.setdefault("source", path.name)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = splitter.split_documents(docs)
        if not splits:
            return "Error loading file: document did not contain any indexable text."
        store = Chroma(persist_directory=CHROMA_DIR, embedding_function=get_embeddings())
        store.add_documents(splits)
        return f"Success! Indexed {len(splits)} chunks from {path.name}."
    except Exception as exc:
        return f"Error processing file: {exc}"


def query_documents(query: str, k: int = 3) -> str:
    """Return the most relevant document chunks, or a clear empty-state message."""
    if not Path(CHROMA_DIR).exists() or not any(item.name != ".gitkeep" for item in Path(CHROMA_DIR).iterdir()):
        return "No documents have been indexed yet. Upload a file first."
    try:
        store = Chroma(persist_directory=CHROMA_DIR, embedding_function=get_embeddings())
        results = store.similarity_search(query, k=max(1, min(int(k), 10)))
    except Exception as exc:
        return f"Document search failed: {exc}"
    if not results:
        return "No relevant text was found in the indexed documents."
    return "\n\n---\n\n".join(
        f"Source: {doc.metadata.get('source', 'uploaded document')}\n{doc.page_content}"
        for doc in results
    )
