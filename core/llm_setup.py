"""Factories for the configured Ollama chat and embedding models."""

from langchain_ollama import ChatOllama, OllamaEmbeddings

from core.config import DEFAULT_NUM_CTX, EMBEDDING_MODEL, MODEL_NAME, OLLAMA_BASE_URL
from core.resource_manager import get_resource_snapshot, infer_local_inference_profile


def get_llm() -> ChatOllama:
    profile = infer_local_inference_profile(get_resource_snapshot())
    return ChatOllama(
        model=MODEL_NAME,
        base_url=OLLAMA_BASE_URL,
        temperature=0.0,
        num_ctx=profile.get("recommended_num_ctx", DEFAULT_NUM_CTX),
        streaming=True,
    )


def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
