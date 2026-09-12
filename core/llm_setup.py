from langchain_ollama import ChatOllama, OllamaEmbeddings
from core.config import OLLAMA_BASE_URL, MODEL_NAME

def get_llm():
    return ChatOllama(
        model=MODEL_NAME, 
        base_url=OLLAMA_BASE_URL, 
        temperature=0.0  
    )

def get_embeddings():
    return OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=OLLAMA_BASE_URL
    )
