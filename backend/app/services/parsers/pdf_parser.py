import io
from typing import List
import pypdf
from app.services.parsers.base import BaseParser, ExtractedContent
from app.core.exceptions import DocumentParsingError
import logging

logger = logging.getLogger(__name__)

class PDFParser(BaseParser):
    async def parse(self, file_bytes: bytes, filename: str = "document.pdf", **kwargs) -> List[ExtractedContent]:
        results: List[ExtractedContent] = []
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)
            
            for idx, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                text = text.strip()
                if not text:
                    continue
                    
                results.append(
                    ExtractedContent(
                        text=text,
                        source_type="pdf",
                        source_name=filename,
                        location_label=f"Page {idx}",
                        location_meta={
                            "page_number": idx,
                            "total_pages": total_pages,
                            "filename": filename
                        }
                    )
                )
        except Exception as e:
            logger.error(f"Failed to parse PDF {filename}: {e}")
            raise DocumentParsingError(f"Error parsing PDF '{filename}': {str(e)}")
            
        if not results:
            raise DocumentParsingError(f"No readable text could be extracted from PDF '{filename}'")
            
        return results
