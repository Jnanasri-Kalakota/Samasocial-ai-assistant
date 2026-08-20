from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.repositories.document_repo import DocumentRepository
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.session_repo import SessionRepository
from app.services.embeddings import get_embedding_provider
from app.services.llm import get_llm_provider
from app.services.ingestion.orchestrator import IngestionOrchestrator
from app.services.retrieval.retriever import RetrievalService
from app.services.citation.citation_service import CitationService
from app.services.memory.session_memory import SessionMemoryService
from app.services.quiz.quiz_service import QuizService
from app.services.planner.course_planner import CoursePlannerService

async def get_document_repo(db: AsyncSession = Depends(get_db_session)) -> DocumentRepository:
    return DocumentRepository(db)

async def get_chunk_repo(db: AsyncSession = Depends(get_db_session)) -> ChunkRepository:
    return ChunkRepository(db)

async def get_session_repo(db: AsyncSession = Depends(get_db_session)) -> SessionRepository:
    return SessionRepository(db)

async def get_ingestion_service(
    doc_repo: DocumentRepository = Depends(get_document_repo),
    chunk_repo: ChunkRepository = Depends(get_chunk_repo)
) -> IngestionOrchestrator:
    return IngestionOrchestrator(
        doc_repo=doc_repo,
        chunk_repo=chunk_repo,
        embedding_provider=get_embedding_provider(),
        llm_provider=get_llm_provider()
    )

async def get_retrieval_service(
    chunk_repo: ChunkRepository = Depends(get_chunk_repo)
) -> RetrievalService:
    return RetrievalService(
        chunk_repo=chunk_repo,
        embedding_provider=get_embedding_provider()
    )

async def get_citation_service() -> CitationService:
    return CitationService()

async def get_memory_service(
    session_repo: SessionRepository = Depends(get_session_repo)
) -> SessionMemoryService:
    return SessionMemoryService(session_repo=session_repo)

async def get_quiz_service(
    chunk_repo: ChunkRepository = Depends(get_chunk_repo)
) -> QuizService:
    return QuizService(
        chunk_repo=chunk_repo,
        llm_provider=get_llm_provider()
    )

async def get_course_planner_service() -> CoursePlannerService:
    return CoursePlannerService(llm_provider=get_llm_provider())
