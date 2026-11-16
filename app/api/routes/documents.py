"""Document upload endpoint."""
from fastapi import APIRouter, File, UploadFile
from app.services.document_service import upload_document

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return await upload_document(file)
