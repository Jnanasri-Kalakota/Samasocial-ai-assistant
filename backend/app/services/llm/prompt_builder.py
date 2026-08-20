from typing import List, Tuple, Dict, Any
from app.models.chunk import DocumentChunk
import json

class PromptBuilder:
    @staticmethod
    def build_system_prompt(simple_terms: bool = False) -> str:
        tone_instruction = ""
        if simple_terms:
            tone_instruction = (
                "\n- TONE: The user requested a simple explanation. Explain concepts in clear, intuitive "
                "language with beginner-friendly analogies while strictly grounded in the source facts."
            )

        return f"""You are an expert AI Learning Assistant built for SamaSocial.
STRICT GROUNDING & CITATION RULES:
1. Ground your answers ONLY in the provided source context chunks below. Do NOT invent facts.
2. CITATIONS: Cite the exact source inline using bracket format:
   - PDFs: [Source: <filename>, Page <num>]
   - PPTX: [Source: <filename>, Slide <num>]
   - YouTube: [Source: <title>, <MM:SS>]
   - Web: [Source: <title>, Web]
   - DOCX: [Source: <filename>, § <heading>]
3. OUT-OF-SCOPE: If the context lacks the answer, decline politely:
   "I cannot find information about this in your uploaded sources. Please ask about topics covered in the loaded documents."
4. Be direct, clear, and concise.{tone_instruction}
""".strip()

    @staticmethod
    def format_context_blocks(chunks_with_scores: List[Tuple[DocumentChunk, float]]) -> str:
        if not chunks_with_scores:
            return "No matching source materials found in this session."

        blocks = []
        for idx, (chunk, score) in enumerate(chunks_with_scores[:3], start=1):
            meta = chunk.metadata_dict
            source_name = meta.get("source_name", "Document")
            label = meta.get("location_label", "Unknown")
            source_type = meta.get("source_type", "file")
            
            clean_content = chunk.content[:500].strip()
            header = f"[SOURCE {idx}: {source_name} | {label} | Type: {source_type}]"
            blocks.append(f"{header}\n{clean_content}\n")

        return "\n---\n".join(blocks)

    @staticmethod
    def construct_messages(
        system_prompt: str,
        context_str: str,
        conversation_history: List[Dict[str, str]],
        current_query: str
    ) -> List[Dict[str, str]]:
        messages = [
            {"role": "system", "content": f"{system_prompt}\n\n=== KNOWLEDGE CONTEXT ===\n{context_str}"}
        ]
        
        for msg in conversation_history[-2:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": current_query})
        return messages
