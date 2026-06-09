"""
Request/Response validators for the API.

Note: ConvertResponse is defined in app.models.convert and should be
imported from there. This module is reserved for any additional
validation schemas.
"""

from pydantic import BaseModel, Field


class ConvertRequest(BaseModel):
    """Placeholder for future request body validation."""
    pass


class AudioResponse(BaseModel):
    """Placeholder for future audio metadata response."""
    pass