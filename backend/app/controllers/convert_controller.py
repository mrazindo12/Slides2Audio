import uuid
from pathlib import Path
from fastapi import UploadFile
from ..services import ParserService, TTSService, LLMService
from ..config import get_settings
from ..models import ConvertResponse
from ..exceptions import AudioNotFoundError


class ConvertController:
    def __init__(self):
        self.parser_service = ParserService()
        self.tts_service = TTSService()
        self.llm_service = LLMService()
        # Resolve audio_dir relative to backend root (parent of the 'app' package)
        backend_root = Path(__file__).resolve().parent.parent.parent
        self.audio_dir = backend_root / get_settings().audio_dir

    async def convert_file(self, file: UploadFile, voice: str) -> ConvertResponse:
        contents = await file.read()
        extension = Path(file.filename).suffix.lower()

        # Step 1: Extract raw text from file
        raw_text = self.parser_service.extract_text(contents, extension)

        # Step 2: Try LLM to convert raw text into a lecture script (graceful fallback)
        lecture_script = await self.llm_service.generate_lecture(raw_text)
        final_text = lecture_script if lecture_script else raw_text

        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = str(self.audio_dir / audio_filename)

        # Step 3: Run TTS on the final text
        await self.tts_service.generate(final_text, audio_path, voice=voice)

        return ConvertResponse(
            text_content=final_text,
            audio_filename=audio_filename,
        )

    def get_audio(self, filename: str) -> Path:
        file_path = self.audio_dir / filename
        if not file_path.exists():
            raise AudioNotFoundError()
        return file_path