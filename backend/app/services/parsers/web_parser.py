import httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import List
from app.services.parsers.base import BaseParser, ExtractedContent
from app.core.exceptions import DocumentParsingError
import logging

logger = logging.getLogger(__name__)

class WebParser(BaseParser):
    async def parse(self, url: str, **kwargs) -> List[ExtractedContent]:
        results: List[ExtractedContent] = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                html = response.text
                
            domain = urlparse(url).netloc
            soup = BeautifulSoup(html, "html.parser")
            
            # Remove scripts, styles, header, footer, nav
            for element in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
                element.decompose()
                
            page_title = soup.title.string.strip() if soup.title and soup.title.string else domain
            
            # Try trafilatura if available
            extracted_text = None
            try:
                import trafilatura
                extracted_text = trafilatura.extract(html, include_links=False, include_images=False, output_format="txt")
            except Exception:
                pass
                
            if not extracted_text:
                # Extract clean paragraphs and article sections
                paragraphs = []
                for tag in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
                    text = tag.get_text().strip()
                    if len(text) > 25:
                        paragraphs.append(text)
                extracted_text = "\\n\\n".join(paragraphs)
                
            if not extracted_text or len(extracted_text.strip()) < 20:
                extracted_text = soup.get_text(separator="\\n")
                extracted_text = "\\n".join([line.strip() for line in extracted_text.splitlines() if len(line.strip()) > 30])
                
            if not extracted_text or len(extracted_text.strip()) < 20:
                raise DocumentParsingError(f"Could not extract readable text from webpage: {url}")
                
            results.append(
                ExtractedContent(
                    text=extracted_text.strip(),
                    source_type="web",
                    source_name=page_title,
                    source_url=url,
                    location_label=f"Web: {domain}",
                    location_meta={
                        "url": url,
                        "page_title": page_title,
                        "domain": domain
                    }
                )
            )
        except Exception as e:
            logger.error(f"Failed to scrape URL {url}: {e}")
            raise DocumentParsingError(f"Error fetching/parsing webpage '{url}': {str(e)}")
            
        return results
