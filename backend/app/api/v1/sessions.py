from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.deps import get_session_repo, get_document_repo
from app.repositories.session_repo import SessionRepository
from app.repositories.document_repo import DocumentRepository
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionResponse, SessionDetailResponse
from app.schemas.document import DocumentResponse
from app.schemas.chat import MessageView
from app.schemas.citation import CitationItem

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/", response_model=SessionResponse)
async def create_session(
    payload: SessionCreate,
    session_repo: SessionRepository = Depends(get_session_repo)
):
    new_session = Session(title=payload.title or "New Learning Session")
    created = await session_repo.create(new_session)
    return SessionResponse(
        id=created.id,
        title=created.title,
        created_at=created.created_at,
        updated_at=created.updated_at,
        document_count=0
    )

@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    session_repo: SessionRepository = Depends(get_session_repo)
):
    sessions = await session_repo.list_sessions(limit=50)
    result = []
    for s in sessions:
        doc_count = len(s.documents) if s.documents else 0
        result.append(
            SessionResponse(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
                document_count=doc_count
            )
        )
    return result

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repo)
):
    session = await session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    docs = [DocumentResponse.model_validate(d) for d in session.documents]
    msgs = []
    for m in session.messages:
        cits = [CitationItem(**c) for c in m.citations if isinstance(c, dict)]
        msgs.append(
            MessageView(
                id=m.id,
                role=m.role,
                content=m.content,
                citations=cits,
                created_at=m.created_at.isoformat()
            )
        )

    return SessionDetailResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        documents=docs,
        messages=msgs
    )

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repo)
):
    deleted = await session_repo.delete_by_id(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted", "id": session_id}
