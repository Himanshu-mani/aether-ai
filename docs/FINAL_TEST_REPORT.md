# AetherAI — Verification and Benchmark Report
## Historical Gemma 2:2B inference snapshot

A previously recorded run on 2026-10-23 used the Ollama streaming generation API and a 256-token generation cap. It is retained here as historical benchmark evidence; it is not a test of every revised application path.

| Metric | Recorded value |
|---|---:|
| Model | gemma2:2b |
| Prompt tokens | 38 |
| Generated tokens | 256 (configured output cap reached) |
| Generated words | 199 |
| Client-measured time to first non-empty chunk | 2.4607 s (2460.74 ms) |
| Prompt evaluation duration | 0.3641 s |
| Generation duration | 4.7714 s |
| Generation throughput | 53.65 tokens/s |
| Ollama server total duration | 5.1636 s |
| Client total duration | 7.2391 s |
| GPU placement reported by ollama ps | 100% GPU |
| GPU | NVIDIA GeForce RTX 2050 |
| Total VRAM | 4096 MB |
| Reported used / free VRAM | 2135 MB / 1830 MB |

## Interpretation and limitations

- The model reached the 256-token generation cap, so the benchmark output ended mid-response.
- Client-measured time to first token includes request and client overhead; it is not a pure model-compute latency.
- Hardware results are machine-specific and are not general performance guarantees.
- Earlier integration checks were recorded before the current code review. Re-run integration tests against this revision before claiming the entire application passes end-to-end.

## Running checks locally

    python -m unittest discover -s tests -v
    python -m compileall -q main.py agent api core tools benchmarks tests
    node --check frontend/script.js

For the full feature path, install requirements.txt, install Playwright Chromium, pull gemma2:2b and nomic-embed-text in Ollama, then run the app and test chat, upload/retrieval, web retrieval, and file generation separately.
