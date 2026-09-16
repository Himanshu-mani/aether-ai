# AetherAI — Local-First Hybrid RAG AI Agent

AetherAI is a local-first agentic AI assistant that combines conversational AI, document retrieval, live web intelligence, streaming responses, resource-aware local inference, and file generation in one workspace.

## Overview

AetherAI is designed as a practical AI workspace rather than a basic chatbot. It routes each request to the appropriate workflow, retrieves context from local documents when needed, gathers live webpage content for current-information queries, and can generate downloadable files.

The application runs its LLM and embedding workloads locally through Ollama and uses ChromaDB for local vector storage.

## Key Capabilities

- **Agentic routing** — classifies requests into `DIRECT`, `FILE`, `SCRAPE`, or `GENERATE` workflows.
- **Local RAG** — ingests PDF, DOCX, CSV, XLSX, XLS, TXT, Markdown, JSON, Python, and other text-based files, splits them into chunks, embeds them, and stores them in ChromaDB.
- **Live web retrieval** — uses Crawl4AI with Playwright/Chromium to crawl webpage content.
- **Concurrent web retrieval** — supports multiple target URLs concurrently while isolating individual scrape failures.
- **Local LLM inference** — uses Ollama with `gemma4:e4b` as the configured chat model.
- **Local embeddings** — uses `nomic-embed-text` through Ollama for document retrieval.
- **SSE response streaming** — `/api/chat` streams generated response chunks to the browser using Server-Sent Events.
- **Resource-aware inference** — probes available system RAM and NVIDIA GPU/VRAM information and adjusts local context/concurrency settings for constrained machines. It falls back safely when GPU/system information is unavailable.
- **File generation** — can create downloadable PDF, DOCX, CSV, TXT, and code/text files through the file-operations layer.
- **Browser UI** — lightweight HTML/CSS/JavaScript frontend served directly by FastAPI.

## Architecture

```text
                         ┌──────────────────────┐
                         │    Browser UI         │
                         │  HTML / CSS / JS      │
                         └──────────┬───────────┘
                                    │ HTTP + SSE
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API      │
                         │  /api/chat /upload    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Agent / Router     │
                         │ DIRECT / FILE /       │
                         │ SCRAPE / GENERATE     │
                         └──────┬───────┬────────┘
                                │       │
                    ┌───────────┘       └──────────────┐
                    ▼                                  ▼
             ┌──────────────┐                  ┌──────────────┐
             │  Local RAG   │                  │  Live Web RAG │
             │ ChromaDB     │                  │ Crawl4AI      │
             │ Nomic Embed  │                  │ Playwright    │
             └──────┬───────┘                  │ Chromium      │
                    │                          └──────────────┘
                    └──────────────┬───────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │    Ollama Runtime    │
                         │     gemma4:e4b       │
                         └──────────────────────┘

                         ┌──────────────────────┐
                         │  File Operations     │
                         │  PDF / DOCX / CSV    │
                         │  TXT / code files    │
                         └──────────────────────┘

                         ┌──────────────────────┐
                         │ Resource Manager     │
                         │ RAM / GPU / VRAM     │
                         │ Context / Concurrency│
                         └──────────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Backend | FastAPI, Uvicorn |
| Agent Framework | LangChain |
| LLM Runtime | Ollama |
| Chat Model | `gemma4:e4b` |
| Embeddings | `nomic-embed-text` |
| Vector Store | ChromaDB |
| RAG | LangChain document loaders + text splitters |
| Web Retrieval | Crawl4AI |
| Browser Automation | Playwright + Chromium |
| File Processing | PyPDF, python-docx, docx2txt, Unstructured, pandas, openpyxl, xlrd |
| Frontend | HTML, CSS, JavaScript |
| API Streaming | Server-Sent Events (SSE) |
| Deployment | Dockerfile |

## Project Structure

The repository currently contains the application code, runtime configuration, verification documentation, and benchmark tooling. Runtime workspace data is kept out of Git except for empty `.gitkeep` files.

```text
.
├── agent/
│   ├── executor.py              # Routing, retrieval orchestration, response streaming
│   └── prompt.py                # Agent prompting
├── api/
│   └── chat_routes.py           # Chat SSE and file-upload API routes
├── benchmarks/
│   └── benchmark_inference.py   # Runtime Ollama throughput benchmark
├── core/
│   ├── config.py                # Runtime/model/workspace configuration
│   ├── llm_setup.py             # Ollama LLM and embedding setup
│   ├── rag_pipeline.py          # File ingestion, chunking and ChromaDB retrieval
│   └── resource_manager.py      # RAM/GPU/VRAM-aware runtime tuning
├── tools/
│   ├── live_web_rag.py          # Crawl4AI web retrieval
│   └── universal_file_ops.py    # File search and downloadable file generation
├── frontend/
│   ├── index.html               # Browser interface
│   ├── script.js                # UI, upload and SSE client
│   └── style.css                # UI styling
├── docs/
│   ├── FINAL_TEST_REPORT.md     # Verified test results
│   ├── VERIFICATION_NOTE.md     # Verification note
│   └── README_TEST_LINK.txt     # Test-report reference
├── workspace/                   # Runtime uploads/downloads/vector DB (ignored)
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── main.py
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Himanshu-mani/aether-ai.git
cd aether-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install the browser required by Crawl4AI

