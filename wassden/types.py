"""Common type definitions for wassden."""

from enum import Enum

from pydantic import BaseModel


class Language(str, Enum):
    """Supported languages for output."""

    JAPANESE = "ja"
    ENGLISH = "en"


class TextContent(BaseModel):
    """Text content structure for handler responses."""

    type: str = "text"
    text: str


class HandlerResponse(BaseModel):
    """Standard response structure for all handlers."""

    content: list[TextContent]
