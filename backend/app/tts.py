import edge_tts
import asyncio


async def generate_audio(text: str, output_path: str, voice: str = "en-US-AriaNeural"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)