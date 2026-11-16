"""Document upload and indexing use case."""
import asyncio
import logging
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import ALLOWED_UPLOAD_EXTENSIONS, MAX_UPLOAD_BYTES, UPLOADS_DIR
from app.rag.ingestion import process_and_store_document


def _safe_upload_name(filename: str) -> str:
    name = re.split(r"[/\\]", filename or "")[-1].strip()
    name = re.sub(r"[^A-Za-z0-9._ -]", "_", name).strip(" .")
    if not name or name in {".", ".."}:
        raise HTTPException(status_code=400, detail="A valid filename is required.")
    return name[:180]


async def upload_document(file: UploadFile):
    original_name = _safe_upload_name(file.filename or "")
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_UPLOAD_EXTENSIONS))
        raise HTTPException(status_code=415, detail=f"Unsupported file type. Allowed: {allowed}")

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOADS_DIR / f"{uuid.uuid4().hex}_{original_name}"
    size = 0
    try:
        with file_path.open("wb") as destination:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    limit_mb = MAX_UPLOAD_BYTES // (1024 * 1024)
                    raise HTTPException(status_code=413, detail=f"File exceeds the {limit_mb} MB upload limit.")
                destination.write(chunk)
        if size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        status = await asyncio.to_thread(process_and_store_document, str(file_path))
        if not status.startswith("Success!"):
            raise HTTPException(status_code=422, detail=status)
        return {
            "filename": original_name,
            "status": status,
            "message": f"{original_name} was uploaded and indexed successfully.",
        }
    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        logging.exception("Upload processing failed")
        raise HTTPException(
            status_code=500,
            detail="The file could not be processed. Check server logs for details.",
        ) from exc
    finally:
        await file.close()
