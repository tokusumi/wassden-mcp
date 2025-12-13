"""Tests for validation engine."""

import pytest

from wassden.language_types import Language
from wassden.lib.spec_ast.blocks import DocumentBlock, SectionBlock
from wassden.lib.spec_ast.document_styles import REQUIREMENTS_STYLE, DocumentStyle
from wassden.lib.spec_ast.section_patterns import SectionType
from wassden.lib.spec_ast.structure_rules import RequirementsStructureRule
from wassden.lib.spec_ast.validation_engine import ValidationEngine


class TestValidationEngine:
    """Tests for ValidationEngine class."""

    def test_initialization(self):
        """Test engine initialization."""
        engine = ValidationEngine(Language.JAPANESE)

        assert engine.language == Language.JAPANESE
        assert engine.context.language == Language.JAPANESE

    def test_validate_requirements_with_style(self):
        """Test validating requirements document."""
        engine = ValidationEngine()

        # Create a minimal valid requirements document
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")

        # Add all required sections
        for section_type in REQUIREMENTS_STYLE.required_sections:
            section = SectionBlock(
                line_start=10,
                line_end=20,
                raw_content=f"## {section_type.value}",
                section_type=section_type,
                normalized_title=section_type.value,
                level=2,
            )
            document.children.append(section)

        results = engine.validate_requirements(document)

        assert len(results) > 0
        assert all(result.is_valid for result in results)

    def test_validate_with_style_by_name(self):
        """Test validating document using style name."""
        engine = ValidationEngine()

        # Create a minimal valid requirements document
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")

        # Add all required sections
        for section_type in REQUIREMENTS_STYLE.required_sections:
            section = SectionBlock(
                line_start=10,
                line_end=20,
                raw_content=f"## {section_type.value}",
                section_type=section_type,
                normalized_title=section_type.value,
                level=2,
            )
            document.children.append(section)

        results = engine.validate_with_style(document, "requirements")

        assert len(results) > 0
        assert all(result.is_valid for result in results)

    def test_validate_with_unknown_style_name(self):
        """Test validating with unknown style name raises error."""
        engine = ValidationEngine()
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Test")

        with pytest.raises(ValueError, match="Unknown document style"):
            engine.validate_with_style(document, "unknown_style")

    def test_validate_document_with_custom_style(self):
        """Test validating with custom document style."""
        engine = ValidationEngine()

        # Create a custom style with only structure rule
        custom_style = DocumentStyle(
            name="Custom Style",
            description="Test style",
            required_sections=[SectionType.SUMMARY],
            validation_rules=[RequirementsStructureRule],
        )

        # Create document without required section
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Test")

        results = engine.validate_document(document, custom_style)

        assert len(results) > 0
        assert not results[0].is_valid  # Should fail due to missing section

    def test_get_validation_summary(self):
        """Test getting validation summary."""
        engine = ValidationEngine()

        # Create a document missing required sections
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")

        results = engine.validate_requirements(document)
        summary = engine.get_validation_summary(results)

        assert "isValid" in summary
        assert "totalRules" in summary
        assert "passedRules" in summary
        assert "failedRules" in summary
        assert "totalErrors" in summary
        assert "errors" in summary
        assert "results" in summary

        assert summary["isValid"] is False  # Missing sections
        assert summary["totalRules"] == len(results)
        assert summary["totalErrors"] > 0

    def test_set_context_documents(self):
        """Test setting context documents for cross-reference validation."""
        engine = ValidationEngine()

        req_doc = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")
        design_doc = DocumentBlock(line_start=1, line_end=100, raw_content="# Design")
        tasks_doc = DocumentBlock(line_start=1, line_end=100, raw_content="# Tasks")

        engine.set_requirements_document(req_doc)
        engine.set_design_document(design_doc)
        engine.set_tasks_document(tasks_doc)

        assert engine.context.requirements_doc is req_doc
        assert engine.context.design_doc is design_doc
        assert engine.context.tasks_doc is tasks_doc

    def test_validate_requirements_missing_sections(self):
        """Test validating requirements with missing sections."""
        engine = ValidationEngine()

        # Create document with only one section
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")
        section = SectionBlock(
            line_start=10,
            line_end=20,
            raw_content="## Summary",
            section_type=SectionType.SUMMARY,
            normalized_title="summary",
            level=2,
        )
        document.children.append(section)

        results = engine.validate_requirements(document)

        # Should have at least one failure (structure rule)
        structure_results = [r for r in results if "Structure" in r.rule_name]
        assert len(structure_results) > 0
        assert not structure_results[0].is_valid
        assert len(structure_results[0].errors) > 0
