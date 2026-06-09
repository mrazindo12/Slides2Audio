import pytest
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO
from pathlib import Path
from fastapi import UploadFile

from app.services.parser_service import ParserService
from app.services.tts_service import TTSService
from app.controllers.convert_controller import ConvertController
from app.exceptions import (
    UnsupportedFileTypeError,
    TextExtractionError,
    NoTextExtractedError,
    AudioGenerationError,
    AudioNotFoundError
)


class TestParserService:
    def setup_method(self):
        self.service = ParserService()

    @pytest.mark.parametrize("extension", [".txt", ".pdf", ".docx", ".pptx"])
    def test_allowed_extensions(self, extension):
        with patch("app.services.parser_service.parse_text") as mock_parse:
            mock_parse.return_value = "test content"
            result = self.service.extract_text(b"test", extension)
            assert result == "test content"

    def test_unsupported_extension(self):
        with pytest.raises(UnsupportedFileTypeError) as exc:
            self.service.extract_text(b"test", ".exe")
        assert exc.value.status_code == 400

    def test_empty_text_raises_error(self):
        with patch("app.services.parser_service.parse_text") as mock_parse:
            mock_parse.return_value = ""
            with pytest.raises(NoTextExtractedError):
                self.service.extract_text(b"test", ".txt")

    def test_text_extraction_error(self):
        with patch("app.services.parser_service.parse_text") as mock_parse:
            mock_parse.side_effect = ValueError("Parse error")
            with pytest.raises(TextExtractionError):
                self.service.extract_text(b"test", ".txt")


class TestTTSService:
    @pytest.mark.asyncio
    async def test_generate_audio(self):
        service = TTSService()

        with patch("app.services.tts_service.edge_tts.Communicate") as mock_communicate:
            mock_instance = AsyncMock()
            mock_communicate.return_value = mock_instance

            await service.generate("test text", "/tmp/test.mp3", voice="en-US-AriaNeural")

            mock_communicate.assert_called_once_with("test text", "en-US-AriaNeural")
            mock_instance.save.assert_called_once_with("/tmp/test.mp3")

    @pytest.mark.asyncio
    async def test_generate_audio_error(self):
        service = TTSService()

        with patch("app.services.tts_service.edge_tts.Communicate") as mock_communicate:
            mock_communicate.side_effect = Exception("TTS error")

            with pytest.raises(AudioGenerationError):
                await service.generate("test", "/tmp/test.mp3")


class TestConvertController:
    def setup_method(self):
        with patch("app.controllers.convert_controller.get_settings") as mock_settings:
            mock_settings.return_value.tts_voice = "TestVoice"
            mock_settings.return_value.audio_dir = "audio"
            mock_settings.return_value.allowed_extensions = [".txt", ".pdf", ".docx", ".pptx"]
            self.controller = ConvertController()

    @pytest.mark.asyncio
    async def test_convert_file(self):
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.txt"
        mock_file.read = AsyncMock(return_value=b"test content")

        with patch.object(self.controller.parser_service, "extract_text", return_value="test content"):
            with patch.object(self.controller.llm_service, "generate_lecture", new=AsyncMock(return_value="test content")):
                with patch.object(self.controller.tts_service, "generate", new=AsyncMock()):
                    result = await self.controller.convert_file(mock_file, voice="en-US-AriaNeural")
                    assert result.text_content == "test content"
                    assert result.audio_filename.endswith(".mp3")

    @pytest.mark.asyncio
    async def test_get_audio_not_found(self):
        with pytest.raises(AudioNotFoundError):
            self.controller.get_audio("nonexistent.mp3")