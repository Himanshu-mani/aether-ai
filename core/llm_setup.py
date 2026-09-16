from langchain_ollama import ChatOllama, OllamaEmbeddings

from core.config import DEFAULT_NUM_CTX, MODEL_NAME, OLLAMA_BASE_URL
from core.resource_manager import infer_local_inference_profile, get_resource_snapshot


def get_llm():
    profile = infer_local_inference_profile(get_resource_snapshot())
    return ChatOllama(
        model=MODEL_NAME,
        base_url=OLLAMA_BASE_URL,
        temperature=0.0,
        num_ctx=profile.get("recommended_num_ctx", DEFAULT_NUM_CTX),
        streaming=True,
    )


def get_embeddings():
    return OllamaEmbeddings(
        model="nomic-embed-text",
        base_url=OLLAMA_BASE_URL,
    )
