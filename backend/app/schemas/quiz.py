from pydantic import BaseModel
from typing import List, Optional

class QuizOption(BaseModel):
    id: str # 'A', 'B', 'C', 'D'
    text: str

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[QuizOption]
    correct_option_id: str # 'A', 'B', 'C', 'D'
    explanation: str
    source_reference: str # e.g. "Lecture Slides, Slide 4"

class QuizResponse(BaseModel):
    session_id: str
    topic: str
    questions: List[QuizQuestion]

class QuizAnswerSubmission(BaseModel):
    question_id: int
    selected_option_id: str

class QuizSubmission(BaseModel):
    session_id: str
    answers: List[QuizAnswerSubmission]

class QuizQuestionEvaluation(BaseModel):
    question_id: int
    is_correct: bool
    selected_option_id: str
    correct_option_id: str
    explanation: str

class QuizResult(BaseModel):
    score: int
    total: int
    percentage: float
    evaluations: List[QuizQuestionEvaluation]
