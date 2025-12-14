"""Structure validation rules for spec documents.

This module contains rules that validate the structure and organization
of spec documents, including required sections.
"""

from wassden.language_types import Language

from .blocks import BlockType, DocumentBlock, SectionBlock
from .section_patterns import SectionType, get_section_pattern
from .validation_rules import (
    BlockLocation,
    StructureValidationRule,
    ValidationContext,
    ValidationError,
    ValidationResult,
)


class RequiredSectionsRule(StructureValidationRule):
    """Base class for required sections validation."""

    def __init__(self, required_section_types: list[SectionType], language: Language = Language.JAPANESE) -> None:
        """Initialize rule with required section types.

        Args:
            required_section_types: List of required section types
            language: Language for validation messages
        """
        super().__init__(language)
        self.required_section_types = required_section_types

    def validate(self, document: DocumentBlock, _context: ValidationContext) -> ValidationResult:
        """Validate that all required sections are present.

        Args:
            document: Document to validate
            context: Validation context

        Returns:
            Validation result with errors for missing sections
        """
        errors: list[ValidationError] = []

        # Get all sections from document
        section_blocks = document.get_blocks_by_type(BlockType.SECTION)
        found_section_types = {section.section_type for section in section_blocks if isinstance(section, SectionBlock)}

        # Check for missing required sections
        for required_type in self.required_section_types:
            if required_type not in found_section_types:
                # Get display name based on language
                display_name = self._get_section_display_name(required_type)
                errors.append(
                    ValidationError(
                        message=f"Missing required section: {display_name}",
                        location=BlockLocation(line_start=1, line_end=1, section_path=[]),
                    )
                )

        return self._create_result(errors)

    def _get_section_display_name(self, section_type: SectionType) -> str:
        """Get display name for section type based on language.

        Args:
            section_type: Section type

        Returns:
            Display name in appropriate language
        """
        # Get pattern for section type
        pattern = get_section_pattern(section_type)
        if pattern:
            # Return localized name based on language
            if self.language == Language.JAPANESE:
                if pattern.ja_patterns:
                    return pattern.ja_patterns[0]
            elif pattern.en_patterns:  # English
                return pattern.en_patterns[0]

        # Fallback to enum value if no pattern found
        return section_type.value


class RequirementsStructureRule(RequiredSectionsRule):
    """Validates requirements document structure."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize requirements structure rule."""
        required_sections = [
            SectionType.OVERVIEW,  # 概要/サマリー
            SectionType.GLOSSARY,
            SectionType.SCOPE,
            SectionType.CONSTRAINTS,
            SectionType.NON_FUNCTIONAL_REQUIREMENTS,  # 非機能要件
            SectionType.KPI,
            SectionType.FUNCTIONAL_REQUIREMENTS,
            SectionType.TESTING_REQUIREMENTS,
        ]
        super().__init__(required_sections, language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "STRUCT-REQ-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Requirements Structure"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that requirements document contains all required sections"


class DesignStructureRule(RequiredSectionsRule):
    """Validates design document structure."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize design structure rule."""
        required_sections = [
            SectionType.ARCHITECTURE,
            SectionType.COMPONENT_DESIGN,
            SectionType.DATA,
            SectionType.API,
            SectionType.NON_FUNCTIONAL,
            SectionType.TEST,
            SectionType.TRACEABILITY,
        ]
        super().__init__(required_sections, language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "STRUCT-DESIGN-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Design Structure"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that design document contains all required sections"


class TasksStructureRule(RequiredSectionsRule):
    """Validates tasks document structure."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize tasks structure rule."""
        required_sections = [
            SectionType.OVERVIEW,
            SectionType.TASK_LIST,
            SectionType.DEPENDENCIES,
            SectionType.MILESTONES,
        ]
        super().__init__(required_sections, language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "STRUCT-TASKS-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Tasks Structure"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that tasks document contains all required sections"
