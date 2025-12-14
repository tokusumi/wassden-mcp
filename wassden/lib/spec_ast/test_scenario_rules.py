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
        referenced: set[str] = set()

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


class DesignComponentCoverageRule(TraceabilityValidationRule):
    """Validates that all design components are referenced in tasks."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize design component coverage rule."""
        super().__init__(language)

    @property
    def rule_id(self) -> str:
        """Unique identifier for this rule."""
        return "TRACE-DESIGN-001"

    @property
    def rule_name(self) -> str:
        """Human-readable name for this rule."""
        return "Design Component Coverage"

    @property
    def description(self) -> str:
        """Description of what this rule validates."""
        return "Validates that all design components are referenced in tasks"

    def validate(self, document: DocumentBlock, context: ValidationContext) -> ValidationResult:
        """Validate design component coverage.

        Args:
            document: Tasks document to validate
            context: Validation context with design document

        Returns:
            Validation result with errors for unreferenced components
        """
        errors: list[ValidationError] = []

        # Only validate if design document exists
        if not context.design_doc:
            return self._create_result(errors)

        # Extract all design components from design document
        design_components = self._extract_design_components(context.design_doc)

        # Extract referenced components from tasks (pass design_components for substring matching)
        referenced_components = self._extract_referenced_components(document, design_components)

        # Find unreferenced components
        unreferenced = design_components - referenced_components

        if unreferenced:
            # Format as single message with all missing components (legacy compatibility)
            sorted_unreferenced = sorted(unreferenced)
            max_display = 10
            display_refs = sorted_unreferenced[:max_display]
            suffix = "..." if len(sorted_unreferenced) > max_display else ""
            components_str = ", ".join(display_refs) + suffix
            errors.append(
                ValidationError(
                    message=f"Design components not referenced in tasks: {components_str}",
                    location=BlockLocation(line_start=1, line_end=1, section_path=[]),
                )
            )

        return self._create_result(errors)

    def _extract_design_components(self, design_doc: DocumentBlock) -> set[str]:
        """Extract design components from design document.

        Args:
            design_doc: Design document

        Returns:
            Set of component identifiers
        """
        components: set[str] = set()

        # Extract from ListItemBlocks
        list_item_blocks = design_doc.get_blocks_by_type(BlockType.LIST_ITEM)
        for block in list_item_blocks:
            if isinstance(block, ListItemBlock) and block.content:
                # Pattern 1: **component-name** (with bold markers)
                bold_pattern = r"\*\*([a-z][a-z0-9]*(?:[-_][a-z0-9]+)+)\*\*"
                bold_matches = re.findall(bold_pattern, block.content)
                components.update(m for m in bold_matches if not m.startswith("test-"))

                # Pattern 2: component-name: (without bold, at start of line)
                # This handles cases where markdown parser already stripped bold markers
                plain_pattern = r"^([a-z][a-z0-9]*(?:[-_][a-z0-9]+)+):"
                plain_matches = re.findall(plain_pattern, block.content)
                components.update(m for m in plain_matches if not m.startswith("test-"))

        return components

    def _extract_referenced_components(self, tasks_doc: DocumentBlock, design_components: set[str]) -> set[str]:
        """Extract referenced design components from tasks document.

        Args:
            tasks_doc: Tasks document
            design_components: Set of design components to look for

        Returns:
            Set of referenced component identifiers
        """
        referenced: set[str] = set()

        # Extract from TaskBlocks
        task_blocks = tasks_doc.get_blocks_by_type(BlockType.TASK)
        for block in task_blocks:
            if isinstance(block, TaskBlock):
                # Add from design_refs field
                if block.design_refs:
                    # Filter out test scenarios
                    referenced.update(ref for ref in block.design_refs if not ref.startswith("test-"))

                # Also check if any design component name appears in task content (legacy compatibility)
                if block.raw_content or block.task_text:
                    content = block.raw_content or block.task_text
                    for component in design_components:
                        if component in content:
                            referenced.add(component)

        return referenced
