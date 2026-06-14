import asyncio
import os
import uuid
from pathlib import Path
import logging
import edge_tts
from ..exceptions import AudioGenerationError

logger = logging.getLogger(__name__)

# Dynamic speaker-to-voice mapping based on the chosen primary EXPERT voice
VOICE_MAPS = {
    "en-US-AriaNeural": {"HOST": "en-US-GuyNeural", "EXPERT": "en-US-AriaNeural", "STUDENT": "en-GB-SoniaNeural"},
    "en-US-GuyNeural": {"HOST": "en-US-AriaNeural", "EXPERT": "en-US-GuyNeural", "STUDENT": "en-GB-RyanNeural"},
    "en-GB-SoniaNeural": {"HOST": "en-GB-RyanNeural", "EXPERT": "en-GB-SoniaNeural", "STUDENT": "en-US-AriaNeural"},
    "en-GB-RyanNeural": {"HOST": "en-GB-SoniaNeural", "EXPERT": "en-GB-RyanNeural", "STUDENT": "en-US-GuyNeural"},
    "en-AU-NatashaNeural": {"HOST": "en-AU-WilliamNeural", "EXPERT": "en-AU-NatashaNeural", "STUDENT": "en-US-AriaNeural"},
    "en-AU-WilliamNeural": {"HOST": "en-AU-NatashaNeural", "EXPERT": "en-AU-WilliamNeural", "STUDENT": "en-US-GuyNeural"},
}


class TTSService:
    # Limit concurrent edge-tts connections to avoid socket timeouts
    _semaphore = asyncio.Semaphore(3)

    def __init__(self):
        pass

    async def _generate_chunk(self, index: int, voice: str, text: str, temp_dir: Path) -> Path:
        """Helper to generate a single speech chunk file with retry logic."""
        chunk_path = temp_dir / f"chunk_{index:04d}.mp3"

        for attempt in range(3):
            try:
                async with self._semaphore:
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(str(chunk_path))
                return chunk_path
            except Exception as e:
                if attempt < 2:
                    wait = (attempt + 1) * 2  # 2s, 4s
                    logger.warning(
                        "TTS chunk %d failed (attempt %d): %s — retrying in %ds...",
                        index, attempt + 1, e, wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    logger.error("TTS chunk %d failed after 3 attempts: %s", index, e)
                    raise

        return chunk_path  # unreachable, but satisfies type checker

    async def generate(self, text: str, output_path: str, voice: str = "en-US-AriaNeural") -> None:
        try:
            import re
            # Regex matching optional markdown formatting (like **, *, __, _) and whitespace around speaker names
            speaker_pattern = re.compile(r'^(?:\*\*|\*|__|_)?\s*(HOST|EXPERT|STUDENT)\s*(?:\*\*|\*|__|_)?\s*:\s*(.*)$', re.IGNORECASE)

            lines = text.split('\n')
            turns = []
            current_speaker = None
            current_content = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this line starts a new speaker turn
                match = speaker_pattern.match(line)
                
                if match:
                    if current_speaker and current_content:
                        turns.append((current_speaker, " ".join(current_content)))
                    current_speaker = match.group(1).upper()
                    current_content = [match.group(2).strip()]
                else:
                    if current_speaker:
                        current_content.append(line)
                    else:
                        # Fallback default speaker if first lines lack tag
                        current_speaker = "HOST"
                        current_content.append(line)

            if current_speaker and current_content:
                turns.append((current_speaker, " ".join(current_content)))

            # If no conversational turns were detected (less than 2 turns, or no EXPERT/STUDENT tags),
            # fall back to standard single-voice synthesis.
            has_discussion = len(turns) >= 2 and any(t[0] in ["EXPERT", "STUDENT"] for t in turns)
            
            if not has_discussion:
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
                return

            # Multi-voice synthesis!
            logger.info("Generating %d discussion turns with multi-voice TTS...", len(turns))

            # Select the voice map matching chosen primary voice
            voice_map = VOICE_MAPS.get(voice, VOICE_MAPS["en-US-AriaNeural"])

            # Setup temp directory in the same folder as the output path
            output_dir = Path(output_path).parent
            temp_dir = output_dir / f"temp_tts_{uuid.uuid4()}"
            temp_dir.mkdir(exist_ok=True)

            try:
                tasks = []
                for idx, (speaker, speech_text) in enumerate(turns):
                    sp_voice = voice_map.get(speaker, voice_map["HOST"])
                    tasks.append(self._generate_chunk(idx, sp_voice, speech_text, temp_dir))
                
                # Run speech synthesis with limited concurrency (semaphore controls it)
                chunk_paths = await asyncio.gather(*tasks)

                # Concatenate all generated MP3 chunks sequentially
                with open(output_path, "wb") as outfile:
                    for chunk_path in chunk_paths:
                        if chunk_path.exists():
                            with open(chunk_path, "rb") as infile:
                                outfile.write(infile.read())
            
            finally:
                # Thorough clean up of temp files and directories
                for chunk_file in temp_dir.glob("*.mp3"):
                    try:
                        chunk_file.unlink()
                    except Exception as e:
                        logger.error("Failed to delete temp chunk %s: %s", chunk_file, e)
                try:
                    temp_dir.rmdir()
                except Exception as e:
                    logger.error("Failed to delete temp directory %s: %s", temp_dir, e)

        except Exception as e:
            raise AudioGenerationError(str(e))