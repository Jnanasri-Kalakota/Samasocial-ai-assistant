from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_quiz_service
from app.services.quiz.quiz_service import QuizService
from app.schemas.quiz import QuizResponse, QuizSubmission, QuizResult

router = APIRouter(prefix="/quiz", tags=["Quiz Generation (Bonus)"])

@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    session_id: str,
    num_questions: int = 4,
    quiz_service: QuizService = Depends(get_quiz_service)
):
    try:
        return await quiz_service.generate_quiz(session_id=session_id, num_questions=num_questions)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation error: {str(e)}")
