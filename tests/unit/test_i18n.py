"""Tests for i18n functionality."""

from wassden.i18n import I18n, get_i18n


class TestI18n:
    """Test i18n core functionality."""

    def test_i18n_japanese_default(self) -> None:
        """Test that Japanese is the default language."""
        i18n = I18n()
        assert i18n.language == "ja"

    def test_i18n_japanese_initialization(self) -> None:
        """Test Japanese language initialization."""
        i18n = I18n("ja")
        assert i18n.language == "ja"

    def test_i18n_fallback_to_english(self) -> None:
        """Test fallback to English for unsupported language."""
        i18n = I18n("unsupported")
        assert i18n.language == "en"

    def test_translation_english(self) -> None:
        """Test English translation."""
        i18n = I18n("en")
        translation = i18n.t("completeness.questions.technology")
        assert "technology" in translation.lower()
        assert len(translation) > 0

    def test_translation_japanese(self) -> None:
        """Test Japanese translation."""
        i18n = I18n("ja")
        translation = i18n.t("completeness.questions.technology")
        assert "技術" in translation
        assert len(translation) > 0

    def test_translation_with_formatting(self) -> None:
        """Test translation with string formatting."""
        i18n = I18n("en")
        translation = i18n.t("completeness.prompts.base", user_input="test input")
        assert "test input" in translation

    def test_translation_missing_key(self) -> None:
        """Test behavior when translation key is missing."""
        i18n = I18n("en")
        result = i18n.t("nonexistent.key")
        assert result == "nonexistent.key"

    def test_translation_missing_namespace(self) -> None:
        """Test behavior when namespace is missing."""
        i18n = I18n("en")
        result = i18n.t("missing_namespace.key")
        assert result == "missing_namespace.key"

    def test_translation_invalid_key_format(self) -> None:
        """Test behavior with invalid key format."""
        i18n = I18n("en")
        result = i18n.t("invalid_key")
        assert result == "invalid_key"

    def test_set_language(self) -> None:
        """Test changing language dynamically."""
        i18n = I18n("en")
        assert i18n.language == "en"

        i18n.set_language("ja")
        assert i18n.language == "ja"

        # Test translation works in new language
        translation = i18n.t("completeness.questions.technology")
        assert "技術" in translation

    def test_keywords_list_english(self) -> None:
        """Test that keywords return a list in English."""
        i18n = I18n("en")
        keywords = i18n.t("completeness.keywords.technology")
        assert isinstance(keywords, list)
        assert "technology" in keywords

    def test_keywords_list_japanese(self) -> None:
        """Test that keywords return a list in Japanese."""
        i18n = I18n("ja")
        keywords = i18n.t("completeness.keywords.technology")
        assert isinstance(keywords, list)
        assert "技術スタック" in keywords


class TestI18nGlobal:
    """Test global i18n instance management."""

    def test_get_i18n_default(self) -> None:
        """Test getting default i18n instance."""
        i18n = get_i18n()
        assert isinstance(i18n, I18n)
        assert i18n.language == "ja"

    def test_get_i18n_with_language(self) -> None:
        """Test getting i18n instance with specific language."""
        i18n = get_i18n("ja")
        assert i18n.language == "ja"

    def test_get_i18n_singleton(self) -> None:
        """Test that get_i18n returns the same instance."""
        i18n1 = get_i18n("ja")
        i18n2 = get_i18n()
        assert i18n1 is i18n2

    def test_get_i18n_language_change(self) -> None:
        """Test that get_i18n can change language of existing instance."""
        i18n1 = get_i18n("en")
        assert i18n1.language == "en"

        i18n2 = get_i18n("ja")
        assert i18n2.language == "ja"
        assert i18n1 is i18n2  # Same instance
        assert i18n1.language == "ja"  # Language changed
