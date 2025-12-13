"""Validation rule objects for spec documents.

This module defines the validation rule interface and base classes
for validating spec documents using the AST-based parser.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum

from wassden.language_types import Language

from .blocks import DocumentBlock, SpecBlock


class Severity(Enum):
    """Severity level for validation errors."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class BlockLocation:
    """Location of a block in the document."""

    line_start: int
    line_end: int
    section_path: list[str] = field(default_factory=list)

    @classmethod
    def from_block(cls, block: SpecBlock) -> "BlockLocation":
        """Create location from a spec block."""
        return cls(line_start=block.line_start, line_end=block.line_end, section_path=block.get_context_path())


@dataclass
class ValidationError:
    """Individual validation error."""

    message: str
    location: BlockLocation | None = None
    severity: Severity = Severity.ERROR

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        result = {"message": self.message, "severity": self.severity.value}
        if self.location:
            result["location"] = {
                "line_start": self.location.line_start,
                "line_end": self.location.line_end,
                "section_path": self.location.section_path,
            }
        return result


@dataclass
class ValidationResult:
    """Result of a validation rule execution."""

    rule_id: str
    rule_name: str
    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "is_valid": self.is_valid,
            "errors": [error.to_dict() for error in self.errors],
        }


class ValidationContext:
    """Context for validation including cross-document references."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize validation context.

        Args:
            language: Language for validation messages
        """
        self.language = language
        self.requirements_doc: DocumentBlock | None = None
        self.design_doc: DocumentBlock | None = None
        self.tasks_doc: DocumentBlock | None = None

    def set_requirements(self, doc: DocumentBlock) -> None:
        """Set requirements document for cross-reference validation."""
        self.requirements_doc = doc

    def set_design(self, doc: DocumentBlock) -> None:
        """Set design document for cross-reference validation."""
        self.design_doc = doc

    def set_tasks(self, doc: DocumentBlock) -> None:
        """Set tasks document for cross-reference validation."""
        self.tasks_doc = doc


class ValidationRule(ABC):
    """Base class for validation rules."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize validation rule.

        Args:
            language: Language for validation messages
        """
        self.language = language

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for this rule."""

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable name for this rule."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this rule validates."""

    @abstractmethod
    def validate(self, document: DocumentBlock, context: ValidationContext) -> ValidationResult:
        """Validate the document block against this rule.

        Args:
            document: Document to validate
            context: Validation context with cross-document references

        Returns:
            Validation result with any errors found
        """

    def _create_result(self, errors: list[ValidationError]) -> ValidationResult:
        """Helper to create a validation result.

        Args:
            errors: List of validation errors

        Returns:
            ValidationResult with is_valid set based on errors
        """
        return ValidationResult(
            rule_id=self.rule_id, rule_name=self.rule_name, is_valid=len(errors) == 0, errors=errors
        )


class StructureValidationRule(ValidationRule):
    """Base class for structure validation rules.

    Structure rules check for presence and organization of sections.
    """



class FormatValidationRule(ValidationRule):
    """Base class for format validation rules.

    Format rules check ID formats, naming conventions, etc.
    """



class ContentValidationRule(ValidationRule):
    """Base class for content validation rules.

    Content rules check the actual content of requirements, tasks, etc.
    Examples: EARS pattern validation, text quality checks.
    """



class TraceabilityValidationRule(ValidationRule):
    """Base class for traceability validation rules.

    Traceability rules check cross-document references and coverage.
    Examples: requirement coverage, design references.
    """



class ConsistencyValidationRule(ValidationRule):
    """Base class for consistency validation rules.

    Consistency rules check for duplicates, conflicts, circular dependencies.
    """

