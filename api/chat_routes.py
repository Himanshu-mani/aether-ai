"""HTTP API routes for streaming chat and document uploads."""

import asyncio
import json
import logging
import os
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent.executor import create_agent
from core.config import ALLOWED_UPLOAD_EXTENSIONS, MAX_UPLOAD_BYTES, UPLOADS_DIR
from core.rag_pipeline import process_and_store_document

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)


def _safe_upload_name(filename: str) -> str:
    name = re.split(r"[/\\\\]", filename or "")[-1].strip()
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name).strip(" .")
    if not name or name in {".", ".."}:
        raise HTTPException(status_code=400, detail="A valid filename is required.")
    return name[:180]


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        try:
            agent_executor, _ = create_agent()
            async for chunk in agent_executor.generate_response_stream(request.message):
                payload = {"type": "chunk", "content": chunk}
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)
            yield 'data: {"type":"done"}\n\n'
        except asyncio.CancelledError:
            raise
        except Exception:
            logging.exception("Chat stream failed")
            payload = {"type": "error", "message": "I could not process this request. Check that Ollama is running and try again."}
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        event_generator(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    original_name = _safe_upload_name(file.filename or "")
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(status_code=415, detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}")

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    file_path = Path(UPLOADS_DIR) / f"{uuid.uuid4().hex}_{original_name}"
    size = 0
    try:
        with file_path.open("wb") as destination:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail=f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB upload limit.")
                destination.write(chunk)
        if size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        status = await asyncio.to_thread(process_and_store_document, str(file_path))
        if not status.startswith("Success!"):
            raise HTTPException(status_code=422, detail=status)
        return {"filename": original_name, "status": status, "message": f"{original_name} was uploaded and indexed successfully."}
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        logging.exception("Upload processing failed")
        raise HTTPException(status_code=500, detail="The file could not be processed. Check server logs for details.") from exc
    finally:
        await file.close()
