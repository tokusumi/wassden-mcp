"""Traceability validation rules for spec documents.

This module contains rules that validate cross-document references
and coverage requirements.
"""

from wassden.language_types import Language

from .blocks import BlockType, DocumentBlock, RequirementBlock, TaskBlock
from .section_patterns import SectionType
from .validation_rules import (
    BlockLocation,
    TraceabilityValidationRule,
    ValidationContext,
    ValidationError,
    ValidationResult,
)

# Display limits for error messages
MAX_DISPLAY_REQUIREMENTS = 5


class RequirementCoverageRule(TraceabilityValidationRule):
    """Validates that all requirements are referenced in design or tasks."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize requirement coverage rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "TRACE-REQ-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Requirement Coverage"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that all requirements are referenced in design or tasks (100% coverage)"

    def validate(self, document: DocumentBlock, context: ValidationContext) -> ValidationResult:
        """Validate requirement coverage.

        Args:
            document: Document to validate (design or tasks)
            context: Validation context with requirements document

        Returns:
            Validation result with errors for missing references
        """
        errors: list[ValidationError] = []

        # Need requirements document for validation
        if not context.requirements_doc:
            return self._create_result(errors)

        # Extract all requirement IDs from requirements document
        all_req_ids = self._extract_requirement_ids(context.requirements_doc)

        # Extract referenced requirement IDs from current document
        referenced_req_ids = self._extract_requirement_references(document)

        # Find missing references
        missing_refs = sorted(all_req_ids - referenced_req_ids)

        if missing_refs:
            # Display first few missing references
            display_refs = missing_refs[:MAX_DISPLAY_REQUIREMENTS]
            suffix = "..." if len(missing_refs) > MAX_DISPLAY_REQUIREMENTS else ""
            message = f"Requirements not referenced: {', '.join(display_refs)}{suffix}"
            errors.append(
                ValidationError(
                    message=message,
                    location=BlockLocation(line_start=1, line_end=1, section_path=[]),
                )
            )

        return self._create_result(errors)

    def _extract_requirement_ids(self, document: DocumentBlock) -> set[str]:
        """Extract all requirement IDs from requirements document.

        Args:
            document: Requirements document

        Returns:
            Set of requirement IDs
        """
        req_ids = set()
        req_blocks = document.get_blocks_by_type(BlockType.REQUIREMENT)

        for block in req_blocks:
            if isinstance(block, RequirementBlock) and block.req_id:
                # Only include REQ-XX IDs, not NFR, KPI, TR
                if block.req_id.startswith("REQ-"):
                    req_ids.add(block.req_id)

        return req_ids

    def _extract_requirement_references(self, document: DocumentBlock) -> set[str]:
        """Extract all requirement references from document.

        Args:
            document: Document to search for references

        Returns:
            Set of referenced requirement IDs
        """
        referenced_ids = set()

        # Check task blocks for req_refs
        task_blocks = document.get_blocks_by_type(BlockType.TASK)
        for block in task_blocks:
            if isinstance(block, TaskBlock) and block.req_refs:
                referenced_ids.update(block.req_refs)

        # Also check requirement blocks (for design traceability section)
        req_blocks = document.get_blocks_by_type(BlockType.REQUIREMENT)
        for block in req_blocks:
            if isinstance(block, RequirementBlock) and block.req_id and block.req_id.startswith("REQ-"):
                referenced_ids.add(block.req_id)

        return referenced_ids


class DesignReferencesRequirementsRule(TraceabilityValidationRule):
    """Validates that design document references requirements."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize design references requirements rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "TRACE-DESIGN-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Design References Requirements"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that design document contains REQ-ID references"

    def validate(self, document: DocumentBlock, _context: ValidationContext) -> ValidationResult:
        """Validate that design references requirements.

        Args:
            document: Design document to validate
            _context: Validation context

        Returns:
            Validation result with errors if no references found
        """
        errors: list[ValidationError] = []

        # Find all requirement blocks (traceability section contains requirements)
        req_blocks = document.get_blocks_by_type(BlockType.REQUIREMENT)

        # Check if any REQ-IDs are found
        has_req_refs = any(
            isinstance(block, RequirementBlock) and block.req_id and block.req_id.startswith("REQ-")
            for block in req_blocks
        )

        if not has_req_refs:
            errors.append(
                ValidationError(
                    message="No REQ-ID references found in design document",
                    location=BlockLocation(line_start=1, line_end=1, section_path=[]),
                )
            )

        return self._create_result(errors)


