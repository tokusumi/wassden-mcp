"""Language detection utilities for automatic language determination."""

import pycld2 as cld2  # type: ignore

from wassden.types import Language

# Spec document section patterns for language detection
JAPANESE_SPEC_PATTERNS = [
    "# プロジェクト",
    "## 概要",
    "## 要求事項",
    "## 機能要求",
    "## 非機能要求",
    "## システム設計",
    "## アーキテクチャ",
    "## データ設計",
    "## タスク",
    "## 依存関係",
    "## マイルストーン",
    "## リスク",
    "# 仕様書",
    "# 設計書",
    "# タスク一覧",
]

ENGLISH_SPEC_PATTERNS = [
    "# Project",
    "## Overview",
    "## Requirements",
    "## Functional Requirements",
    "## Non-Functional Requirements",
    "## System Design",
    "## Architecture",
    "## Data Design",
    "## Tasks",
    "## Dependencies",
    "## Milestones",
    "## Risks",
    "# Specification",
    "# Design Document",
    "# Task List",
]


def detect_language_from_spec_content(content: str) -> Language:
    """Detect language from spec document content by checking section patterns.

    This is optimized for spec documents with known section patterns,
    making it more reliable and faster than general language detection.

    Args:
        content: Spec document content to analyze

    Returns:
        Language.JAPANESE if Japanese patterns detected, Language.ENGLISH if English patterns detected,
        defaults to Language.JAPANESE if undetermined
    """
    if not content:
        return Language.JAPANESE  # Default to Japanese

    # Count pattern matches for each language
    japanese_matches = sum(1 for pattern in JAPANESE_SPEC_PATTERNS if pattern in content)
    english_matches = sum(1 for pattern in ENGLISH_SPEC_PATTERNS if pattern in content)

    # If English patterns are significantly more common, use English
    if english_matches > japanese_matches:
        return Language.ENGLISH

    # Default to Japanese (backward compatibility)
    return Language.JAPANESE


def detect_language_from_content(content: str) -> Language:
    """Detect language from document content using pycld2.

    Args:
        content: Document content to analyze

    Returns:
        Language.JAPANESE if Japanese detected, Language.ENGLISH if English,
        defaults to Language.JAPANESE if undetermined
    """
    if not content:
        return Language.JAPANESE  # Default to Japanese

    try:
        # Use pycld2 to detect language
        # Returns: (isReliable, textBytesFound, details)
        # details is a list of (languageName, languageCode, percent, score)
        _, _, details = cld2.detect(content)

        if details:
            # Get the primary detected language
            primary_lang = details[0][1]  # languageCode

            # Map detected language to our supported languages
            if primary_lang == "ja":
                return Language.JAPANESE
            if primary_lang == "en":
                return Language.ENGLISH
            # Default to Japanese for any other language
            return Language.JAPANESE
    except Exception:
        # If detection fails, default to Japanese
        pass

    return Language.JAPANESE  # Default to Japanese


def detect_language_from_user_input(user_input: str) -> Language:
    """Detect language from user input text using pycld2.

    Args:
        user_input: User input text to analyze

    Returns:
        Language.JAPANESE if Japanese detected, Language.ENGLISH if English,
        defaults to Language.JAPANESE if undetermined
    """
    if not user_input:
        return Language.JAPANESE  # Default to Japanese

    try:
        # Use pycld2 to detect language
        _, _, details = cld2.detect(user_input)

        if details:
            # Get the primary detected language
            primary_lang = details[0][1]  # languageCode

            # Map detected language to our supported languages
            if primary_lang == "ja":
                return Language.JAPANESE
            if primary_lang == "en":
                return Language.ENGLISH
            # For backward compatibility, default to Japanese
            return Language.JAPANESE
    except Exception:
        # If detection fails, default to Japanese
        pass

    # For backward compatibility, default to Japanese
    return Language.JAPANESE


def determine_language(
    explicit_language: Language | None = None,
    content: str | None = None,
    user_input: str | None = None,
    is_spec_document: bool = False,
) -> Language:
    """Determine the appropriate language to use.

    Priority order:
    1. Explicit language parameter if provided
    2. Language detected from content if provided (using spec patterns if is_spec_document=True)
    3. Language detected from user input if provided
    4. Default to Japanese

    Args:
        explicit_language: Explicitly specified language (Language enum only)
        content: Document content to analyze for language detection
        user_input: User input to analyze for language detection
        is_spec_document: True if content is a spec document (uses pattern-based detection)

    Returns:
        The determined language (Language enum)
    """
    # Handle explicit language specification
    if explicit_language is not None:
        return explicit_language

    # Try to detect from content
    if content:
        return detect_language_from_spec_content(content) if is_spec_document else detect_language_from_content(content)

    # Try to detect from user input
    if user_input:
        return detect_language_from_user_input(user_input)

    # Default fallback
    return Language.JAPANESE
