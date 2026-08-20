import json
import logging
from typing import List
from app.repositories.chunk_repo import ChunkRepository
from app.services.llm.base import BaseLLMProvider
from app.schemas.quiz import QuizQuestion, QuizResponse, QuizOption, QuizSubmission, QuizResult, QuizQuestionEvaluation

logger = logging.getLogger(__name__)

class QuizService:
    def __init__(self, chunk_repo: ChunkRepository, llm_provider: BaseLLMProvider):
        self.chunk_repo = chunk_repo
        self.llm_provider = llm_provider

    async def generate_quiz(self, session_id: str, num_questions: int = 4) -> QuizResponse:
        chunks = await self.chunk_repo.get_chunks_by_session_id(session_id)
        if not chunks:
            raise ValueError("No documents loaded in this session yet. Upload a PDF, PPTX, or URL first.")

        sample_texts = []
        source_labels = []
        for c in chunks[:4]:
            meta = c.metadata_dict
            label = meta.get("location_label", "Section")
            source_name = meta.get("source_name", "Document")
            source_labels.append(f"{source_name} ({label})")
            sample_texts.append(f"[{source_name} | {label}]: {c.content[:300]}")

        combined_context = "\n\n".join(sample_texts)

        prompt = [
            {
                "role": "system",
                "content": """You are an expert test generator.
Create 3 multiple choice questions based on the provided material.
Return a valid JSON array matching:
[
  {
    "id": 1,
    "question": "Question text?",
    "options": [
      {"id": "A", "text": "Option A"},
      {"id": "B", "text": "Option B"},
      {"id": "C", "text": "Option C"},
      {"id": "D", "text": "Option D"}
    ],
    "correct_option_id": "A",
    "explanation": "Why A is correct",
    "source_reference": "Source Name, Location"
  }
]
Output ONLY raw JSON."""
            },
            {
                "role": "user",
                "content": f"Generate questions from this content:\n\n{combined_context}"
            }
        ]

        try:
            raw_output = await self.llm_provider.generate_text(prompt, temperature=0.3)
            raw_output = raw_output.strip()
            if raw_output.startswith("```json"):
                raw_output = raw_output[7:]
            if raw_output.startswith("```"):
                raw_output = raw_output[3:]
            if raw_output.endswith("```"):
                raw_output = raw_output[:-3]

            questions_data = json.loads(raw_output.strip())
            questions: List[QuizQuestion] = []
            for item in questions_data:
                opts = [QuizOption(id=o["id"], text=o["text"]) for o in item["options"]]
                questions.append(
                    QuizQuestion(
                        id=item["id"],
                        question=item["question"],
                        options=opts,
                        correct_option_id=item["correct_option_id"],
                        explanation=item["explanation"],
                        source_reference=item.get("source_reference", source_labels[0] if source_labels else "Loaded Materials")
                    )
                )
            if questions:
                return QuizResponse(session_id=session_id, topic="Session Mastery Quiz", questions=questions)
        except Exception as e:
            logger.warning(f"LLM quiz parsing fallback triggered: {e}")

        first_source = source_labels[0] if source_labels else "Uploaded Materials"
        second_source = source_labels[1] if len(source_labels) > 1 else first_source
        
        fallback_questions = [
            QuizQuestion(
                id=1,
                question=f"Based on {first_source}, what is the primary focus of the discussed concepts?",
                options=[
                    QuizOption(id="A", text="Core architectural mechanisms and operational fundamentals"),
                    QuizOption(id="B", text="Unrelated external domain standards"),
                    QuizOption(id="C", text="Theoretical frameworks without practical context"),
                    QuizOption(id="D", text="None of the above")
                ],
                correct_option_id="A",
                explanation=f"The primary material in {first_source} highlights the core mechanisms and principles.",
                source_reference=first_source
            ),
            QuizQuestion(
                id=2,
                question=f"How does the knowledge presented in {second_source} connect with the session learning outcomes?",
                options=[
                    QuizOption(id="A", text="It establishes evidence-backed definitions and structured examples"),
                    QuizOption(id="B", text="It contradicts the core methodology"),
                    QuizOption(id="C", text="It provides generic unrelated web content"),
                    QuizOption(id="D", text="It is purely deprecated historical data")
                ],
                correct_option_id="A",
                explanation="The loaded source provides grounded, contextual evidence supporting the session topics.",
                source_reference=second_source
            )
        ]
        return QuizResponse(session_id=session_id, topic="Knowledge Check", questions=fallback_questions)

    async def evaluate_submission(
        self,
        submission: QuizSubmission,
        original_quiz: List[QuizQuestion]
    ) -> QuizResult:
        quiz_map = {q.id: q for q in original_quiz}
        evaluations: List[QuizQuestionEvaluation] = []
        score = 0

        for ans in submission.answers:
            q = quiz_map.get(ans.question_id)
            if not q:
                continue
            is_correct = (ans.selected_option_id.upper() == q.correct_option_id.upper())
            if is_correct:
                score += 1
            evaluations.append(
                QuizQuestionEvaluation(
                    question_id=q.id,
                    is_correct=is_correct,
                    selected_option_id=ans.selected_option_id,
                    correct_option_id=q.correct_option_id,
                    explanation=q.explanation
                )
            )

        total = len(original_quiz) if original_quiz else len(submission.answers)
        pct = (score / total * 100.0) if total > 0 else 0.0
        return QuizResult(score=score, total=total, percentage=round(pct, 1), evaluations=evaluations)
