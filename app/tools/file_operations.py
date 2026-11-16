"""Local document search and downloadable file creation tools."""
import re
from pathlib import Path
import docx
from fpdf import FPDF
from langchain_core.tools import tool
from app.core.config import ALLOWED_DOWNLOAD_EXTENSIONS, DOWNLOADS_DIR
from app.rag.retrieval import query_documents


def _safe_filename(filename: str) -> str:
    name = re.split(r"[/\\]", filename or "")[-1].strip()
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name).strip(" .")
    if not name or name in {".", ".."}:
        raise ValueError("A valid filename is required.")
    if Path(name).suffix.lower() not in ALLOWED_DOWNLOAD_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_DOWNLOAD_EXTENSIONS))
        raise ValueError("Unsupported output type. Allowed: " + allowed)
    return name[:180]


@tool
def search_uploaded_files(query: str) -> str:
    """Search text from documents uploaded to the local workspace."""
    return query_documents(query)


@tool
def create_downloadable_file(filename: str, content: str) -> str:
    """Create a downloadable PDF, DOCX, CSV, TXT, Markdown, JSON, or code file."""
    try:
        safe_name = _safe_filename(filename)
        DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        file_path = DOWNLOADS_DIR / safe_name
        extension = file_path.suffix.lower()
        if extension == ".pdf":
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 7, text=content.encode("latin-1", "replace").decode("latin-1"))
            pdf.output(str(file_path))
        elif extension == ".docx":
            document = docx.Document()
            for paragraph in content.splitlines() or [""]:
                document.add_paragraph(paragraph)
            document.save(str(file_path))
        else:
            file_path.write_text(content, encoding="utf-8", newline="")
        return f"File created successfully. Download it here: /downloads/{safe_name}"
    except Exception as exc:
        return f"Error creating file: {exc}"
