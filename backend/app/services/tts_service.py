import asyncio
from pathlib import Path
import edge_tts
from ..exceptions import AudioGenerationError


class TTSService:
    def __init__(self):
        pass

    async def generate(self, text: str, output_path: str, voice: str = "en-US-AriaNeural") -> None:
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
        except Exception as e:
            raise AudioGenerationError(str(e))