Playwright is included in `requirements.txt`. Chromium is a separate browser runtime and must be installed once:

```bash
playwright install chromium
```

### 5. Install and start Ollama

Install Ollama for your platform and make sure the local Ollama service is running.

Pull the configured chat and embedding models:

```bash
ollama pull gemma4:e4b
ollama pull nomic-embed-text
```

### 6. Run AetherAI

```bash
python main.py
```

The application starts the FastAPI server on port `8000` and attempts to open the browser automatically. If it does not open, visit:

```text
http://127.0.0.1:8000
```

## Configuration

The repository includes `.env.example` with the local Ollama configuration. The current application defaults are:

```text
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=gemma4:e4b
EMBEDDING_MODEL=nomic-embed-text
```

Runtime workspace paths are created automatically under `workspace/` for uploads, downloads, and ChromaDB storage.

## Web Retrieval

For live web queries, AetherAI uses Crawl4AI with a headless Chromium browser through Playwright.

The agent can:

- extract URLs from a query;
- retrieve multiple URLs concurrently;
- preserve successful results when one URL fails; and
- pass the retrieved webpage context to the local LLM.

Required browser setup:

```bash
playwright install chromium
```

## Local RAG

Uploaded documents are processed through the RAG pipeline:

```text
File upload
    ↓
Document loader
    ↓
Recursive text splitting
    ↓
Nomic embeddings
    ↓
ChromaDB
    ↓
Similarity search
    ↓
Retrieved context → Gemma 4 E4B
```

Supported loaders currently cover:

- PDF
- DOCX
- CSV
- XLSX
- XLS
- TXT
- Markdown
- JSON
- Python and other UTF-8 text/code files

## Streaming

The `/api/chat` endpoint uses **Server-Sent Events (SSE)**. The backend yields response chunks from the Ollama/LangChain async stream, while the frontend reads the event stream and progressively renders the assistant response.

## Resource-Aware Local Inference

`core/resource_manager.py` checks available Linux system memory and NVIDIA GPU/VRAM information when available. It uses this information to select a conservative local inference profile, including context size and web-scraping concurrency.

The implementation is designed to fail safely when NVIDIA tooling or system statistics are unavailable. It does **not** claim hardware-level GPU/RAM isolation.

## Benchmarking

The runtime benchmark is available at:

```text
benchmarks/benchmark_inference.py
```

Run it with:

```bash
python benchmarks/benchmark_inference.py
```

The benchmark reads the current Ollama generation metadata and calculates observed generation throughput rather than using a hardcoded performance value.

## Docker

A Dockerfile is included for containerized application setup. Ollama remains a separate runtime service because the project is designed around local Ollama inference.

For browser-based web retrieval in a container, the Playwright Chromium runtime also needs to be available in that container environment.

## Runtime Data and Git

The `workspace/` directory is used for runtime data such as:

- uploaded files;
- generated downloads; and
- the local ChromaDB store.

User/runtime data is ignored by Git so test documents, generated files, and vector-store contents are not committed to the repository.

## Verification

The project includes a final verification report covering the main application paths, including:

- FastAPI endpoints;
- real SSE streaming;
- Crawl4AI + Playwright/Chromium web crawling;
- concurrent web retrieval;
- document embeddings and ChromaDB retrieval;
- hybrid routing for direct, file, and web workflows;
- frontend behavior;
- error handling and no-GPU fallback; and
- runtime inference benchmarking.

See [`docs/FINAL_TEST_REPORT.md`](docs/FINAL_TEST_REPORT.md) for the recorded verification results.

## Design Goals

1. **Local-first** — keep model inference and vector data under the user's control.
2. **Tool-aware** — route requests to the appropriate retrieval or generation workflow.
3. **Retrieval-grounded** — use document or web context when a request requires it.
4. **Resource-aware** — adapt local runtime settings to available machine resources.
5. **Extensible** — keep routing, retrieval, tools, API, benchmarking, and frontend concerns separated.

## Current Limitations

- Ollama and the configured local models must be available for AI inference.
- Chromium must be installed for live browser-based web retrieval.
- Runtime data is intentionally excluded from Git.
- Docker does not bundle the Ollama model itself.
- Authentication and multi-user workspace isolation are not currently implemented.

## License

No license has been declared yet. Add a `LICENSE` file before distributing the project publicly under a specific open-source license.

---

Built as a practical exploration of local LLMs, agentic workflows, RAG, concurrent web retrieval, streaming responses, and resource-aware AI systems.
