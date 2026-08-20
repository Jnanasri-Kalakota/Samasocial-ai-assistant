from fastapi import APIRouter
from app.api.v1.documents import router as documents_router
from app.api.v1.chat import router as chat_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.quiz import router as quiz_router

api_v1_router = APIRouter()

api_v1_router.include_router(sessions_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(quiz_router)
