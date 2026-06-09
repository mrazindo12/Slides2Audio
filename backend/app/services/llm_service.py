import asyncio
import logging

from google import genai
from ..config import get_settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        api_key = get_settings().gemini_api_key
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model_name = "gemini-2.0-flash"

    async def generate_lecture(self, raw_text: str) -> str | None:
        """
        Attempt to convert raw text into a lecture script via Gemini.
        Returns None if the LLM is unavailable (no key, quota exhausted, etc.)
        so the caller can fall back to raw text.
        """
        if not self.client:
            logger.warning("No Gemini API key configured — skipping LLM step.")
            return None

        prompt = (
            "You are an expert, engaging university lecturer. "
            "Please read the following raw document/presentation text and convert it into a comprehensive lecture script. "
            "Explain concepts clearly, use natural conversational transitions, and speak directly to the listener as if you are teaching a live class. "
            "EXTREMELY IMPORTANT: Do not include ANY stage directions, markdown formatting, or spoken cues (like [Pause], [Sigh], or Speaker 1:). "
            "This output will be fed directly into a Text-To-Speech engine, so return ONLY the raw spoken words you want the teacher to say.\n\n"
            f"Here is the raw text:\n{raw_text}"
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt
            )

            if response.text:
                return response.text

            logger.warning("LLM returned empty response — falling back to raw text.")
            return None
        except Exception as e:
            logger.warning("LLM generation failed: %s — falling back to raw text.", e)
            return None
