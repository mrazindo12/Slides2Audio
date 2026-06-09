"""
Slide2Audio — FastAPI application entry point.

Routing follows the fastapi-router-py skill:
  - Routes are mounted via APIRouter with explicit response_model and status codes.
  - Exception handlers are registered centrally.
"""

from pathlib import Path

from fastapi import FastAPI, APIRouter, UploadFile, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .controllers import ConvertController
from .exceptions import AppException, app_exception_handler, generic_exception_handler
from .config import get_settings
from .models import ConvertResponse

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title=get_settings().app_name,
    description="Convert presentation and document files to spoken MP3 audio.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ---------------------------------------------------------------------------
# Audio directory bootstrap
# ---------------------------------------------------------------------------

_backend_root = Path(__file__).resolve().parent.parent
audio_dir = _backend_root / get_settings().audio_dir
audio_dir.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Router (fastapi-router-py pattern)
# ---------------------------------------------------------------------------

router = APIRouter(prefix="", tags=["conversion"])

_controller = ConvertController()


@router.post(
    "/convert",
    response_model=ConvertResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert a file to audio",
    response_description="Extracted text and the generated audio filename.",
)
async def convert_file(file: UploadFile, voice: str = Form("en-US-AriaNeural")) -> ConvertResponse:
    """
    Upload a `.pptx`, `.pdf`, `.docx`, or `.txt` file.
    Returns the extracted text and a filename for the generated MP3.
    """
    return await _controller.convert_file(file, voice)


@router.get(
    "/audio/{filename}",
    status_code=status.HTTP_200_OK,
    summary="Stream or download a generated audio file",
    response_class=FileResponse,
)
async def get_audio(filename: str) -> FileResponse:
    """Serve the generated MP3 by filename."""
    file_path = _controller.get_audio(filename)
    return FileResponse(file_path, media_type="audio/mpeg")


app.include_router(router)