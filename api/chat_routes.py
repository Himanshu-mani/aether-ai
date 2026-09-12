import os
import shutil
import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Core Imports
from langchain_core.outputs import LLMResult
from typing import Any

from agent.executor import create_agent
from core.config import UPLOADS_DIR
from core.rag_pipeline import process_and_store_document

from fastapi.responses import JSONResponse

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        user_message = request.message
        agent_executor, _ = create_agent()
        
        reply_text = await agent_executor.generate_response(user_message)
        return {"reply": reply_text}
    except Exception as e:
        print(f"[!] Agent Execution Error: {e}")
        return {"reply": "I encountered an error processing this request. Please ask again."}

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
            "message": f"File '{file.filename}' successfully saved to memory."
        }
    except Exception as e:
        print(f"[!] Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))