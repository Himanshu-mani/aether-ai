# AetherAI — Local-First AI Assistant

AetherAI is a local-first AI workspace built with FastAPI, Ollama, LangChain, and ChromaDB. It supports streamed chat, retrieval over uploaded documents, public-web retrieval, and downloadable file generation. The chat model defaults to gemma2:2b; document embeddings default to nomic-embed-text.

## Features

- Local chat: Ollama-powered responses streamed to the browser over Server-Sent Events.
- Document RAG: PDF, DOCX, CSV, XLSX, XLS, TXT, Markdown, JSON, and Python file ingestion.
- Web retrieval: Crawl4AI and Playwright extraction from public HTTP(S) pages. Local/private URL targets are rejected.
- Downloadable files: PDF, DOCX, CSV, TXT, Markdown, JSON, and code files.
- Resource-aware defaults based on available RAM and NVIDIA VRAM when detectable.
- Lightweight browser UI served by FastAPI.

## Requirements

- Python 3.11 recommended.
- Ollama running locally.
- gemma2:2b and nomic-embed-text pulled in Ollama.
- Chromium installed for Playwright/Crawl4AI web retrieval.

## Setup on Windows PowerShell

    git clone https://github.com/Himanshu-mani/aether-ai.git
    cd aether-ai
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    playwright install chromium
    ollama pull gemma2:2b
    ollama pull nomic-embed-text
    python main.py

## Setup on Linux/macOS

    git clone https://github.com/Himanshu-mani/aether-ai.git
    cd aether-ai
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    playwright install chromium
    ollama pull gemma2:2b
    ollama pull nomic-embed-text
    python main.py

Open http://127.0.0.1:8000 if the browser does not open automatically. Ollama must be running before chatting or indexing files.

## Configuration

Copy .env.example to .env and adjust values. The application loads .env from the project root; shell/container environment variables take precedence.

| Variable | Default | Purpose |
|---|---|---|
| OLLAMA_BASE_URL | http://localhost:11434 | Ollama API base URL |
| MODEL_NAME | gemma2:2b | Chat model |
| EMBEDDING_MODEL | nomic-embed-text | Embedding model |
| DEFAULT_NUM_CTX | 4096 | Fallback context window |
| MAX_WEB_SCRAPE_CONCURRENCY | 2 | Maximum concurrent retrieval tasks |
| MAX_UPLOAD_MB | 20 | Maximum upload size |
| HOST | 127.0.0.1 | API bind address; Docker sets 0.0.0.0 |
| PORT | 8000 | API port |
| AETHERAI_OPEN_BROWSER | 1 | Set 0 to disable browser launch |
| CORS_ALLOW_ORIGINS | unset | Optional comma-separated origins for a separately hosted frontend |

## API

- POST /api/chat — JSON body with a message field; returns an SSE stream with chunk, done, or error events.
- POST /api/upload — multipart form with a file field; indexes a supported document.
- /downloads/<filename> — serves generated downloadable files.

Uploads are restricted to supported extensions and 20 MiB by default. Runtime uploads, downloads, and ChromaDB data live under workspace/ and are excluded from Git.

## Checks

    python -m unittest discover -s tests -v
    python -m compileall -q main.py agent api core tools benchmarks tests
    node --check frontend/script.js

These checks do not require Ollama. End-to-end chat, embeddings, file indexing, web retrieval, and file generation require dependencies, models, and Playwright Chromium to be installed and available. Do not mark integration checks as passed unless they have actually run.

## Docker

    docker build -t aetherai .
    docker run --rm -p 8000:8000 -e OLLAMA_BASE_URL=http://host.docker.internal:11434 -v aetherai-workspace:/app/workspace aetherai

The container includes Chromium. Ollama runs outside the container in this example; configure the host address appropriately for your platform.

## Project layout

- agent/: request routing and response streaming
- api/: FastAPI chat and upload routes
- benchmarks/: Ollama inference benchmark
- core/: configuration, LLM setup, RAG, and resource detection
- docs/: model and verification notes
- frontend/: browser UI
- tests/: unit tests
- tools/: web retrieval and file operations
- workspace/: runtime data, excluded from Git
- main.py: application entry point

## Known limitations

- A running Ollama server and configured models are required for AI features.
- PDF output uses a built-in Latin-1 font and may replace unsupported Unicode glyphs.
- Web retrieval may fail on inaccessible or bot-protected sites.
- Resource detection is best-effort; hardware allocation is controlled by Ollama and the runtime.
