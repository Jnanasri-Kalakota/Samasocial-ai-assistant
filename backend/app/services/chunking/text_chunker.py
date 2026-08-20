from typing import List, Dict, Any
from app.services.parsers.base import ExtractedContent
from app.models.chunk import DocumentChunk
from app.core.config import settings
import json
import uuid

class TextChunker:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def _split_text(self, text: str) -> List[str]:
        """Splits text recursively using paragraphs, sentences, or word boundaries."""
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size
            if end >= text_len:
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break

            # Find best split boundary (newline or period or space)
            split_idx = -1
            boundary_candidates = [
                text.rfind("\n\n", start, end),
                text.rfind("\n", start, end),
                text.rfind(". ", start, end),
                text.rfind(" ", start, end)
            ]
            for candidate in boundary_candidates:
                if candidate != -1 and candidate > start + (self.chunk_size // 3):
                    split_idx = candidate + (1 if candidate == text.rfind(". ", start, end) else 0)
                    break

            if split_idx == -1:
                split_idx = end

            chunk = text[start:split_idx].strip()
            if chunk:
                chunks.append(chunk)

            # Shift start by chunk length minus overlap
            start = max(start + 1, split_idx - self.chunk_overlap)

        return chunks

    def chunk_extracted_content(
        self,
        extracted_items: List[ExtractedContent],
        document_id: str,
        session_id: str
    ) -> List[DocumentChunk]:
        """
        Converts extracted content pages/slides/segments into DocumentChunks,
        propagating and preserving full provenance metadata.
        """
        chunks: List[DocumentChunk] = []

        for item in extracted_items:
            sub_texts = self._split_text(item.text)
            for sub_text in sub_texts:
                meta = {
                    "source_name": item.source_name,
                    "source_type": item.source_type,
                    "source_url": item.source_url,
                    "location_label": item.location_label,
                    **item.location_meta
                }
                chunks.append(
                    DocumentChunk(
                        id=str(uuid.uuid4()),
                        document_id=document_id,
                        session_id=session_id,
                        content=sub_text,
                        metadata_json=json.dumps(meta),
                        embedding_json=None
                    )
                )

        return chunks
