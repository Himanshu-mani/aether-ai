# Gemma 2 Model Configuration Note

AetherAI defaults to gemma2:2b for chat and nomic-embed-text for document embeddings. These values are configurable through the MODEL_NAME, EMBEDDING_MODEL, and OLLAMA_BASE_URL environment variables.

## Local benchmark snapshot

A previously recorded run on 2026-10-23 used an NVIDIA GeForce RTX 2050 (4 GB VRAM) and the Ollama streaming API with a 256-token generation cap.

| Metric | Recorded value |
|---|---:|
| Time to first token (client-observed) | 2.461 s |
| Prompt tokens | 38 |
| Generated tokens | 256 |
| Generated words | 199 |
| Generation speed | 53.65 tokens/s |
| Ollama server total | 5.164 s |
| Client total | 7.239 s |

This is a single machine-specific observation, not a general performance guarantee. Since generation reached the 256-token cap, the output was truncated by the benchmark limit. Client TTFT includes overhead and is not a server-only latency measure.

## Verification status

The model and embedding names are configured in code. The benchmark is available at benchmarks/benchmark_inference.py. A previous local Ollama smoke test was recorded, but the full FastAPI chat and document-ingestion integration path must be tested in the target environment after installing dependencies and pulling both models.
