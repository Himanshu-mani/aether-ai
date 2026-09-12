import os
# Loaders for reading different types of files
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, CSVLoader, UnstructuredExcelLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from core.llm_setup import get_embeddings
from core.config import CHROMA_DIR

def process_and_store_document(file_path: str):
    """Reads the file, splits it into chunks, and saves it to ChromaDB."""
    ext = file_path.split('.')[-1].lower()
    
    # Select the appropriate loader based on the file extension
    if ext == 'pdf':
        loader = PyPDFLoader(file_path)
    elif ext == 'docx':
        loader = Docx2txtLoader(file_path)
    elif ext == 'csv':
        loader = CSVLoader(file_path)
    elif ext in ['xlsx', 'xls']:
        loader = UnstructuredExcelLoader(file_path)
    else: # txt, py, md, json etc.
        loader = TextLoader(file_path, encoding='utf-8')
        
    try:
        docs = loader.load()
    except Exception as e:
        return f"Error loading file: {e}"

    # Chunking: Split large files into 1000 character chunks to prevent LLM overload
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # Save to ChromaDB using Nomic-embed-text
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=CHROMA_DIR)
    
    return f"Success! Created {len(splits)} chunks of the file and saved them to memory."

def query_documents(query: str, k: int = 3):
    """Searches ChromaDB to retrieve the most relevant text."""
    if not os.path.exists(CHROMA_DIR):
        return "Memory is empty. Please upload a file first."
        
    embeddings = get_embeddings()
    vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    
    # Retrieves the top 3 chunks matching the question
    results = vectorstore.similarity_search(query, k=k)
    
    if not results:
        return "The answer to this question was not found in the file."
        
    context = "\n\n".join([doc.page_content for doc in results])
    return context