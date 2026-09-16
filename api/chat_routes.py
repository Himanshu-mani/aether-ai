import asyncio
import json
import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.executor import create_agent
from core.config import UPLOADS_DIR
from core.rag_pipeline import process_and_store_document

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    async def event_generator():
        try:
            agent_executor, _ = create_agent()
            async for chunk in agent_executor.generate_response_stream(request.message):
                payload = {"type": "chunk", "content": chunk}
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0)
            yield "data: {\"type\": \"done\"}\n\n"
        except asyncio.CancelledError:
            print("[!] SSE stream cancelled by client.")
            raise
        except Exception as exc:
            print(f"[!] Agent Execution Error: {exc}")
            payload = {"type": "error", "content": "I encountered an error processing this request. Please ask again."}
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        file_path = os.path.join(UPLOADS_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        rag_status = process_and_store_document(file_path)

        return {
            "filename": file.filename,
            "status": rag_status,
            "message": f"File '{file.filename}' successfully saved to memory.",
        }
    except Exception as e:
        print(f"[!] Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
