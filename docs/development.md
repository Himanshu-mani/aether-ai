# Development Guide

## Environment

- Python 3.11
- Ollama running locally
- Chat model configured by `MODEL_NAME` (default: `gemma2:2b`)
- Embedding model configured by `EMBEDDING_MODEL` (default: `nomic-embed-text`)
- Playwright Chromium for Live Web

## Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
ollama pull gemma2:2b
ollama pull nomic-embed-text
```

## Run

```bash
python main.py
```

## Checks

```bash
python -m unittest discover -s tests -v
python -m compileall -q app tests benchmarks main.py
node --check frontend/script.js
python -c "from app.main import app; print(app.title)"
```

Unit tests should not require a running Ollama server. Integration checks that exercise model inference, ChromaDB, or browser crawling need the corresponding local services and dependencies. Report those checks separately from unit tests.
