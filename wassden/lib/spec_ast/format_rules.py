"""Format validation rules for spec documents.

This module contains rules that validate ID formats, naming conventions,
and other formatting requirements.
"""

import re

from wassden.language_types import Language

from .blocks import BlockType, DocumentBlock, RequirementBlock, TaskBlock
from .validation_rules import (
    BlockLocation,
    FormatValidationRule,
    ValidationContext,
    ValidationError,
    ValidationResult,
)


class RequirementIDFormatRule(FormatValidationRule):
    """Validates requirement ID formats."""

    REQ_ID_PATTERN = re.compile(r"^REQ-\d{2}$")

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize requirement ID format rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "FORMAT-REQ-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Requirement ID Format"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that requirement IDs follow REQ-XX format (01-99, not 00)"

    def validate(self, document: DocumentBlock, _context: ValidationContext) -> ValidationResult:
        """Validate requirement ID formats.

        Args:
            document: Document to validate
            context: Validation context

        Returns:
            Validation result with errors for invalid IDs
        """
        errors: list[ValidationError] = []

        # Get all requirement blocks
        req_blocks = document.get_blocks_by_type(BlockType.REQUIREMENT)

        for block in req_blocks:
            if not isinstance(block, RequirementBlock):
                continue

            req_id = block.req_id
            if req_id and not self._is_valid_req_id(req_id):
                errors.append(
                    ValidationError(
                        message=f"Invalid REQ-ID format: {req_id}",
                        location=BlockLocation.from_block(block),
                    )
                )

        return self._create_result(errors)

    def _is_valid_req_id(self, req_id: str) -> bool:
        """Check if requirement ID is valid.

        Args:
            req_id: Requirement ID to validate

        Returns:
            True if valid, False otherwise
        """
        if not self.REQ_ID_PATTERN.match(req_id):
            return False

        # Check that number part is not 00
        num_part = req_id.split("-")[1]
        return num_part != "00"


class TaskIDFormatRule(FormatValidationRule):
    """Validates task ID formats."""

    TASK_ID_PATTERN = re.compile(r"^TASK-\d{2}(-\d{2}){1,2}$")

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize task ID format rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "FORMAT-TASK-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Task ID Format"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that task IDs follow TASK-XX-XX or TASK-XX-XX-XX format (01-99, not 00)"

    def validate(self, document: DocumentBlock, _context: ValidationContext) -> ValidationResult:
        """Validate task ID formats.

        Args:
            document: Document to validate
            context: Validation context

        Returns:
            Validation result with errors for invalid IDs
        """
        errors: list[ValidationError] = []

        # Get all task blocks
        task_blocks = document.get_blocks_by_type(BlockType.TASK)

        for block in task_blocks:
            if not isinstance(block, TaskBlock):
                continue

            task_id = block.task_id
            if task_id and not self._is_valid_task_id(task_id):
                errors.append(
                    ValidationError(
                        message=f"Invalid TASK-ID format: {task_id}",
                        location=BlockLocation.from_block(block),
                    )
                )

        return self._create_result(errors)

    def _is_valid_task_id(self, task_id: str) -> bool:
        """Check if task ID is valid.

        Args:
            task_id: Task ID to validate

        Returns:
            True if valid, False otherwise
        """
        if not self.TASK_ID_PATTERN.match(task_id):
            return False

        # Check that no number parts are 00
        parts = task_id.split("-")[1:]  # Remove "TASK" part
        return all(part != "00" for part in parts)


class DuplicateRequirementIDRule(FormatValidationRule):
    """Detects duplicate requirement IDs."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize duplicate requirement ID rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "FORMAT-REQ-002"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Duplicate Requirement ID"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Detects duplicate requirement IDs in the document"

    def validate(self, document: DocumentBlock, _context: ValidationContext) -> ValidationResult:
        """Validate for duplicate requirement IDs.

        Args:
            document: Document to validate
            context: Validation context

        Returns:
            Validation result with errors for duplicates
        """
        errors: list[ValidationError] = []

        # Get all requirement blocks with IDs
        req_blocks = document.get_blocks_by_type(BlockType.REQUIREMENT)
        req_id_locations: dict[str, list[RequirementBlock]] = {}

        for block in req_blocks:
            if not isinstance(block, RequirementBlock):
                continue

            req_id = block.req_id
            if req_id:
                if req_id not in req_id_locations:
                    req_id_locations[req_id] = []
                req_id_locations[req_id].append(block)

        # Find duplicates
        for req_id, blocks in req_id_locations.items():
            if len(blocks) > 1:
                # Report all occurrences
                for block in blocks:
                    errors.append(
                        ValidationError(
                            message=f"Duplicate REQ-ID found: {req_id}",
                            location=BlockLocation.from_block(block),
                        )
                    )

        return self._create_result(errors)


class DuplicateTaskIDRule(FormatValidationRule):
    """Detects duplicate task IDs."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize duplicate task ID rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "FORMAT-TASK-002"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Duplicate Task ID"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Detects duplicate task IDs in the document"

    def validate(self, document: DocumentBlock, _context: ValidationContext) -> ValidationResult:
        """Validate for duplicate task IDs.

        Args:
            document: Document to validate
            context: Validation context

        Returns:
            Validation result with errors for duplicates
        """
        errors: list[ValidationError] = []

        # Get all task blocks with IDs
        task_blocks = document.get_blocks_by_type(BlockType.TASK)
        task_id_locations: dict[str, list[TaskBlock]] = {}

        for block in task_blocks:
            if not isinstance(block, TaskBlock):
                continue

            task_id = block.task_id
            if task_id:
                if task_id not in task_id_locations:
                    task_id_locations[task_id] = []
                task_id_locations[task_id].append(block)

        # Find duplicates
        for task_id, blocks in task_id_locations.items():
            if len(blocks) > 1:
                # Report all occurrences
                for block in blocks:
                    errors.append(
                        ValidationError(
                            message=f"Duplicate TASK-ID found: {task_id}",
                            location=BlockLocation.from_block(block),
                        )
                    )

        return self._create_result(errors)
