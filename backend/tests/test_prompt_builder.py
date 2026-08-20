from app.services.llm.prompt_builder import PromptBuilder
from app.models.chunk import DocumentChunk
import json

def test_prompt_builder_grounding_rules():
    prompt = PromptBuilder.build_system_prompt(simple_terms=True)
    assert "STRICT GROUNDING & CITATION RULES" in prompt
    assert "simple explanation" in prompt

def test_prompt_builder_context_formatting():
    chunk = DocumentChunk(
        id="c-1",
        document_id="d-1",
        session_id="s-1",
        content="FastAPI is a modern asynchronous web framework for Python.",
        metadata_json=json.dumps({"source_name": "fastapi_guide.pdf", "location_label": "Page 2", "source_type": "pdf"})
    )
    formatted = PromptBuilder.format_context_blocks([(chunk, 0.89)])
    assert "fastapi_guide.pdf" in formatted
    assert "Page 2" in formatted
    assert "FastAPI is a modern asynchronous web framework" in formatted
