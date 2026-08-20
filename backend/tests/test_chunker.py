from app.services.parsers.base import ExtractedContent
from app.services.chunking.text_chunker import TextChunker

def test_chunker_metadata_preservation():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    
    items = [
        ExtractedContent(
            text="Vector embeddings allow semantic similarity search over unstructured text. They encode high-dimensional representations of concepts.",
            source_type="pdf",
            source_name="guide.pdf",
            location_label="Page 3",
            location_meta={"page_number": 3, "total_pages": 10}
        )
    ]
    
    chunks = chunker.chunk_extracted_content(items, document_id="doc-123", session_id="sess-456")
    assert len(chunks) >= 1
    for c in chunks:
        assert c.document_id == "doc-123"
        assert c.session_id == "sess-456"
        meta = c.metadata_dict
        assert meta["page_number"] == 3
        assert meta["location_label"] == "Page 3"
        assert meta["source_name"] == "guide.pdf"
