import re
import httpx
from typing import List, Optional, Any
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from app.services.parsers.base import BaseParser, ExtractedContent
from app.core.exceptions import DocumentParsingError
import logging

logger = logging.getLogger(__name__)

class YouTubeParser(BaseParser):
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        clean_url = url.strip()
        if "youtu.be" in clean_url:
            path = urlparse(clean_url).path
            return path.lstrip("/").split("?")[0].split("&")[0]
        elif "youtube.com" in clean_url:
            parsed = urlparse(clean_url)
            query = parse_qs(parsed.query)
            if "v" in query:
                return query["v"][0]
            elif "/embed/" in parsed.path:
                return parsed.path.split("/embed/")[1].split("?")[0]
            elif "/shorts/" in parsed.path:
                return parsed.path.split("/shorts/")[1].split("?")[0]
        
        match = re.search(r"(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})", clean_url)
        return match.group(1) if match else None

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        seconds = int(seconds)
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"

    async def fetch_video_title(self, video_id: str) -> str:
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(oembed_url)
                if res.status_code == 200:
                    title = res.json().get("title")
                    if title:
                        return title
        except Exception:
            pass
        return f"YouTube Video ({video_id})"

    async def parse(self, url: str, **kwargs) -> List[ExtractedContent]:
        video_id = self.extract_video_id(url)
        if not video_id:
            raise DocumentParsingError(f"Invalid YouTube URL: '{url}'")

        title = await self.fetch_video_title(video_id)
        raw_snippets = []

        try:
            yt_api = YouTubeTranscriptApi()
            try:
                transcript_list = yt_api.list(video_id)
            except TypeError:
                transcript_list = YouTubeTranscriptApi.list(video_id)

            target_transcript = None
            # 1. Prefer English variants (en-IN, en-US, en-GB, en)
            for lang_code in ['en', 'en-IN', 'en-US', 'en-GB', 'en-CA', 'en-AU']:
                for t in transcript_list:
                    if t.language_code.lower().startswith(lang_code.lower()):
                        target_transcript = t
                        break
                if target_transcript:
                    break

            # 2. Fallback to first available transcript
            if not target_transcript:
                target_transcript = next(iter(transcript_list), None)

            if target_transcript:
                raw_snippets = target_transcript.fetch()
            else:
                raise Exception("No transcripts listed.")

        except Exception as transcript_err:
            logger.warning(f"youtube-transcript-api list error for {video_id}: {transcript_err}")
            try:
                raw_snippets = YouTubeTranscriptApi().fetch(video_id, languages=['en', 'en-IN', 'hi', 'es', 'fr', 'de'])
            except Exception as direct_err:
                raise DocumentParsingError(f"Could not retrieve transcripts for YouTube video '{url}': {str(transcript_err)}")

        if not raw_snippets:
            raise DocumentParsingError(f"No subtitle entries found for YouTube video '{title}'")

        results: List[ExtractedContent] = []
        current_segment_text = []
        segment_start_time = 0.0
        segment_duration = 0.0

        for item in raw_snippets:
            text = getattr(item, 'text', item.get('text', '') if isinstance(item, dict) else str(item)).strip()
            start = float(getattr(item, 'start', item.get('start', 0.0) if isinstance(item, dict) else 0.0))
            dur = float(getattr(item, 'duration', item.get('duration', 0.0) if isinstance(item, dict) else 0.0))

            if not text:
                continue

            if not current_segment_text:
                segment_start_time = start

            current_segment_text.append(text)
            segment_duration = (start + dur) - segment_start_time

            if segment_duration >= 40.0 or len(" ".join(current_segment_text).split()) >= 70:
                formatted_time = self.format_timestamp(segment_start_time)
                results.append(
                    ExtractedContent(
                        text=" ".join(current_segment_text),
                        source_type="youtube",
                        source_name=title,
                        source_url=f"https://www.youtube.com/watch?v={video_id}&t={int(segment_start_time)}s",
                        location_label=formatted_time,
                        location_meta={
                            "start_time_seconds": segment_start_time,
                            "formatted_time": formatted_time,
                            "duration": segment_duration,
                            "video_id": video_id,
                            "title": title,
                            "url": f"https://www.youtube.com/watch?v={video_id}&t={int(segment_start_time)}s"
                        }
                    )
                )
                current_segment_text = []

        if current_segment_text:
            formatted_time = self.format_timestamp(segment_start_time)
            results.append(
                ExtractedContent(
                    text=" ".join(current_segment_text),
                    source_type="youtube",
                    source_name=title,
                    source_url=f"https://www.youtube.com/watch?v={video_id}&t={int(segment_start_time)}s",
                    location_label=formatted_time,
                    location_meta={
                        "start_time_seconds": segment_start_time,
                        "formatted_time": formatted_time,
                        "duration": segment_duration,
                        "video_id": video_id,
                        "title": title,
                        "url": f"https://www.youtube.com/watch?v={video_id}&t={int(segment_start_time)}s"
                    }
                )
            )

        return results
