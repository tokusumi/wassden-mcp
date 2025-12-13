"""Section pattern configuration for multi-language document parsing.

This module defines the mapping between section titles and normalized identifiers
for both Japanese and English specification documents.
Each section pattern is defined as an individual class inheriting from BaseSectionPattern.
"""

from abc import ABC, abstractmethod
from enum import Enum


class SectionType(Enum):
    """Normalized section types across document types."""

    # Requirements document sections
    SUMMARY = "summary"
    GLOSSARY = "glossary"
    SCOPE = "scope"
    CONSTRAINTS = "constraints"
    NON_FUNCTIONAL_REQUIREMENTS = "non_functional_requirements"
    KPI = "kpi"
    FUNCTIONAL_REQUIREMENTS = "functional_requirements"
    TESTING_REQUIREMENTS = "testing_requirements"

    # Design document sections
    ARCHITECTURE = "architecture"
    COMPONENT_DESIGN = "component_design"
    DATA = "data"
    API = "api"
    NON_FUNCTIONAL = "non_functional"
    TEST = "test"
    TRACEABILITY = "traceability"

    # Tasks document sections
    OVERVIEW = "overview"
    TASK_LIST = "task_list"
    DEPENDENCIES = "dependencies"
    MILESTONES = "milestones"

    # Common sections
    REFERENCES = "references"
    APPENDIX = "appendix"
    UNKNOWN = "unknown"


class BaseSectionPattern(ABC):
    """Base class for section patterns.

    Each section pattern defines:
    - section_type: Normalized section type identifier
    - ja_patterns: List of Japanese section title patterns
    - en_patterns: List of English section title patterns
    - contains_requirements: Whether this section contains requirement items
    - contains_tasks: Whether this section contains task items
    """

    @property
    @abstractmethod
    def section_type(self) -> SectionType:
        """Get the normalized section type."""
        ...

    @property
    @abstractmethod
    def ja_patterns(self) -> list[str]:
        """Get Japanese section title patterns."""
        ...

    @property
    @abstractmethod
    def en_patterns(self) -> list[str]:
        """Get English section title patterns."""
        ...

    @property
    def contains_requirements(self) -> bool:
        """Whether this section typically contains requirement items."""
        return False

    @property
    def contains_tasks(self) -> bool:
        """Whether this section typically contains task items."""
        return False


# ============================================================================
# Requirements Document Section Patterns
# ============================================================================


