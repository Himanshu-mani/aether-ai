import os
from fpdf import FPDF
import docx
from langchain.tools import tool
from core.config import DOWNLOADS_DIR
from core.rag_pipeline import query_documents

@tool
def search_uploaded_files(query: str) -> str:
    """Use this to search for information INSIDE the files uploaded by the user.
    Input should be the exact question you want to ask the documents."""
    try:
        # Fetches data directly from ChromaDB (rag_pipeline)
        return query_documents(query)
    except Exception as e:
        return f"Error searching files: {str(e)}"

@tool
def create_downloadable_file(filename: str, content: str) -> str:
    """Use this to create a file (PDF, CSV, TXT, DOCX, PY) with the generated content.
    Input MUST be filename (e.g., report.pdf, data.csv) and the full content.
    DO NOT output the content in the chat, ONLY provide the final download link."""
    
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOADS_DIR, filename)
    ext = filename.split('.')[-1].lower()
    
    try:
        if ext == 'pdf':
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            encoded_content = content.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, txt=encoded_content)
            pdf.output(file_path)
        elif ext == 'docx':
            doc = docx.Document()
            doc.add_paragraph(content)
            doc.save(file_path)
        else: # TXT, CSV, PY, JS
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        download_url = f"http://localhost:8000/downloads/{filename}"
        return f"File created successfully. Tell user EXACTLY: Your file is ready. Download it here: {download_url}"
        
    except Exception as e:
        return f"Error creating file: {str(e)}"
