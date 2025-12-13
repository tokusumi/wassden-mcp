"""Validation engine for spec documents.

This module provides a high-level interface for running validation rules
on spec documents.
"""

from typing import Any

from wassden.language_types import Language

from .blocks import DocumentBlock
from .consistency_rules import CircularDependencyRule
from .format_rules import (
    DuplicateRequirementIDRule,
    DuplicateTaskIDRule,
    RequirementIDFormatRule,
    TaskIDFormatRule,
)
from .structure_rules import DesignStructureRule, RequirementsStructureRule, TasksStructureRule
from .traceability_rules import (
    DesignReferencesRequirementsRule,
    RequirementCoverageRule,
    TasksReferenceDesignRule,
    TasksReferenceRequirementsRule,
    TraceabilitySectionRule,
)
from .validation_rules import ValidationContext, ValidationResult, ValidationRule


class ValidationEngine:
    """Engine for running validation rules on spec documents."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize validation engine.

        Args:
            language: Language for validation messages
        """
        self.language = language
        self.context = ValidationContext(language)

        # Initialize rule sets
        self._init_requirements_rules()
        self._init_design_rules()
        self._init_tasks_rules()

    def _init_requirements_rules(self) -> None:
        """Initialize requirements document validation rules."""
        self.requirements_rules: list[ValidationRule] = [
            RequirementsStructureRule(self.language),
            RequirementIDFormatRule(self.language),
            DuplicateRequirementIDRule(self.language),
        ]

    def _init_design_rules(self) -> None:
        """Initialize design document validation rules."""
        self.design_rules: list[ValidationRule] = [
            DesignStructureRule(self.language),
            TraceabilitySectionRule(self.language),
            DesignReferencesRequirementsRule(self.language),
            RequirementCoverageRule(self.language),
        ]

    def _init_tasks_rules(self) -> None:
        """Initialize tasks document validation rules."""
        self.tasks_rules: list[ValidationRule] = [
            TasksStructureRule(self.language),
            TaskIDFormatRule(self.language),
            DuplicateTaskIDRule(self.language),
            CircularDependencyRule(self.language),
            TasksReferenceRequirementsRule(self.language),
            TasksReferenceDesignRule(self.language),
            RequirementCoverageRule(self.language),
        ]

    def set_requirements_document(self, document: DocumentBlock) -> None:
        """Set requirements document for cross-reference validation.

        Args:
            document: Requirements document
        """
        self.context.set_requirements(document)

    def set_design_document(self, document: DocumentBlock) -> None:
        """Set design document for cross-reference validation.

        Args:
            document: Design document
        """
        self.context.set_design(document)

    def set_tasks_document(self, document: DocumentBlock) -> None:
        """Set tasks document for cross-reference validation.

        Args:
            document: Tasks document
        """
        self.context.set_tasks(document)

    def validate_requirements(self, document: DocumentBlock) -> list[ValidationResult]:
        """Validate requirements document.

        Args:
            document: Requirements document to validate

        Returns:
            List of validation results
        """
        return self._run_rules(document, self.requirements_rules)

    def validate_design(self, document: DocumentBlock) -> list[ValidationResult]:
        """Validate design document.

        Args:
            document: Design document to validate

        Returns:
            List of validation results
        """
        return self._run_rules(document, self.design_rules)

    def validate_tasks(self, document: DocumentBlock) -> list[ValidationResult]:
        """Validate tasks document.

        Args:
            document: Tasks document to validate

        Returns:
            List of validation results
        """
        return self._run_rules(document, self.tasks_rules)

    def _run_rules(self, document: DocumentBlock, rules: list[ValidationRule]) -> list[ValidationResult]:
        """Run validation rules on a document.

        Args:
            document: Document to validate
            rules: List of rules to apply

        Returns:
            List of validation results
        """
        results = []
        for rule in rules:
            result = rule.validate(document, self.context)
            results.append(result)
        return results

    def get_validation_summary(self, results: list[ValidationResult]) -> dict[str, Any]:
        """Get summary of validation results.

        Args:
            results: List of validation results

        Returns:
            Dictionary with summary information
        """
        total_rules = len(results)
        passed_rules = sum(1 for r in results if r.is_valid)
        failed_rules = total_rules - passed_rules
        total_errors = sum(len(r.errors) for r in results)

        all_errors = []
        for result in results:
            for error in result.errors:
                all_errors.append(error.message)

        return {
            "isValid": failed_rules == 0,
            "totalRules": total_rules,
            "passedRules": passed_rules,
            "failedRules": failed_rules,
            "totalErrors": total_errors,
            "errors": all_errors,
            "results": [result.to_dict() for result in results],
        }
