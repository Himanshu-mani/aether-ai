# AetherAI

A local-first agentic AI assistant that combines conversational AI, document retrieval, live web intelligence, and file generation in one workspace.

## Overview

AetherAI is designed as a practical AI workspace rather than a basic chatbot. It can route requests to the right capability, retrieve context from local documents, gather information from the live web, and generate downloadable files.

## Key Capabilities

- **Agentic routing** — classifies requests and selects direct chat, file operations, web retrieval, or generation workflows.
- **Local RAG** — ingests supported documents and retrieves relevant context using embeddings and ChromaDB.
- **Live web retrieval** — fetches and processes current webpage content with Crawl4AI.
- **Local LLM inference** — uses Ollama for local model execution.
- **File generation and processing** — supports practical document/data workflows through the file tools layer.
- **Web interface** — browser-based UI backed by FastAPI.
- **Container support** — includes a Dockerfile for reproducible setup.

## Architecture

```text
                    ┌─────────────────────┐
                    │   Browser Frontend   │
                    │ HTML / CSS / JS      │
                    └──────────┬──────────┘
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI API     │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │   Agent / Router    │
                    └──────┬──────┬───────┘
                           │      │
             ┌─────────────┘      └──────────────┐
             ▼                                   ▼
      ┌─────────────┐                     ┌─────────────┐
      │ Local RAG   │                     │ Live Web RAG │
      │ Embeddings  │                     │ Crawl4AI     │
      │ ChromaDB    │                     └─────────────┘
      └──────┬──────┘
             │
             ▼
      ┌─────────────┐
      │ Ollama LLM  │
      └─────────────┘

             ┌───────────────────┐
             │ File Operations   │
             │ / Generation      │
             └───────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| LLM Runtime | Ollama |
| LLM | Gemma (`gemma4:e4b`, configurable) |
| Embeddings | Nomic Embed Text |
| Vector Store | ChromaDB |
| Web Retrieval | Crawl4AI |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Docker |

## Project Structure

```text
.
├── agent/                 # Agent execution and prompting
├── api/                   # FastAPI routes
├── core/                  # Configuration, LLM setup, RAG pipeline
├── tools/                 # Web retrieval and file operations
├── frontend/              # Browser UI
├── workspace/             # Runtime data (ignored by Git)
├── Dockerfile
├── requirements.txt
├── main.py
├── .env.example
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Himanshu-mani/aether-ai.git
cd aether-ai
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and start Ollama

Install Ollama for your platform, then make sure the configured model is available locally.

```bash
ollama pull gemma4:e4b
ollama pull nomic-embed-text
```

### 5. Run the application

```bash
python main.py
```

Then open the local URL printed by the application in your browser.

## Configuration

Copy `.env.example` to `.env` and adjust the local model/runtime values when needed.

The project currently defaults to:

- Model: `gemma4:e4b`
- Embedding model: `nomic-embed-text`
- Ollama: `http://localhost:11434`

## Docker

A Dockerfile is included for containerized deployment. Local LLM serving is intentionally kept as a separate runtime concern so the application can connect to an Ollama instance.

## Design Goals

AetherAI focuses on four practical properties:

1. **Local-first** — keep model inference and vector data under the user's control.
2. **Tool-aware** — use the right tool for the task instead of treating every request as plain chat.
3. **Retrieval-grounded** — use relevant document or web context when a request requires external knowledge.
4. **Extensible** — keep routing, retrieval, tools, API, and frontend separated so new capabilities can be added without rewriting the whole application.

## Current Limitations

- Live web retrieval and local model execution require their respective local dependencies.
- Generated/runtime data is intentionally excluded from Git.
- Exact supported file types depend on the installed dependencies and tool implementation.

## Roadmap

- Add automated tests for routing, RAG retrieval, and file operations.
- Add observability for agent decisions and retrieval quality.
- Add authentication and multi-user workspace support.
- Improve evaluation with a benchmark set for routing and grounded answers.
- Add CI for linting, tests, and Docker builds.

## License

No license has been declared yet. Add a `LICENSE` file before distributing the project publicly under a specific open-source license.

---

Built as a practical exploration of local LLMs, agentic workflows, RAG, and tool-augmented AI systems.
