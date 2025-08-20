"""Core internationalization functionality."""

import json
import os
from pathlib import Path
from typing import Any

from wassden.types import Language


class I18n:
    """Internationalization handler for wassden."""

    def __init__(self, language: Language | str = Language.JAPANESE) -> None:
        """Initialize i18n with specified language.

        Args:
            language: Language code (Language enum or string)
        """
        if isinstance(language, Language):
            self.language = language.value
        else:
            self.language = language
        self._translations: dict[str, Any] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        """Load translations for the current language."""
        locale_dir = Path(__file__).parent / "locales" / self.language

        if not locale_dir.exists():
            # Fallback to English if language not found
            self.language = "en"
            locale_dir = Path(__file__).parent / "locales" / "en"

        # Load all JSON files in the locale directory
        for json_file in locale_dir.glob("*.json"):
            with json_file.open(encoding="utf-8") as f:
                namespace = json_file.stem
                self._translations[namespace] = json.load(f)

    def t(self, key: str, **kwargs: Any) -> Any:
        """Translate a key with optional formatting.

        Args:
            key: Translation key in format "namespace.key" or "namespace.nested.key"
            **kwargs: Format parameters for string formatting

        Returns:
            Translated value (string, list, or dict)
        """
        parts = key.split(".")
        min_key_parts = 2
        if len(parts) < min_key_parts:
            return key  # Return key if no namespace

        namespace = parts[0]
        key_path = parts[1:]

        if namespace not in self._translations:
            return key  # Return original key if namespace not found

        translation = self._translations[namespace]

        # Navigate nested keys
        for key_part in key_path:
            if not (isinstance(translation, dict) and key_part in translation):
                return key  # Return original key if path not found
            translation = translation[key_part]

        # Handle different translation types
        if isinstance(translation, str):
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                return translation

        # Return lists and dicts as-is, everything else returns the key
        return translation if isinstance(translation, list | dict) else key

    def set_language(self, language: Language) -> None:
        """Change the current language and reload translations.

        Args:
            language: New language code (Language enum)
        """
        # Handle both string and Language enum
        self.language = language.value if hasattr(language, "value") else language
        self._translations = {}
        self._load_translations()


class _I18nSingleton:
    """Singleton holder for i18n instance."""

    def __init__(self) -> None:
        self._instance: I18n | None = None

    def get(self, language: Language | None = None) -> I18n:
        """Get or create the i18n instance."""
        if self._instance is None:
            # Detect language from environment
            if language is None:
                env_lang = os.getenv("WASSDEN_LANG", "ja") or "ja"
                self._instance = I18n(env_lang)
            else:
                self._instance = I18n(language)
        elif language is not None:
            # Handle both string and Language enum
            lang_value = language.value if hasattr(language, "value") else language
            if self._instance.language != lang_value:
                self._instance.set_language(language)

        return self._instance


_singleton = _I18nSingleton()


def get_i18n(language: Language | None = None) -> I18n:
    """Get or create the global i18n instance.

    Args:
        language: Language to set (if None, uses existing or defaults to 'ja')

    Returns:
        I18n instance
    """
    return _singleton.get(language)
