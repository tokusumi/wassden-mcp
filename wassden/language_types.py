"""Language type definition to avoid circular imports."""

from enum import Enum


class Language(str, Enum):
    """Supported languages for output."""

    JAPANESE = "ja"
    ENGLISH = "en"
