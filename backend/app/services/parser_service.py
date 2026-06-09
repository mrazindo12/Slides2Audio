import io
from typing import Optional
from ..parse import extract_text as parse_text
from ..exceptions import (
    UnsupportedFileTypeError,
    TextExtractionError,
    NoTextExtractedError
)


class ParserService:
    ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".pptx"}

    def extract_text(self, file_bytes: bytes, extension: str) -> str:
        if extension.lower() not in self.ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(extension)
        
        try:
            text = parse_text(file_bytes, extension)
        except ValueError as e:
            raise TextExtractionError(str(e))
        
        if not text or not text.strip():
            raise NoTextExtractedError()
        
        return text