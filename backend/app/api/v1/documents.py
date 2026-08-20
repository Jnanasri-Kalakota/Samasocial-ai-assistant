from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List
from app.api.deps import get_ingestion_service, get_document_repo
from app.services.ingestion.orchestrator import IngestionOrchestrator
from app.repositories.document_repo import DocumentRepository
from app.schemas.document import DocumentResponse, URLIngestRequest
from app.core.exceptions import AppException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents & Ingestion"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    ingestion_service: IngestionOrchestrator = Depends(get_ingestion_service)
):
    try:
        contents = await file.read()
        doc = await ingestion_service.ingest_file(
            session_id=session_id,
            filename=file.filename,
            file_bytes=contents
        )
        return DocumentResponse.model_validate(doc)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/url", response_model=DocumentResponse)
async def ingest_url(
    payload: URLIngestRequest,
    ingestion_service: IngestionOrchestrator = Depends(get_ingestion_service)
):
    try:
        doc = await ingestion_service.ingest_url(
            session_id=payload.session_id,
            url=payload.url
        )
        return DocumentResponse.model_validate(doc)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Error ingesting URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}", response_model=List[DocumentResponse])
async def list_session_documents(
    session_id: str,
    doc_repo: DocumentRepository = Depends(get_document_repo)
):
    docs = await doc_repo.get_by_session_id(session_id)
    return [DocumentResponse.model_validate(d) for d in docs]

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    doc_repo: DocumentRepository = Depends(get_document_repo)
):
    deleted = await doc_repo.delete_by_id(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully", "id": document_id}
