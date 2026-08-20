from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal

class SourceLocationMeta(BaseModel):
    page_number: Optional[int] = None
    total_pages: Optional[int] = None
    slide_number: Optional[int] = None
    slide_title: Optional[str] = None
    heading: Optional[str] = None
    paragraph_idx: Optional[int] = None
    start_time_seconds: Optional[float] = None
    formatted_time: Optional[str] = None
    url: Optional[str] = None
    section_heading: Optional[str] = None

class CitationItem(BaseModel):
    source_id: str
    source_name: str
    source_type: Literal["pdf", "pptx", "docx", "web", "youtube"]
    source_url: Optional[str] = None
    location_label: str # e.g. "Page 4", "Slide 3", "03:22", "§ Intro"
    location_meta: SourceLocationMeta
    snippet: str # Snippet of the grounded chunk