class TasksReferenceRequirementsRule(TraceabilityValidationRule):
    """Validates that tasks document references requirements."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize tasks reference requirements rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "TRACE-TASKS-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Tasks Reference Requirements"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that tasks document references requirements when requirements exist"

    def validate(self, document: DocumentBlock, context: ValidationContext) -> ValidationResult:
        """Validate that tasks reference requirements.

        Args:
            document: Tasks document to validate
            context: Validation context with requirements document

        Returns:
            Validation result with errors if requirements exist but not referenced
        """
        errors: list[ValidationError] = []

        # Only validate if requirements document exists
        if not context.requirements_doc:
            return self._create_result(errors)

        # Check if tasks have any requirement references
        task_blocks = document.get_blocks_by_type(BlockType.TASK)
        has_req_refs = any(isinstance(block, TaskBlock) and block.req_refs for block in task_blocks)

        # Extract all requirements from requirements document
        req_blocks = context.requirements_doc.get_blocks_by_type(BlockType.REQUIREMENT)
        has_requirements = any(
            isinstance(block, RequirementBlock) and block.req_id and block.req_id.startswith("REQ-")
            for block in req_blocks
        )

        # If requirements exist but tasks don't reference them, error
        if has_requirements and not has_req_refs:
            errors.append(
                ValidationError(
                    message="Requirements not referenced - tasks reference REQ-IDs but requirements.md is missing",
                    location=BlockLocation(line_start=1, line_end=1, section_path=[]),
                )
            )

        return self._create_result(errors)


class TasksReferenceDesignRule(TraceabilityValidationRule):
    """Validates that tasks document references design components."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize tasks reference design rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "TRACE-TASKS-002"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Tasks Reference Design"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that tasks document references design components when design exists"

    def validate(self, document: DocumentBlock, context: ValidationContext) -> ValidationResult:
        """Validate that tasks reference design components.

        Args:
            document: Tasks document to validate
            context: Validation context with design document

        Returns:
            Validation result with errors if design exists but not referenced
        """
        errors: list[ValidationError] = []

        # Only validate if design document exists
        if not context.design_doc:
            return self._create_result(errors)

        # Check if tasks have any design references
        task_blocks = document.get_blocks_by_type(BlockType.TASK)
        has_design_refs = any(isinstance(block, TaskBlock) and block.design_refs for block in task_blocks)

        # If design exists but tasks don't reference it, error
        if not has_design_refs:
            errors.append(
                ValidationError(
                    message=(
                        "Design components not referenced - "
                        "tasks reference design components but design.md is missing"
                    ),
                    location=BlockLocation(line_start=1, line_end=1, section_path=[]),
                )
            )

        return self._create_result(errors)


class TraceabilitySectionRule(TraceabilityValidationRule):
    """Validates that design document has traceability section."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize traceability section rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "TRACE-DESIGN-002"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Traceability Section"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that design document has traceability section"

    def validate(self, document: DocumentBlock, _context: ValidationContext) -> ValidationResult:
        """Validate that traceability section exists.

        Args:
            document: Design document to validate
            _context: Validation context

        Returns:
            Validation result with errors if section missing
        """
        errors: list[ValidationError] = []

        # Check for traceability section
        section_blocks = document.get_blocks_by_type(BlockType.SECTION)
        has_traceability = any(
            block.section_type == SectionType.TRACEABILITY for block in section_blocks if hasattr(block, "section_type")
        )

        if not has_traceability:
            errors.append(
                ValidationError(
                    message="Missing required traceability section (トレーサビリティ or Traceability)",
                    location=BlockLocation(line_start=1, line_end=1, section_path=[]),
                )
            )

        return self._create_result(errors)
