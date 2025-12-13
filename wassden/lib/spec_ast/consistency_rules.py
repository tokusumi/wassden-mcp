"""Consistency validation rules for spec documents.

This module contains rules that validate consistency across the document,
including circular dependencies and conflicts.
"""

from wassden.language_types import Language

from .blocks import BlockType, DocumentBlock, TaskBlock
from .validation_rules import (
    BlockLocation,
    ConsistencyValidationRule,
    ValidationContext,
    ValidationError,
    ValidationResult,
)


class CircularDependencyRule(ConsistencyValidationRule):
    """Detects circular dependencies in task dependencies."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize circular dependency rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "CONSIST-TASK-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Circular Dependency Detection"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Detects circular dependencies in task relationships"

    def validate(self, document: DocumentBlock, _context: ValidationContext) -> ValidationResult:
        """Validate for circular dependencies.

        Args:
            document: Document to validate
            context: Validation context

        Returns:
            Validation result with errors for circular dependencies
        """
        errors: list[ValidationError] = []

        # Build dependency graph
        task_blocks = document.get_blocks_by_type(BlockType.TASK)
        dependencies: dict[str, list[str]] = {}
        task_locations: dict[str, TaskBlock] = {}

        for block in task_blocks:
            if isinstance(block, TaskBlock) and block.task_id:
                task_locations[block.task_id] = block
                if block.dependencies:
                    dependencies[block.task_id] = block.dependencies

        # Check for direct circular dependencies (A depends on B, B depends on A)
        for task_id, deps in dependencies.items():
            for dep_id in deps:
                if dep_id in dependencies and task_id in dependencies[dep_id]:
                    # Found circular dependency
                    task_block = task_locations[task_id]
                    errors.append(
                        ValidationError(
                            message=f"Circular dependency detected: {task_id} <-> {dep_id}",
                            location=BlockLocation.from_block(task_block),
                        )
                    )

        return self._create_result(errors)
