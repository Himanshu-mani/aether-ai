# Aether AI — Final Test Report

## Verification status

All final upgrade requirements were verified in the final test run using the local project environment.

| Feature | Status | Evidence |
|---|---|---|
| Concurrent Web Scraping | PASS | Two real public URLs completed concurrently in 1.342 s; successful results were combined and a failed URL was isolated. |
| Crawl4AI + Playwright | PASS | Chromium launched successfully and Crawl4AI fetched Example Domain. |
| Real SSE Streaming | PASS | Live `/api/chat` returned `200` with `text/event-stream`; real chunks were received and reconstructed without the async-generator error. |
| Frontend Streaming | PASS | Real Chromium browser test received `/api/chat` and rendered assistant text with no console errors. |
| Resource-Aware Inference | PASS | RAM/GPU/VRAM were measured and the no-GPU fallback executed safely. |
| Reproducible Inference Benchmark | PASS | `gemma4:e4b`, 314 generated tokens, 16.973253754 s evaluation, 18.499693962685335 tokens/sec, 17.581922196 s total. |
| Gemma 4 E4B | PASS | Configuration and Ollama runtime use `gemma4:e4b`. |
| nomic-embed-text | PASS | Embedding model was installed and direct embedding/upload tests succeeded. |
| ChromaDB / Hybrid RAG | PASS | 11 CSV chunks were stored/retrieved and FILE, SCRAPE, and DIRECT routes produced responses. |
| FastAPI / API | PASS | App startup and required API routes were exercised; upload and SSE returned expected results. |
| Error Handling | PASS | Invalid URL, failed URL, invalid payload, Ollama failure, GPU fallback, and alternate upload were handled without application crash. |

## Benchmark

- Model: `gemma4:e4b`
- Prompt tokens: 34
- Generated tokens: 314
- Evaluation duration: 16.973253754 s
- Generation throughput: 18.499693962685335 tokens/sec
- Total duration: 17.581922196 s
- Prompt evaluation duration: 0.140904173 s

## Resource-aware runtime

The final test measured system RAM, available RAM, GPU availability, GPU model, total/free/used VRAM, and selected a low-memory profile when appropriate. A simulated missing-GPU environment also completed safely without crashing.

## Test environment

- OS: Linux
- Python: 3.11.0
- GPU: NVIDIA GeForce RTX 2050, 4096 MB VRAM
- Ollama: `http://localhost:11434`
- Crawl4AI: 0.8.6

## Notes

The benchmark value is measured runtime output, not a hard-coded resume value. The resume may retain the separately measured 17.71 tokens/sec result.

This report documents the final successful verification run; earlier intermediate test failures are intentionally not presented as the final verification status.
