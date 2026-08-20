import io
from typing import List
import docx
from app.services.parsers.base import BaseParser, ExtractedContent
from app.core.exceptions import DocumentParsingError
import logging

logger = logging.getLogger(__name__)

class DOCXParser(BaseParser):
    async def parse(self, file_bytes: bytes, filename: str = "document.docx", **kwargs) -> List[ExtractedContent]:
        results: List[ExtractedContent] = []
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            current_heading = "General"
            section_paragraphs = []
            section_idx = 1
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                    
                if para.style.name.startswith("Heading"):
                    if section_paragraphs:
                        combined_text = "\n".join(section_paragraphs)
                        results.append(
                            ExtractedContent(
                                text=combined_text,
                                source_type="docx",
                                source_name=filename,
                                location_label=f"§ {current_heading}",
                                location_meta={
                                    "heading": current_heading,
                                    "section_idx": section_idx,
                                    "filename": filename
                                }
                            )
                        )
                        section_paragraphs = []
                        section_idx += 1
                    current_heading = text
                else:
                    section_paragraphs.append(text)
                    
            if section_paragraphs:
                combined_text = "\n".join(section_paragraphs)
                results.append(
                    ExtractedContent(
                        text=combined_text,
                        source_type="docx",
                        source_name=filename,
                        location_label=f"§ {current_heading}",
                        location_meta={
                            "heading": current_heading,
                            "section_idx": section_idx,
                            "filename": filename
                        }
                    )
                )
        except Exception as e:
            logger.error(f"Failed to parse DOCX {filename}: {e}")
            raise DocumentParsingError(f"Error parsing Word Document '{filename}': {str(e)}")
            
        if not results:
            raise DocumentParsingError(f"No text content found in Word Document '{filename}'")
            
        return results
