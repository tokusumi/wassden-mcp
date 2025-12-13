"""Validation engine for spec documents.

This module provides a high-level interface for running validation rules
on spec documents using document styles.
"""

from typing import Any

from wassden.language_types import Language

from .blocks import DocumentBlock
from .document_styles import DESIGN_STYLE, REQUIREMENTS_STYLE, TASKS_STYLE, DocumentStyle, get_document_style
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
        """Validate requirements document using predefined requirements style.

        Args:
            document: Requirements document to validate

        Returns:
            List of validation results
        """
        return self.validate_document(document, REQUIREMENTS_STYLE)

    def validate_design(self, document: DocumentBlock) -> list[ValidationResult]:
        """Validate design document using predefined design style.

        Args:
            document: Design document to validate

        Returns:
            List of validation results
        """
        return self.validate_document(document, DESIGN_STYLE)

    def validate_tasks(self, document: DocumentBlock) -> list[ValidationResult]:
        """Validate tasks document using predefined tasks style.

        Args:
            document: Tasks document to validate

        Returns:
            List of validation results
        """
        return self.validate_document(document, TASKS_STYLE)

    def validate_with_style(self, document: DocumentBlock, style_name: str) -> list[ValidationResult]:
        """Validate document using a named document style.

        Args:
            document: Document to validate
            style_name: Name of the style to use (requirements, design, tasks)

        Returns:
            List of validation results

        Raises:
            ValueError: If style_name is not found
        """
        style = get_document_style(style_name)
        if style is None:
            msg = f"Unknown document style: {style_name}"
            raise ValueError(msg)
        return self.validate_document(document, style)

    def validate_document(self, document: DocumentBlock, style: DocumentStyle) -> list[ValidationResult]:
        """Validate document using a DocumentStyle.

        Args:
            document: Document to validate
            style: Document style defining structure and rules

        Returns:
            List of validation results
        """
        # Create validation rules from style
        rules = style.create_validation_rules(self.language)
        return self._run_rules(document, rules)

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
