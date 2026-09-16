import json
import time
from typing import Any, Dict

from core.config import MODEL_NAME, OLLAMA_BASE_URL
from core.resource_manager import build_resource_summary


def _run_ollama_generate(prompt: str, model: str = MODEL_NAME) -> Dict[str, Any]:
    import requests

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0},
    }

    started = time.perf_counter()
    response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=120)
    elapsed = time.perf_counter() - started

    if response.status_code != 200:
        raise RuntimeError(f"Ollama generation request failed: {response.status_code} {response.text[:300]}")

    data = response.json()
    eval_count = int(data.get("eval_count", 0) or 0)
    prompt_eval_count = int(data.get("prompt_eval_count", 0) or 0)
    total_duration_s = float(data.get("total_duration", 0) or 0) / 1_000_000_000
    prompt_eval_duration_s = float(data.get("prompt_eval_duration", 0) or 0) / 1_000_000_000
    eval_duration_s = float(data.get("eval_duration", 0) or 0) / 1_000_000_000

    return {
        "model": model,
        "prompt_tokens": prompt_eval_count,
        "prompt_eval_duration_s": prompt_eval_duration_s or None,
        "eval_duration_s": eval_duration_s or None,
        "total_duration_s": total_duration_s or elapsed,
        "generated_tokens": eval_count,
        "generation_tokens_per_sec": (eval_count / eval_duration_s) if eval_duration_s else None,
    }


def main() -> int:
    prompt = "Explain in two short sentences why a local-first AI assistant is useful for private work."
    try:
        result = _run_ollama_generate(prompt)
    except Exception as exc:
        print(json.dumps({
            "status": "error",
            "error": str(exc),
            "model": MODEL_NAME,
            "resources": build_resource_summary(),
        }, indent=2))
        return 1

    print(json.dumps({
        "status": "ok",
        **result,
        "resources": build_resource_summary(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
