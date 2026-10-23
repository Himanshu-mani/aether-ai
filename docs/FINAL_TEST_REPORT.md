# Aether AI — Final Test Report

## Verification status

The following application features were verified in the earlier full test run. The additional Gemma 2:2B inference measurement below is a separate benchmark run and does not replace those feature tests.

| Feature | Status | Evidence |
|---|---|---|
| Concurrent Web Scraping | PASS | Two real public URLs completed concurrently in 1.342 s; successful results were combined and a failed URL was isolated. |
| Crawl4AI + Playwright | PASS | Chromium launched successfully and Crawl4AI fetched Example Domain. |
| Real SSE Streaming | PASS | Live /api/chat returned 200 with text/event-stream; real chunks were received and reconstructed without the async-generator error. |
| Frontend Streaming | PASS | Real Chromium browser test received /api/chat and rendered assistant text with no console errors. |
| Resource-Aware Inference | PASS | RAM/GPU/VRAM were measured and the no-GPU fallback executed safely. |
| Reproducible Inference Benchmark (Gemma 4 E4B baseline) | PASS | Earlier measured baseline: 314 generated tokens, 16.9733 s evaluation, 18.50 tokens/sec, 17.5819 s total. |
| Gemma 4 E4B baseline | PASS | Earlier test configuration and Ollama runtime used gemma4:e4b. |
| nomic-embed-text | PASS | Embedding model was installed and direct embedding/upload tests succeeded. |
| ChromaDB / Hybrid RAG | PASS | 11 CSV chunks were stored/retrieved and FILE, SCRAPE, and DIRECT routes produced responses. |
| FastAPI / API | PASS | App startup and required API routes were exercised; upload and SSE returned expected results. |
| Error Handling | PASS | Invalid URL, failed URL, invalid payload, Ollama failure, GPU fallback, and alternate upload were handled without application crash. |

## Latest inference benchmark — Gemma 2:2B

Measured on 2026-10-23 using the streaming benchmark script and Ollama.

| Metric | Result |
|---|---:|
| Model | gemma2:2b |
| Prompt tokens | 38 |
| Generated tokens | 256 (configured output cap reached) |
| Generated words | 199 |
| Time to first non-empty streaming chunk (client-measured TTFT) | 2.4607 s (2460.74 ms) |
| Prompt evaluation duration | 0.3641 s |
| Generation duration | 4.7714 s |
| Generation throughput | 53.65 tokens/sec |
| Ollama server total duration | 5.1636 s |
| Client total duration | 7.2391 s |
| GPU placement | 100% GPU reported by ollama ps |
| GPU | NVIDIA GeForce RTX 2050 |
| Total VRAM | 4096 MB |
| Reported used / free VRAM | 2135 MB / 1830 MB |

### Interpretation and caveats

- TTFT is measured from the start of the client request until the first non-empty streaming response chunk. It includes request and model-startup overhead; it is not a pure GPU-compute latency.
- Ollama reported 100% GPU for the loaded gemma2:2b model in this run.
- The benchmark requested at most 256 generated tokens and the model reached that cap. The captured answer therefore ends mid-response; this is a benchmark output limit, not evidence that a normal chat response will always be truncated.
- Client total time includes streaming/request overhead and is expected to exceed Ollama's server-reported total duration.

## Earlier Gemma 4 E4B baseline

- Prompt tokens: 34
- Generated tokens: 314
- Evaluation duration: 16.9733 s
- Generation throughput: 18.50 tokens/sec
- Total duration: 17.5819 s
- Prompt evaluation duration: 0.1409 s

The Gemma 4 E4B baseline and Gemma 2:2B measurement are separate runs using different prompts and output lengths; compare them as measured runs, not as a controlled apples-to-apples model evaluation.

## Resource-aware runtime

The earlier full test measured system RAM, available RAM, GPU availability, GPU model, total/free/used VRAM, and selected a low-memory profile when appropriate. A simulated missing-GPU environment also completed safely without crashing.

## Test environment

- OS reported by resource summary: Linux
- GPU: NVIDIA GeForce RTX 2050, 4096 MB VRAM
- Ollama endpoint: http://localhost:11434
- Embedding model: nomic-embed-text
- Crawl4AI: 0.8.6

## Notes

Benchmark values are measured runtime output, not hard-coded performance claims. Repeat benchmarks with the same model, prompt, output cap, and runtime conditions for meaningful comparisons.