class SummaryPattern(BaseSectionPattern):
    """Summary/サマリー section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.SUMMARY

    @property
    def ja_patterns(self) -> list[str]:
        return ["サマリー"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Summary"]


class GlossaryPattern(BaseSectionPattern):
    """Glossary/用語集 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.GLOSSARY

    @property
    def ja_patterns(self) -> list[str]:
        return ["用語集"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Glossary"]


class ScopePattern(BaseSectionPattern):
    """Scope/スコープ section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.SCOPE

    @property
    def ja_patterns(self) -> list[str]:
        return ["スコープ", "適用範囲"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Scope"]


class ConstraintsPattern(BaseSectionPattern):
    """Constraints/制約事項 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.CONSTRAINTS

    @property
    def ja_patterns(self) -> list[str]:
        return ["制約事項", "制約"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Constraints"]


class NonFunctionalRequirementsPattern(BaseSectionPattern):
    """Non-Functional Requirements/非機能要件 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.NON_FUNCTIONAL_REQUIREMENTS

    @property
    def ja_patterns(self) -> list[str]:
        return ["非機能要件"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Non-Functional Requirements"]

    @property
    def contains_requirements(self) -> bool:
        return True


class KPIPattern(BaseSectionPattern):
    """KPI section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.KPI

    @property
    def ja_patterns(self) -> list[str]:
        return ["KPI"]

    @property
    def en_patterns(self) -> list[str]:
        return ["KPI", "Key Performance Indicators"]

    @property
    def contains_requirements(self) -> bool:
        return True


class FunctionalRequirementsPattern(BaseSectionPattern):
    """Functional Requirements/機能要件 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.FUNCTIONAL_REQUIREMENTS

    @property
    def ja_patterns(self) -> list[str]:
        return ["機能要件", "機能要件（EARS）", "機能要求仕様"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Functional Requirements"]

    @property
    def contains_requirements(self) -> bool:
        return True


class TestingRequirementsPattern(BaseSectionPattern):
    """Testing Requirements/テスト要件 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.TESTING_REQUIREMENTS

    @property
    def ja_patterns(self) -> list[str]:
        return ["テスト要件", "テスト要求仕様", "受入要件"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Testing Requirements", "Test Requirements"]

    @property
    def contains_requirements(self) -> bool:
        return True


# ============================================================================
# Design Document Section Patterns
# ============================================================================


class ArchitecturePattern(BaseSectionPattern):
    """Architecture/アーキテクチャ section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.ARCHITECTURE

    @property
    def ja_patterns(self) -> list[str]:
        return ["アーキテクチャ", "システム構成"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Architecture", "System Architecture"]


class ComponentDesignPattern(BaseSectionPattern):
    """Component Design/コンポーネント設計 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.COMPONENT_DESIGN

    @property
    def ja_patterns(self) -> list[str]:
        return ["コンポーネント設計", "詳細設計"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Component Design", "Detailed Design"]


class DataPattern(BaseSectionPattern):
    """Data/データ section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.DATA

    @property
    def ja_patterns(self) -> list[str]:
        return ["データ", "データモデル"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Data", "Data Model"]


class APIPattern(BaseSectionPattern):
    """API section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.API

    @property
    def ja_patterns(self) -> list[str]:
        return ["API"]

    @property
    def en_patterns(self) -> list[str]:
        return ["API", "APIs"]


class NonFunctionalPattern(BaseSectionPattern):
    """Non-Functional/非機能 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.NON_FUNCTIONAL

    @property
    def ja_patterns(self) -> list[str]:
        return ["非機能", "非機能要求仕様"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Non-Functional"]


class TestPattern(BaseSectionPattern):
    """Test/テスト section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.TEST

    @property
    def ja_patterns(self) -> list[str]:
        return ["テスト"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Test", "Testing"]


class TraceabilityPattern(BaseSectionPattern):
    """Traceability/トレーサビリティ section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.TRACEABILITY

    @property
    def ja_patterns(self) -> list[str]:
        return ["トレーサビリティ", "要件追跡"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Traceability"]


# ============================================================================
# Tasks Document Section Patterns
# ============================================================================


class OverviewPattern(BaseSectionPattern):
    """Overview/概要 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.OVERVIEW

    @property
    def ja_patterns(self) -> list[str]:
        return ["概要"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Overview"]


class TaskListPattern(BaseSectionPattern):
    """Task List/タスク一覧 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.TASK_LIST

    @property
    def ja_patterns(self) -> list[str]:
        return ["タスク一覧", "タスクリスト"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Task List", "Tasks"]

    @property
    def contains_tasks(self) -> bool:
        return True


class DependenciesPattern(BaseSectionPattern):
    """Dependencies/依存関係 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.DEPENDENCIES

    @property
    def ja_patterns(self) -> list[str]:
        return ["依存関係"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Dependencies"]


class MilestonesPattern(BaseSectionPattern):
    """Milestones/マイルストーン section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.MILESTONES

    @property
    def ja_patterns(self) -> list[str]:
        return ["マイルストーン"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Milestones"]


# ============================================================================
# Common Section Patterns
# ============================================================================


class ReferencesPattern(BaseSectionPattern):
    """References/参考資料 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.REFERENCES

    @property
    def ja_patterns(self) -> list[str]:
        return ["参考資料", "参照"]

    @property
    def en_patterns(self) -> list[str]:
        return ["References"]


class AppendixPattern(BaseSectionPattern):
    """Appendix/付録 section pattern."""

    @property
    def section_type(self) -> SectionType:
        return SectionType.APPENDIX

    @property
    def ja_patterns(self) -> list[str]:
        return ["付録"]

    @property
    def en_patterns(self) -> list[str]:
        return ["Appendix"]


# ============================================================================
# Pattern Instances - each as individual object
# ============================================================================

# Requirements document sections
SUMMARY_PATTERN = SummaryPattern()
GLOSSARY_PATTERN = GlossaryPattern()
SCOPE_PATTERN = ScopePattern()
CONSTRAINTS_PATTERN = ConstraintsPattern()
NON_FUNCTIONAL_REQUIREMENTS_PATTERN = NonFunctionalRequirementsPattern()
KPI_PATTERN = KPIPattern()
FUNCTIONAL_REQUIREMENTS_PATTERN = FunctionalRequirementsPattern()
TESTING_REQUIREMENTS_PATTERN = TestingRequirementsPattern()

# Design document sections
ARCHITECTURE_PATTERN = ArchitecturePattern()
COMPONENT_DESIGN_PATTERN = ComponentDesignPattern()
DATA_PATTERN = DataPattern()
API_PATTERN = APIPattern()
NON_FUNCTIONAL_PATTERN = NonFunctionalPattern()
TEST_PATTERN = TestPattern()
TRACEABILITY_PATTERN = TraceabilityPattern()

# Tasks document sections
OVERVIEW_PATTERN = OverviewPattern()
TASK_LIST_PATTERN = TaskListPattern()
DEPENDENCIES_PATTERN = DependenciesPattern()
MILESTONES_PATTERN = MilestonesPattern()

# Common sections
REFERENCES_PATTERN = ReferencesPattern()
APPENDIX_PATTERN = AppendixPattern()

# All section patterns for iteration
# Note: Order matters! More specific patterns should come before general ones
# to avoid false matches (e.g., "非機能要求仕様" before "機能要求仕様")
SECTION_PATTERNS: list[BaseSectionPattern] = [
    SUMMARY_PATTERN,
    GLOSSARY_PATTERN,
    SCOPE_PATTERN,
    CONSTRAINTS_PATTERN,
    NON_FUNCTIONAL_REQUIREMENTS_PATTERN,
    NON_FUNCTIONAL_PATTERN,  # Must come before FUNCTIONAL_REQUIREMENTS_PATTERN
    KPI_PATTERN,
    FUNCTIONAL_REQUIREMENTS_PATTERN,
    TESTING_REQUIREMENTS_PATTERN,
    TEST_PATTERN,  # Moved after TESTING_REQUIREMENTS_PATTERN for specificity
    ARCHITECTURE_PATTERN,
    COMPONENT_DESIGN_PATTERN,
    DATA_PATTERN,
    API_PATTERN,
    TRACEABILITY_PATTERN,
    OVERVIEW_PATTERN,
    TASK_LIST_PATTERN,
    DEPENDENCIES_PATTERN,
    MILESTONES_PATTERN,
    REFERENCES_PATTERN,
    APPENDIX_PATTERN,
]


def classify_section(title: str, language: str = "ja") -> SectionType:
    """Classify a section title into a normalized section type.

    Args:
        title: Section title (may include section number, e.g., "1. 概要")
        language: Document language ("ja" or "en")

    Returns:
        Normalized SectionType
    """
    # Clean title: remove section numbers, extra whitespace
    clean_title = title.strip()

    # Try to match against patterns
    for pattern in SECTION_PATTERNS:
        patterns = pattern.ja_patterns if language == "ja" else pattern.en_patterns
        for pattern_text in patterns:
            if pattern_text in clean_title:
                return pattern.section_type

    return SectionType.UNKNOWN


def get_section_pattern(section_type: SectionType) -> BaseSectionPattern | None:
    """Get pattern definition for a section type.

    Args:
        section_type: Section type to look up

    Returns:
        BaseSectionPattern instance or None if not found
    """
    for pattern in SECTION_PATTERNS:
        if pattern.section_type == section_type:
            return pattern
    return None
