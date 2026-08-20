import json
import logging
from typing import Dict, Any, Optional
from app.services.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class CoursePlannerService:
    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm_provider = llm_provider

    async def generate_course_structure(
        self,
        subject: str,
        target_audience: str,
        duration_weeks: int,
        learning_goals: str,
        syllabus_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a structured course breakdown with modules, lessons, difficulty indicators,
        prerequisites, and recommended public resources (Task 2 Foundation).
        """
        prompt = [
            {
                "role": "system",
                "content": """You are a world-class instructional designer and curriculum architect.
Generate a comprehensive, structured course syllabus in JSON format.
JSON structure must match:
{
  "course_title": "Title",
  "subject": "Topic",
  "target_audience": "Audience",
  "total_weeks": 4,
  "difficulty_progression": "Beginner -> Intermediate",
  "prerequisites": ["List of prerequisite topics"],
  "modules": [
    {
      "module_number": 1,
      "title": "Module Title",
      "learning_objectives": ["Objective 1", "Objective 2"],
      "lessons": [
        {
          "lesson_number": 1,
          "title": "Lesson Title",
          "difficulty": "Beginner",
          "topics": ["Key topic 1", "Key topic 2"],
          "recommended_resources": [
            {"type": "YouTube / Article", "title": "Resource title", "url": "https://example.com"}
          ]
        }
      ],
      "module_assessment": "Project or quiz description"
    }
  ]
}
Return raw valid JSON ONLY."""
            },
            {
                "role": "user",
                "content": f"""Build a course for:
Subject: {subject}
Target Audience: {target_audience}
Duration: {duration_weeks} weeks
Learning Goals: {learning_goals}
Additional Syllabus Context: {syllabus_text or 'None'}
"""
            }
        ]

        raw_output = await self.llm_provider.generate_text(prompt, temperature=0.3)
        raw_output = raw_output.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]

        try:
            return json.loads(raw_output.strip())
        except Exception as e:
            logger.error(f"Failed to parse course plan JSON: {e}")
            return {
                "course_title": f"Complete Course on {subject}",
                "subject": subject,
                "target_audience": target_audience,
                "total_weeks": duration_weeks,
                "difficulty_progression": "Beginner -> Intermediate",
                "prerequisites": ["Basic interest and fundamentals in " + subject],
                "modules": [
                    {
                        "module_number": 1,
                        "title": f"Introduction to {subject}",
                        "learning_objectives": ["Understand core definitions", "Set up development tools"],
                        "lessons": [
                            {
                                "lesson_number": 1,
                                "title": "Fundamentals & Overview",
                                "difficulty": "Beginner",
                                "topics": ["History", "Architecture", "Basic Syntax"],
                                "recommended_resources": [
                                    {"type": "Documentation", "title": "Official Guides", "url": "https://docs.python.org"}
                                ]
                            }
                        ],
                        "module_assessment": "Hands-on starter project"
                    }
                ]
            }
