"""Unit tests for section pattern configuration."""

from wassden.lib.spec_ast.section_patterns import (
    API_PATTERN,
    FUNCTIONAL_REQUIREMENTS_PATTERN,
    GLOSSARY_PATTERN,
    OVERVIEW_PATTERN,
    SUMMARY_PATTERN,
    TASK_LIST_PATTERN,
    SectionType,
    classify_section,
    get_section_pattern,
)


class TestSectionPatterns:
    """Tests for section pattern objects."""

    def test_functional_requirements_pattern(self) -> None:
        """Test functional requirements pattern object."""
        assert FUNCTIONAL_REQUIREMENTS_PATTERN.section_type == SectionType.FUNCTIONAL_REQUIREMENTS
        assert "機能要件" in FUNCTIONAL_REQUIREMENTS_PATTERN.ja_patterns
        assert "Functional Requirements" in FUNCTIONAL_REQUIREMENTS_PATTERN.en_patterns
        assert FUNCTIONAL_REQUIREMENTS_PATTERN.contains_requirements is True
        assert FUNCTIONAL_REQUIREMENTS_PATTERN.contains_tasks is False

    def test_task_list_pattern(self) -> None:
        """Test task list pattern object."""
        assert TASK_LIST_PATTERN.section_type == SectionType.TASK_LIST
        assert "タスク一覧" in TASK_LIST_PATTERN.ja_patterns
        assert "Task List" in TASK_LIST_PATTERN.en_patterns
        assert TASK_LIST_PATTERN.contains_requirements is False
        assert TASK_LIST_PATTERN.contains_tasks is True

    def test_summary_pattern(self) -> None:
        """Test summary pattern object (deprecated)."""
        assert SUMMARY_PATTERN.section_type == SectionType.SUMMARY
        # SUMMARY pattern is deprecated - "サマリー" moved to OVERVIEW
        assert len(SUMMARY_PATTERN.ja_patterns) == 0
        assert "Summary" in SUMMARY_PATTERN.en_patterns
        assert SUMMARY_PATTERN.contains_requirements is False
        assert SUMMARY_PATTERN.contains_tasks is False

    def test_overview_pattern(self) -> None:
        """Test overview pattern object."""
        assert OVERVIEW_PATTERN.section_type == SectionType.OVERVIEW
        assert "概要" in OVERVIEW_PATTERN.ja_patterns
        assert "サマリー" in OVERVIEW_PATTERN.ja_patterns  # Moved from SUMMARY
        assert "Overview" in OVERVIEW_PATTERN.en_patterns

    def test_glossary_pattern(self) -> None:
        """Test glossary pattern object."""
        assert GLOSSARY_PATTERN.section_type == SectionType.GLOSSARY
        assert "用語集" in GLOSSARY_PATTERN.ja_patterns
        assert "Glossary" in GLOSSARY_PATTERN.en_patterns

    def test_api_pattern(self) -> None:
        """Test API pattern object."""
        assert API_PATTERN.section_type == SectionType.API
        assert "API" in API_PATTERN.ja_patterns
        assert "API" in API_PATTERN.en_patterns


class TestClassifySection:
    """Tests for section classification."""

    def test_classify_japanese_functional_requirements(self) -> None:
        """Test classifying Japanese functional requirements section."""
        result = classify_section("機能要件", "ja")
        assert result == SectionType.FUNCTIONAL_REQUIREMENTS

        result = classify_section("6. 機能要件（EARS）", "ja")
        assert result == SectionType.FUNCTIONAL_REQUIREMENTS

    def test_classify_english_functional_requirements(self) -> None:
        """Test classifying English functional requirements section."""
        result = classify_section("Functional Requirements", "en")
        assert result == SectionType.FUNCTIONAL_REQUIREMENTS

        result = classify_section("6. Functional Requirements", "en")
        assert result == SectionType.FUNCTIONAL_REQUIREMENTS

    def test_classify_japanese_task_list(self) -> None:
        """Test classifying Japanese task list section."""
        result = classify_section("タスク一覧", "ja")
        assert result == SectionType.TASK_LIST

        result = classify_section("2. タスク一覧", "ja")
        assert result == SectionType.TASK_LIST

    def test_classify_english_task_list(self) -> None:
        """Test classifying English task list section."""
        result = classify_section("Task List", "en")
        assert result == SectionType.TASK_LIST

        result = classify_section("2. Task List", "en")
        assert result == SectionType.TASK_LIST

    def test_classify_japanese_glossary(self) -> None:
        """Test classifying Japanese glossary section."""
        result = classify_section("用語集", "ja")
        assert result == SectionType.GLOSSARY

        result = classify_section("1. 用語集", "ja")
        assert result == SectionType.GLOSSARY

    def test_classify_english_glossary(self) -> None:
        """Test classifying English glossary section."""
        result = classify_section("Glossary", "en")
        assert result == SectionType.GLOSSARY

    def test_classify_unknown_section(self) -> None:
        """Test classifying unknown section."""
        result = classify_section("Unknown Section", "en")
        assert result == SectionType.UNKNOWN

        result = classify_section("不明なセクション", "ja")
        assert result == SectionType.UNKNOWN

    def test_classify_with_extra_whitespace(self) -> None:
        """Test classifying with extra whitespace."""
        result = classify_section("  機能要件  ", "ja")
        assert result == SectionType.FUNCTIONAL_REQUIREMENTS

        result = classify_section("  Task List  ", "en")
        assert result == SectionType.TASK_LIST


class TestGetSectionPattern:
    """Tests for getting section patterns."""

    def test_get_functional_requirements_pattern(self) -> None:
        """Test getting functional requirements pattern."""
        pattern = get_section_pattern(SectionType.FUNCTIONAL_REQUIREMENTS)
        assert pattern is not None
        assert pattern == FUNCTIONAL_REQUIREMENTS_PATTERN
        assert pattern.contains_requirements is True

    def test_get_task_list_pattern(self) -> None:
        """Test getting task list pattern."""
        pattern = get_section_pattern(SectionType.TASK_LIST)
        assert pattern is not None
        assert pattern == TASK_LIST_PATTERN
        assert pattern.contains_tasks is True

    def test_get_summary_pattern(self) -> None:
        """Test getting summary pattern."""
        pattern = get_section_pattern(SectionType.SUMMARY)
        assert pattern is not None
        assert pattern == SUMMARY_PATTERN

    def test_get_unknown_pattern(self) -> None:
        """Test getting unknown pattern returns None."""
        pattern = get_section_pattern(SectionType.UNKNOWN)
        assert pattern is None
