import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    app_name: str = "Slide2Audio"
    audio_dir: str = "audio"
    cors_origins: list = ["http://localhost:5173", "http://127.0.0.1:5173", "*"]
    allowed_extensions: list = [".txt", ".pdf", ".docx", ".pptx"]
    tts_voice: str = "en-US-AriaNeural"
    gemini_api_key: str = ""

    model_config = {
        "env_file": str(_ENV_FILE),
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()