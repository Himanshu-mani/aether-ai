import json
import re
import subprocess
import time
from typing import Any, Dict

import requests

from core.config import MODEL_NAME, OLLAMA_BASE_URL
from core.resource_manager import build_resource_summary


def run_benchmark(prompt: str) -> Dict[str, Any]:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "keep_alive": "10m",
        "options": {"temperature": 0.0, "num_predict": 256},
    }

    started = time.perf_counter()
    first_token_time = None
    output_parts = []
    metadata = {}

    with requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=payload,
        stream=True,
        timeout=180,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            chunk_text = chunk.get("response", "")
            if chunk_text:
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                output_parts.append(chunk_text)
            if chunk.get("done"):
                metadata = chunk
                break

    finished = time.perf_counter()
    output_text = "".join(output_parts)
    generated_tokens = int(metadata.get("eval_count", 0) or 0)
    prompt_tokens = int(metadata.get("prompt_eval_count", 0) or 0)
    eval_seconds = float(metadata.get("eval_duration", 0) or 0) / 1e9
    prompt_seconds = float(metadata.get("prompt_eval_duration", 0) or 0) / 1e9
    server_total_seconds = float(metadata.get("total_duration", 0) or 0) / 1e9
    words = re.findall(r"\b[\w'-]+\b", output_text)

    try:
        gpu_check = subprocess.run(
            ["ollama", "ps"], capture_output=True, text=True, timeout=10
        )
        gpu_status = gpu_check.stdout.strip() or gpu_check.stderr.strip()
    except Exception as exc:
        gpu_status = f"GPU status check failed: {exc}"

    return {
        "status": "ok",
        "model": MODEL_NAME,
        "ttft_seconds": round(first_token_time - started, 4) if first_token_time else None,
        "ttft_milliseconds": round((first_token_time - started) * 1000, 2) if first_token_time else None,
        "prompt_tokens": prompt_tokens,
        "prompt_eval_seconds": round(prompt_seconds, 4),
        "generated_tokens": generated_tokens,
        "generated_words": len(words),
        "generation_seconds": round(eval_seconds, 4),
        "generation_tokens_per_second": round(generated_tokens / eval_seconds, 2) if eval_seconds else None,
        "server_total_seconds": round(server_total_seconds, 4),
        "client_total_seconds": round(finished - started, 4),
        "output": output_text,
        "gpu_check": gpu_status,
        "resources": build_resource_summary(),
    }


def main() -> int:
    prompt = (
        "Explain how a local-first AI assistant works. Cover privacy, "
        "retrieval augmented generation, local models, and practical examples. "
        "Write several clear paragraphs."
    )
    try:
        result = run_benchmark(prompt)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc), "model": MODEL_NAME}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
