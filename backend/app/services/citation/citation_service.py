from typing import List, Tuple, Dict, Any
from app.models.chunk import DocumentChunk
from app.schemas.citation import CitationItem, SourceLocationMeta

class CitationService:
    @staticmethod
    def build_citations_from_retrieved_chunks(
        retrieved_chunks: List[Tuple[DocumentChunk, float]]
    ) -> List[CitationItem]:
        """
        Constructs rich, structured CitationItem DTOs from retrieved context chunks.
        """
        citations: List[CitationItem] = []
        seen_keys = set()

        for chunk, score in retrieved_chunks:
            meta = chunk.metadata_dict
            source_id = chunk.document_id
            source_name = meta.get("source_name", "Document")
            source_type = meta.get("source_type", "pdf")
            source_url = meta.get("source_url")
            label = meta.get("location_label", "Reference")
            
            # Deduplicate by (source_name, label)
            dedup_key = f"{source_name}:{label}"
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            snippet = chunk.content[:180].replace("\n", " ").strip() + "..."

            location_meta = SourceLocationMeta(
                page_number=meta.get("page_number"),
                total_pages=meta.get("total_pages"),
                slide_number=meta.get("slide_number"),
                slide_title=meta.get("slide_title"),
                heading=meta.get("heading"),
                paragraph_idx=meta.get("paragraph_idx"),
                start_time_seconds=meta.get("start_time_seconds"),
                formatted_time=meta.get("formatted_time"),
                url=meta.get("url") or source_url,
                section_heading=meta.get("section_heading")
            )

            citations.append(
                CitationItem(
                    source_id=source_id,
                    source_name=source_name,
                    source_type=source_type,
                    source_url=source_url,
                    location_label=label,
                    location_meta=location_meta,
                    snippet=snippet
                )
            )

        return citations
