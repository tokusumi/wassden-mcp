"""Test scenario coverage validation rules.

This module contains rules that validate test scenario coverage in tasks documents.
"""

import re

from wassden.language_types import Language

from .blocks import BlockType, DocumentBlock, ListItemBlock, TaskBlock
from .id_extractor import IDExtractor
from .validation_rules import (
    BlockLocation,
    TraceabilityValidationRule,
    ValidationContext,
    ValidationError,
    ValidationResult,
)


class TestScenarioCoverageRule(TraceabilityValidationRule):
    """Validates that all test scenarios from design are referenced in tasks."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize test scenario coverage rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "TRACE-TASKS-003"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Test Scenario Coverage"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that all test scenarios from design document are referenced in tasks"

    def validate(self, document: DocumentBlock, context: ValidationContext) -> ValidationResult:
        """Validate test scenario coverage.

        Args:
            document: Tasks document to validate
            context: Validation context with design document

        Returns:
            Validation result with errors for unreferenced test scenarios
        """
        errors: list[ValidationError] = []

        # Only validate if design document exists
        if not context.design_doc:
            return self._create_result(errors)

        # Extract all test scenarios from design document
        design_test_scenarios = self._extract_test_scenarios(context.design_doc)

        # Extract referenced design components from tasks
        referenced_components = self._extract_referenced_components(document)

        # Find unreferenced test scenarios
        unreferenced_scenarios = design_test_scenarios - referenced_components

        if unreferenced_scenarios:
            errors.extend(
                ValidationError(
                    message=f"Test scenario not referenced in tasks: {scenario}",
                    location=BlockLocation(line_start=1, line_end=1, section_path=[]),
                )
                for scenario in sorted(unreferenced_scenarios)
            )

        return self._create_result(errors)

    def _extract_test_scenarios(self, design_doc: DocumentBlock) -> set[str]:
        """Extract test scenarios from design document.

        Args:
            design_doc: Design document

        Returns:
            Set of test scenario identifiers (e.g., "test-input-processing")
        """
        test_scenarios = set()

        # Extract from ListItemBlocks in test strategy section
        list_item_blocks = design_doc.get_blocks_by_type(BlockType.LIST_ITEM)
        for block in list_item_blocks:
            if isinstance(block, ListItemBlock) and block.content:
                # Try extracting design component references using pattern **component-name**
                dc_refs = list(IDExtractor.extract_all_dc_refs(block.content))
                test_scenarios.update(dc_refs)

                # Also extract test scenario names from format "**test-xxx**: description" or "test-xxx: description"
                # This handles cases where markdown bold markers are already stripped
                # Pattern: test-xxx (kebab-case identifier starting with "test-")
                test_pattern = r"\b(test-[a-z0-9]+(?:-[a-z0-9]+)*)\b"
                matches = re.findall(test_pattern, block.content)
                test_scenarios.update(matches)

        return test_scenarios

    def _extract_referenced_components(self, tasks_doc: DocumentBlock) -> set[str]:
        """Extract referenced design components from tasks document.

        Args:
            tasks_doc: Tasks document

        Returns:
            Set of referenced component identifiers
        """
        referenced = set()

        # Extract from TaskBlocks
        task_blocks = tasks_doc.get_blocks_by_type(BlockType.TASK)
        for block in task_blocks:
            if isinstance(block, TaskBlock):
                # Add formal DC references (DC-01, DC-02, etc.)
                if block.design_refs:
                    referenced.update(block.design_refs)

                # Also scan raw content for test scenario references (test-xxx format)
                # This handles cases where test scenarios are referenced in task content
                if block.raw_content:
                    test_pattern = r"(test-[a-z0-9]+(?:-[a-z0-9]+)*)"
                    matches = re.findall(test_pattern, block.raw_content)
                    referenced.update(matches)

        return referenced
