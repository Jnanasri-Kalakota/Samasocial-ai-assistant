from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ExtractedContent:
    text: str
    source_type: str # 'pdf', 'pptx', 'docx', 'web', 'youtube'
    source_name: str
    location_label: str # "Page 4", "Slide 2", "03:15", "§ Overview"
    location_meta: Dict[str, Any] = field(default_factory=dict)
    source_url: Optional[str] = None

class BaseParser(ABC):
    @abstractmethod
    async def parse(self, source: Any, **kwargs) -> List[ExtractedContent]:
        """Extract text content with fine-grained location metadata."""
        pass
