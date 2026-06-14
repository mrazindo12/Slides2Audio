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

    async def convert_file(self, file: UploadFile, voice: str, mode: str = "lecture") -> ConvertResponse:
        import logging
        logger = logging.getLogger(__name__)

        contents = await file.read()
        extension = Path(file.filename).suffix.lower()
        logger.info("Convert request: file=%s, ext=%s, mode=%s, voice=%s, size=%d bytes",
                     file.filename, extension, mode, voice, len(contents))

        # Step 1: Extract raw text from file
        raw_text = self.parser_service.extract_text(contents, extension)
        logger.info("Extracted text length: %d characters", len(raw_text))

        # Step 2: Try LLM to convert raw text into a script (graceful fallback)
        if mode == "direct":
            final_text = raw_text
        else:
            try:
                lecture_script = await self.llm_service.generate_lecture(raw_text, mode=mode)
                if lecture_script:
                    final_text = lecture_script
                    logger.info("LLM script generated: %d characters", len(final_text))
                else:
                    final_text = raw_text
                    logger.warning("LLM returned None — falling back to raw text")
            except Exception as e:
                logger.error("LLM generation failed: %s — falling back to raw text", e)
                final_text = raw_text

        if not final_text or not final_text.strip():
            from ..exceptions import NoTextExtractedError
            raise NoTextExtractedError()

        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = str(self.audio_dir / audio_filename)

        # Step 3: Run TTS on the final text
        logger.info("Starting TTS generation (%d chars) -> %s", len(final_text), audio_filename)
        await self.tts_service.generate(final_text, audio_path, voice=voice)
        logger.info("TTS generation complete: %s", audio_filename)

        return ConvertResponse(
            text_content=final_text,
            audio_filename=audio_filename,
        )

    def get_audio(self, filename: str) -> Path:
        file_path = self.audio_dir / filename
        if not file_path.exists():
            raise AudioNotFoundError()
        return file_path