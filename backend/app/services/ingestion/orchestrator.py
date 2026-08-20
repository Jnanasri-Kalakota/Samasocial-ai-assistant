import os
import json
import logging
from typing import List, Optional

from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.repositories.document_repo import DocumentRepository
from app.repositories.chunk_repo import ChunkRepository
from app.services.parsers.base import ExtractedContent, BaseParser
from app.services.parsers.pdf_parser import PDFParser
from app.services.parsers.pptx_parser import PPTXParser
from app.services.parsers.docx_parser import DOCXParser
from app.services.parsers.web_parser import WebParser
from app.services.parsers.youtube_parser import YouTubeParser
from app.services.chunking.text_chunker import TextChunker
from app.services.embeddings.base import BaseEmbeddingProvider
from app.services.llm.base import BaseLLMProvider
from app.core.exceptions import DocumentParsingError

logger = logging.getLogger(__name__)

class IngestionOrchestrator:
    def __init__(
        self,
        doc_repo: DocumentRepository,
        chunk_repo: ChunkRepository,
        embedding_provider: BaseEmbeddingProvider,
        llm_provider: BaseLLMProvider
    ):
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider
        self.chunker = TextChunker()

        # Registered parsers
        self.pdf_parser = PDFParser()
        self.pptx_parser = PPTXParser()
        self.docx_parser = DOCXParser()
        self.web_parser = WebParser()
        self.youtube_parser = YouTubeParser()

    async def ingest_file(
        self,
        session_id: str,
        filename: str,
        file_bytes: bytes
    ) -> Document:
        ext = os.path.splitext(filename)[1].lower()
        source_type = "file"
        extracted_items: List[ExtractedContent] = []

        if ext == ".pdf":
            source_type = "pdf"
            extracted_items = await self.pdf_parser.parse(file_bytes, filename=filename)
        elif ext in [".pptx", ".ppt"]:
            source_type = "pptx"
            extracted_items = await self.pptx_parser.parse(file_bytes, filename=filename)
        elif ext in [".docx", ".doc"]:
            source_type = "docx"
            extracted_items = await self.docx_parser.parse(file_bytes, filename=filename)
        else:
            raise DocumentParsingError(f"Unsupported file extension '{ext}'. Supported: .pdf, .pptx, .docx")

        return await self._process_extracted_content(
            session_id=session_id,
            source_type=source_type,
            source_name=filename,
            source_url=None,
            extracted_items=extracted_items
        )

    async def ingest_url(
        self,
        session_id: str,
        url: str
    ) -> Document:
        extracted_items: List[ExtractedContent] = []
        is_youtube = ("youtube.com" in url or "youtu.be" in url)
        
        if is_youtube:
            source_type = "youtube"
            extracted_items = await self.youtube_parser.parse(url)
            source_name = extracted_items[0].source_name if extracted_items else "YouTube Video"
        else:
            source_type = "web"
            extracted_items = await self.web_parser.parse(url)
            source_name = extracted_items[0].source_name if extracted_items else "Web Page"

        return await self._process_extracted_content(
            session_id=session_id,
            source_type=source_type,
            source_name=source_name,
            source_url=url,
            extracted_items=extracted_items
        )

    async def _process_extracted_content(
        self,
        session_id: str,
        source_type: str,
        source_name: str,
        source_url: Optional[str],
        extracted_items: List[ExtractedContent]
    ) -> Document:
        # 1. Create document record
        doc = Document(
            session_id=session_id,
            source_type=source_type,
            source_name=source_name,
            source_url=source_url,
            summary="Processing document...",
            chunk_count=0
        )
        doc = await self.doc_repo.create(doc)

        # 2. Chunk text with metadata preservation
        chunks = self.chunker.chunk_extracted_content(
            extracted_items=extracted_items,
            document_id=doc.id,
            session_id=session_id
        )

        if not chunks:
            raise DocumentParsingError(f"Document '{source_name}' contains no readable text content.")

        # 3. High-throughput batch vector embeddings
        chunk_texts = [c.content for c in chunks]
        embeddings = await self.embedding_provider.embed_documents(chunk_texts)

        for chunk, emb in zip(chunks, embeddings):
            chunk.embedding_json = json.dumps(emb)

        # 4. Save chunks
        await self.chunk_repo.save_chunks(chunks)

        # 5. Fast summary generation
        summary = self._generate_smart_summary(source_name, extracted_items, len(chunks))
        await self.doc_repo.update_summary(doc.id, summary=summary, chunk_count=len(chunks))

        doc.summary = summary
        doc.chunk_count = len(chunks)
        return doc

    def _generate_smart_summary(self, source_name: str, extracted_items: List[ExtractedContent], total_chunks: int) -> str:
        if not extracted_items:
            return f"Processed {source_name} into {total_chunks} retrieval chunks."

        lead_texts = []
        for item in extracted_items[:3]:
            lines = [l.strip() for l in item.text.split('\n') if len(l.strip()) > 30]
            if lines:
                lead_texts.append(lines[0])

        if lead_texts:
            lead = ". ".join(lead_texts[:2]).replace("..", ".")
            if len(lead) > 220:
                lead = lead[:217] + "..."
            return f"{lead} ({total_chunks} chunks indexed)"
            
        return f"Indexed '{source_name}' across {len(extracted_items)} sections and {total_chunks} semantic chunks."
