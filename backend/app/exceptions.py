from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UnsupportedFileTypeError(AppException):
    def __init__(self, extension: str):
        super().__init__(f"Unsupported file type: {extension}", 400)


class TextExtractionError(AppException):
    def __init__(self, message: str):
        super().__init__(f"Failed to extract text: {message}", 400)


class NoTextExtractedError(AppException):
    def __init__(self):
        super().__init__("No text extracted from the file", 400)


class AudioGenerationError(AppException):
    def __init__(self, message: str):
        super().__init__(f"Failed to generate audio: {message}", 500)


class AudioNotFoundError(AppException):
    def __init__(self):
        super().__init__("Audio file not found", 404)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    import logging
    import traceback
    logger = logging.getLogger(__name__)
    logger.error("Unhandled exception: %s\n%s", exc, traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {exc}"}
    )