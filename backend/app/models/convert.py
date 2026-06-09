"""
Pydantic models for the /convert endpoint.

Follows the multi-model pattern (pydantic-models-py skill):
  - ConvertResponse: API response returned to the client
"""

from pydantic import BaseModel, Field


class ConvertResponse(BaseModel):
    """Response model for a successful file-to-audio conversion."""

    text_content: str = Field(
        ...,
        description="The full text extracted from the uploaded file.",
        min_length=1,
    )
    audio_filename: str = Field(
        ...,
        description="The generated MP3 filename, served at GET /audio/{filename}.",
        pattern=r"^[a-f0-9\-]+\.mp3$",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "text_content": "Welcome to this presentation...",
                "audio_filename": "3fa85f64-5717-4562-b3fc-2c963f66afa6.mp3",
            }
        }
    }
