"""Document style definitions for spec documents.

This module defines document styles that specify the required structure
and validation rules for different types of specification documents.
"""

from dataclasses import dataclass, field

from wassden.language_types import Language

from .consistency_rules import CircularDependencyRule
from .format_rules import (
    DuplicateRequirementIDRule,
    DuplicateTaskIDRule,
    RequirementIDFormatRule,
    TaskIDFormatRule,
)
from .section_patterns import SectionType
from .structure_rules import DesignStructureRule, RequirementsStructureRule, TasksStructureRule
from .test_scenario_rules import DesignComponentCoverageRule, TestScenarioCoverageRule
from .traceability_rules import (
    DesignReferencesRequirementsRule,
    RequirementCoverageRule,
    TasksReferenceDesignRule,
    TasksReferenceRequirementsRule,
    TraceabilitySectionRule,
)
from .validation_rules import ValidationRule


@dataclass
class DocumentStyle:
    """Defines the structure and validation rules for a document type.

    A document style specifies:
    - Required sections that must be present
    - Validation rules that should be applied
    - Optional sections that may be present
    """

    name: str
    description: str
    required_sections: list[SectionType]
    validation_rules: list[type[ValidationRule]]
    optional_sections: list[SectionType] = field(default_factory=list)

    def create_validation_rules(self, language: Language = Language.JAPANESE) -> list[ValidationRule]:
        """Create instances of validation rules for this style.

        Args:
            language: Language for validation messages

        Returns:
            List of instantiated validation rules
        """
        return [rule_class(language) for rule_class in self.validation_rules]


# Predefined document styles

REQUIREMENTS_STYLE = DocumentStyle(
    name="Requirements Document",
    description="Standard requirements specification document with EARS patterns",
    required_sections=[
        SectionType.OVERVIEW,  # 概要/サマリー
        SectionType.GLOSSARY,
        SectionType.SCOPE,
        SectionType.CONSTRAINTS,
        SectionType.NON_FUNCTIONAL_REQUIREMENTS,  # 非機能要件/非機能要求仕様
        SectionType.KPI,
        SectionType.FUNCTIONAL_REQUIREMENTS,
        SectionType.TESTING_REQUIREMENTS,
    ],
    validation_rules=[
        RequirementsStructureRule,
        RequirementIDFormatRule,
        DuplicateRequirementIDRule,
        # EARS validation can be added here in future
    ],
    optional_sections=[
        SectionType.REFERENCES,
        SectionType.APPENDIX,
    ],
)

DESIGN_STYLE = DocumentStyle(
    name="Design Document",
    description="Standard design specification document with traceability",
    required_sections=[
        SectionType.ARCHITECTURE,
        SectionType.COMPONENT_DESIGN,
        SectionType.DATA,
        SectionType.API,
        SectionType.NON_FUNCTIONAL,
        SectionType.TEST,
        SectionType.TRACEABILITY,
    ],
    validation_rules=[
        DesignStructureRule,
        TraceabilitySectionRule,
        DesignReferencesRequirementsRule,
        RequirementCoverageRule,
    ],
    optional_sections=[
        SectionType.REFERENCES,
        SectionType.APPENDIX,
    ],
)

TASKS_STYLE = DocumentStyle(
    name="Tasks Document",
    description="Standard task breakdown document with dependencies",
    required_sections=[
        SectionType.OVERVIEW,
        SectionType.TASK_LIST,
        SectionType.DEPENDENCIES,
        SectionType.MILESTONES,
    ],
    validation_rules=[
        TasksStructureRule,
        TaskIDFormatRule,
        DuplicateTaskIDRule,
        CircularDependencyRule,
        TasksReferenceRequirementsRule,
        TasksReferenceDesignRule,
        RequirementCoverageRule,
        TestScenarioCoverageRule,
        DesignComponentCoverageRule,
    ],
    optional_sections=[
        SectionType.REFERENCES,
        SectionType.APPENDIX,
    ],
)

# Registry of all predefined styles
DOCUMENT_STYLES: dict[str, DocumentStyle] = {
    "requirements": REQUIREMENTS_STYLE,
    "design": DESIGN_STYLE,
    "tasks": TASKS_STYLE,
}


def get_document_style(style_name: str) -> DocumentStyle | None:
    """Get a document style by name.

    Args:
        style_name: Name of the style to retrieve

    Returns:
        DocumentStyle if found, None otherwise
    """
    return DOCUMENT_STYLES.get(style_name.lower())
