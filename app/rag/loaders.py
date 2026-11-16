"""Format-specific document loader selection."""
from pathlib import Path
from langchain_community.document_loaders import (
    CSVLoader, Docx2txtLoader, PyPDFLoader, TextLoader, UnstructuredExcelLoader,
)


def loader_for(path: Path):
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
    raise ValueError("Unsupported file type: " + (extension or "(no extension)"))
