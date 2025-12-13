"""Tests for validation rule base classes."""


from wassden.language_types import Language
from wassden.lib.spec_ast.blocks import DocumentBlock, SectionBlock
from wassden.lib.spec_ast.validation_rules import (
    BlockLocation,
    Severity,
    ValidationContext,
    ValidationError,
    ValidationResult,
)


class TestBlockLocation:
    """Tests for BlockLocation class."""

    def test_from_block(self):
        """Test creating BlockLocation from a block."""
        # Create a simple section block
        section = SectionBlock(
            line_start=5,
            line_end=10,
            raw_content="## Test Section",
            level=2,
            title="Test Section",
            normalized_title="Test Section",
        )

        location = BlockLocation.from_block(section)

        assert location.line_start == 5
        assert location.line_end == 10
        assert isinstance(location.section_path, list)


class TestValidationError:
    """Tests for ValidationError class."""

    def test_to_dict_without_location(self):
        """Test converting error to dict without location."""
        error = ValidationError(message="Test error", severity=Severity.ERROR)

        result = error.to_dict()

        assert result["message"] == "Test error"
        assert result["severity"] == "error"
        assert "location" not in result

    def test_to_dict_with_location(self):
        """Test converting error to dict with location."""
        location = BlockLocation(line_start=5, line_end=10, section_path=["Section 1"])
        error = ValidationError(message="Test error", location=location, severity=Severity.WARNING)

        result = error.to_dict()

        assert result["message"] == "Test error"
        assert result["severity"] == "warning"
        assert result["location"]["line_start"] == 5
        assert result["location"]["line_end"] == 10
        assert result["location"]["section_path"] == ["Section 1"]


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_to_dict_valid(self):
        """Test converting result to dict when valid."""
        result = ValidationResult(rule_id="TEST-001", rule_name="Test Rule", is_valid=True, errors=[])

        result_dict = result.to_dict()

        assert result_dict["rule_id"] == "TEST-001"
        assert result_dict["rule_name"] == "Test Rule"
        assert result_dict["is_valid"] is True
        assert result_dict["errors"] == []

    def test_to_dict_with_errors(self):
        """Test converting result to dict with errors."""
        errors = [
            ValidationError(message="Error 1", severity=Severity.ERROR),
            ValidationError(message="Error 2", severity=Severity.WARNING),
        ]
        result = ValidationResult(rule_id="TEST-002", rule_name="Test Rule 2", is_valid=False, errors=errors)

        result_dict = result.to_dict()

        assert result_dict["rule_id"] == "TEST-002"
        assert result_dict["is_valid"] is False
        assert len(result_dict["errors"]) == 2
        assert result_dict["errors"][0]["message"] == "Error 1"
        assert result_dict["errors"][1]["message"] == "Error 2"


class TestValidationContext:
    """Tests for ValidationContext class."""

    def test_initialization(self):
        """Test context initialization."""
        context = ValidationContext(Language.JAPANESE)

        assert context.language == Language.JAPANESE
        assert context.requirements_doc is None
        assert context.design_doc is None
        assert context.tasks_doc is None

    def test_set_documents(self):
        """Test setting documents in context."""
        context = ValidationContext()

        req_doc = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")
        design_doc = DocumentBlock(line_start=1, line_end=100, raw_content="# Design")
        tasks_doc = DocumentBlock(line_start=1, line_end=100, raw_content="# Tasks")

        context.set_requirements(req_doc)
        context.set_design(design_doc)
        context.set_tasks(tasks_doc)

        assert context.requirements_doc is req_doc
        assert context.design_doc is design_doc
        assert context.tasks_doc is tasks_doc
