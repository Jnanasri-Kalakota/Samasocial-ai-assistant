from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import json
import asyncio

from app.api.deps import (
    get_retrieval_service,
    get_citation_service,
    get_memory_service,
    get_session_repo
)
from app.services.retrieval.retriever import RetrievalService
from app.services.citation.citation_service import CitationService
from app.services.memory.session_memory import SessionMemoryService
from app.repositories.session_repo import SessionRepository
from app.services.llm import get_llm_provider, PromptBuilder
from app.schemas.chat import ChatRequest, MessageView
from app.schemas.citation import CitationItem
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat & Retrieval"])

@router.post("/stream")
async def chat_stream(
    payload: ChatRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    citation_service: CitationService = Depends(get_citation_service),
    memory_service: SessionMemoryService = Depends(get_memory_service)
):
    async def sse_generator():
        try:
            # 1. Retrieve grounded context chunks
            retrieved = await retrieval_service.retrieve_context(
                session_id=payload.session_id,
                query=payload.message
            )

            # 2. Build structured citations
            citations = citation_service.build_citations_from_retrieved_chunks(retrieved)
            citations_dto_list = [c.model_dump() for c in citations]

            # 3. Emit citation event first so client UI can prepare source cards immediately
            yield f"event: citations\ndata: {json.dumps(citations_dto_list)}\n\n"

            # 4. Check if we have grounded context
            if not retrieved:
                declined_msg = (
                    "I cannot find information about this in your uploaded sources. "
                    "Please upload related materials (PDF, PPTX, YouTube, or Web URL) or ask a question regarding the loaded content."
                )
                yield f"event: token\ndata: {json.dumps({'token': declined_msg})}\n\n"
                yield f"event: done\ndata: {json.dumps({'full_text': declined_msg, 'citations': []})}\n\n"
                
                # Save turn
                await memory_service.save_message_turn(
                    session_id=payload.session_id,
                    user_message=payload.message,
                    assistant_message=declined_msg,
                    citations=[]
                )
                return

            # 5. Build prompt with strict grounding and tone
            system_prompt = PromptBuilder.build_system_prompt(simple_terms=payload.simple_terms)
            context_str = PromptBuilder.format_context_blocks(retrieved)
            history = await memory_service.get_conversation_history(payload.session_id, limit=6)
            messages = PromptBuilder.construct_messages(
                system_prompt=system_prompt,
                context_str=context_str,
                conversation_history=history,
                current_query=payload.message
            )

            # 6. Stream tokens from LLM
            llm = get_llm_provider()
            full_response_text = []

            async for token in llm.generate_stream(messages, temperature=0.2):
                full_response_text.append(token)
                yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

            complete_text = "".join(full_response_text)

            # 7. Persist turn in session memory
            await memory_service.save_message_turn(
                session_id=payload.session_id,
                user_message=payload.message,
                assistant_message=complete_text,
                citations=citations_dto_list
            )

            yield f"event: done\ndata: {json.dumps({'full_text': complete_text, 'citations': citations_dto_list})}\n\n"

        except Exception as e:
            logger.error(f"Error in chat stream: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@router.get("/history/{session_id}", response_model=List[MessageView])
async def get_chat_history(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repo)
):
    messages = await session_repo.get_messages(session_id=session_id)
    views = []
    for msg in messages:
        cits = [CitationItem(**c) for c in msg.citations if isinstance(c, dict)]
        views.append(
            MessageView(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                citations=cits,
                created_at=msg.created_at.isoformat()
            )
        )
    return views
