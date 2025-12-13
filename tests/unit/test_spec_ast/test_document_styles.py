"""Tests for document style definitions."""

from wassden.language_types import Language
from wassden.lib.spec_ast.document_styles import (
    DESIGN_STYLE,
    DOCUMENT_STYLES,
    REQUIREMENTS_STYLE,
    TASKS_STYLE,
    get_document_style,
)
from wassden.lib.spec_ast.section_patterns import SectionType


class TestDocumentStyle:
    """Tests for DocumentStyle class."""

    def test_create_validation_rules(self):
        """Test creating validation rule instances from a style."""
        style = REQUIREMENTS_STYLE

        rules = style.create_validation_rules(Language.JAPANESE)

        assert len(rules) > 0
        assert all(hasattr(rule, "validate") for rule in rules)
        assert all(hasattr(rule, "rule_id") for rule in rules)

    def test_create_validation_rules_with_language(self):
        """Test creating validation rules with different languages."""
        style = REQUIREMENTS_STYLE

        ja_rules = style.create_validation_rules(Language.JAPANESE)
        en_rules = style.create_validation_rules(Language.ENGLISH)

        assert len(ja_rules) == len(en_rules)
        assert all(rule.language == Language.JAPANESE for rule in ja_rules)
        assert all(rule.language == Language.ENGLISH for rule in en_rules)


class TestRequirementsStyle:
    """Tests for predefined requirements style."""

    def test_requirements_style_properties(self):
        """Test requirements style has expected properties."""
        style = REQUIREMENTS_STYLE

        assert style.name == "Requirements Document"
        assert len(style.description) > 0
        assert len(style.required_sections) == 8
        assert len(style.validation_rules) >= 3

    def test_requirements_style_required_sections(self):
        """Test requirements style has all required sections."""
        style = REQUIREMENTS_STYLE

        expected_sections = {
            SectionType.OVERVIEW,  # Changed from SUMMARY to OVERVIEW for Japanese "サマリー/概要"
            SectionType.GLOSSARY,
            SectionType.SCOPE,
            SectionType.CONSTRAINTS,
            SectionType.NON_FUNCTIONAL_REQUIREMENTS,  # 非機能要件/非機能要求仕様
            SectionType.KPI,
            SectionType.FUNCTIONAL_REQUIREMENTS,
            SectionType.TESTING_REQUIREMENTS,
        }

        assert set(style.required_sections) == expected_sections

    def test_requirements_style_optional_sections(self):
        """Test requirements style has optional sections."""
        style = REQUIREMENTS_STYLE

        assert SectionType.REFERENCES in style.optional_sections
        assert SectionType.APPENDIX in style.optional_sections


class TestDesignStyle:
    """Tests for predefined design style."""

    def test_design_style_properties(self):
        """Test design style has expected properties."""
        style = DESIGN_STYLE

        assert style.name == "Design Document"
        assert len(style.description) > 0
        assert len(style.required_sections) == 7
        assert len(style.validation_rules) >= 4

    def test_design_style_required_sections(self):
        """Test design style has all required sections."""
        style = DESIGN_STYLE

        expected_sections = {
            SectionType.ARCHITECTURE,
            SectionType.COMPONENT_DESIGN,
            SectionType.DATA,
            SectionType.API,
            SectionType.NON_FUNCTIONAL,
            SectionType.TEST,
            SectionType.TRACEABILITY,
        }

        assert set(style.required_sections) == expected_sections

    def test_design_style_includes_traceability(self):
        """Test design style requires traceability section."""
        style = DESIGN_STYLE

        assert SectionType.TRACEABILITY in style.required_sections


class TestTasksStyle:
    """Tests for predefined tasks style."""

    def test_tasks_style_properties(self):
        """Test tasks style has expected properties."""
        style = TASKS_STYLE

        assert style.name == "Tasks Document"
        assert len(style.description) > 0
        assert len(style.required_sections) == 4
        assert len(style.validation_rules) >= 7

    def test_tasks_style_required_sections(self):
        """Test tasks style has all required sections."""
        style = TASKS_STYLE

        expected_sections = {
            SectionType.OVERVIEW,
            SectionType.TASK_LIST,
            SectionType.DEPENDENCIES,
            SectionType.MILESTONES,
        }

        assert set(style.required_sections) == expected_sections


class TestDocumentStyleRegistry:
    """Tests for document style registry."""

    def test_document_styles_registry(self):
        """Test document styles registry contains all predefined styles."""
        assert "requirements" in DOCUMENT_STYLES
        assert "design" in DOCUMENT_STYLES
        assert "tasks" in DOCUMENT_STYLES

        assert DOCUMENT_STYLES["requirements"] is REQUIREMENTS_STYLE
        assert DOCUMENT_STYLES["design"] is DESIGN_STYLE
        assert DOCUMENT_STYLES["tasks"] is TASKS_STYLE

    def test_get_document_style_by_name(self):
        """Test retrieving document style by name."""
        req_style = get_document_style("requirements")
        design_style = get_document_style("design")
        tasks_style = get_document_style("tasks")

        assert req_style is REQUIREMENTS_STYLE
        assert design_style is DESIGN_STYLE
        assert tasks_style is TASKS_STYLE

    def test_get_document_style_case_insensitive(self):
        """Test getting document style is case insensitive."""
        assert get_document_style("Requirements") is REQUIREMENTS_STYLE
        assert get_document_style("DESIGN") is DESIGN_STYLE
        assert get_document_style("Tasks") is TASKS_STYLE

    def test_get_document_style_unknown(self):
        """Test getting unknown style returns None."""
        assert get_document_style("unknown") is None
        assert get_document_style("") is None
