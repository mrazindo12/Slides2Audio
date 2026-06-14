import logging
import httpx
import asyncio

from ..config import get_settings

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Ordered by preference — will try the next model if the current one is rate-limited
FREE_MODELS = [
    "google/gemma-4-31b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "google/gemma-3-27b-it:free",
]


class LLMService:
    def __init__(self):
        self.api_key = get_settings().openrouter_api_key

    async def _call_openrouter(self, model: str, messages: list, temperature: float = 0.7) -> str | None:
        """Make a single request to OpenRouter. Returns text or None."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "Slide2Audio",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def generate_lecture(self, raw_text: str, mode: str = "lecture") -> str | None:
        """
        Convert raw text into a script via OpenRouter (free model).
        Returns None if the LLM is unavailable (no key, error, etc.)
        so the caller can fall back to raw text.
        """
        if not self.api_key:
            logger.warning("No OpenRouter API key configured — skipping LLM step.")
            return None

        if mode == "discussion":
            system_msg = (
                "You are a professional podcast script writer. You write scripts for educational podcasts "
                "with THREE distinct speakers who have a lively, dynamic conversation. "
                "You NEVER write monologues. Every speaker turn is short (1-4 sentences max). "
                "The dialogue has rapid back-and-forth exchanges like a real conversation."
            )
            user_msg = (
                "Write a podcast discussion script with exactly THREE speakers based on the content below.\n\n"
                "=== SPEAKERS ===\n"
                "HOST: The moderator. Introduces topics, asks questions, makes transitions. Warm and curious tone.\n"
                "EXPERT: The knowledgeable one. Explains concepts, provides depth and insights. Confident but approachable.\n"
                "STUDENT: The curious learner. Asks clarifying questions, reacts with surprise or excitement, pushes for simpler explanations.\n\n"
                "=== STRICT RULES ===\n"
                "1. EVERY line MUST start with a speaker tag followed by a colon: HOST: or EXPERT: or STUDENT:\n"
                "2. Each speaker turn must be SHORT — 1 to 4 sentences maximum. NO long paragraphs.\n"
                "3. Generate AT LEAST 25 speaker turns total, alternating between speakers frequently.\n"
                "4. The STUDENT must speak at least 7 times. The HOST must speak at least 7 times. The EXPERT must speak at least 7 times.\n"
                "5. Include natural reactions: \"Wait, really?\", \"Oh that's fascinating!\", \"Hold on, let me make sure I get this...\", \"Exactly!\", \"Great question!\"\n"
                "6. The STUDENT should INTERRUPT and ask follow-ups — don't let the EXPERT monologue.\n"
                "7. NEVER include stage directions, markdown formatting, asterisks, brackets, or parenthetical actions. NO [laughs], (pauses), *gestures*, **bold**, etc.\n"
                "8. Output ONLY the spoken words. This goes directly to a text-to-speech engine.\n\n"
                "=== EXAMPLE FORMAT (follow this structure) ===\n"
                "HOST: Welcome back everyone! Today we're diving into something really interesting.\n"
                "EXPERT: Yeah, this is a topic I'm really excited to break down for you.\n"
                "STUDENT: I've heard about this but honestly, I don't fully understand it yet.\n"
                "HOST: Perfect, that's exactly why we're here. So let's start from the basics.\n"
                "EXPERT: Sure! So the core idea is actually pretty simple.\n"
                "STUDENT: Wait, really? I always thought this was super complicated.\n"
                "EXPERT: It can be, but the foundation is straightforward. Let me explain.\n"
                "HOST: Go for it!\n"
                "EXPERT: So basically, what happens is...\n"
                "STUDENT: Oh, that makes so much more sense now! But what about...\n\n"
                "=== CONTENT TO DISCUSS ===\n"
                f"{raw_text}"
            )
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ]
            temperature = 0.9
        else:
            system_msg = (
                "You are an expert, engaging university lecturer who explains complex material clearly and conversationally."
            )
            user_msg = (
                "Convert the following document/presentation text into a comprehensive lecture script. "
                "Speak directly to the listener as if teaching a live class.\n\n"
                "RULES:\n"
                "1. Use natural conversational transitions between topics.\n"
                "2. Break the lecture into clear paragraphs — separate each paragraph with a blank line.\n"
                "3. Do NOT include ANY stage directions, markdown formatting, or spoken cues like [Pause], [Sigh], or *emphasis*.\n"
                "4. This output goes directly into a Text-To-Speech engine — return ONLY the raw spoken words.\n"
                "5. Make it engaging and easy to follow. Explain jargon and complex ideas.\n\n"
                f"Here is the raw text:\n{raw_text}"
            )
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ]
            temperature = 0.7

        for model in FREE_MODELS:
            # Retry each model up to 3 times with exponential backoff
            for attempt in range(3):
                try:
                    logger.info("Trying model %s (attempt %d)...", model, attempt + 1)
                    text = await self._call_openrouter(model, messages, temperature)

                    if text:
                        logger.info("Success with model %s", model)
                        return text

                    logger.warning("Model %s returned empty — trying next.", model)
                    break  # Empty response = move to next model, don't retry

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        wait = 2 ** attempt * 2  # 2s, 4s, 8s
                        logger.warning(
                            "Rate limited on %s (attempt %d) — waiting %ds...",
                            model, attempt + 1, wait,
                        )
                        await asyncio.sleep(wait)
                        continue  # Retry same model
                    else:
                        logger.warning("HTTP %d on %s — trying next model.", e.response.status_code, model)
                        break  # Non-429 error = move to next model

                except Exception as e:
                    import traceback
                    logger.warning("Error with %s: %s — trying next model.", model, e)
                    logger.error(traceback.format_exc())
                    break

        logger.warning("All free models exhausted — falling back to raw text.")
        return None
