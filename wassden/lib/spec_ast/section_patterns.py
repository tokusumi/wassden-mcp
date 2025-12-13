"""Section pattern configuration for multi-language document parsing.

This module defines the mapping between section titles and normalized identifiers
for both Japanese and English specification documents.
"""

from dataclasses import dataclass
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


@dataclass
class SectionPattern:
    """Pattern definition for a section type.

    Attributes:
        section_type: Normalized section type
        ja_patterns: Japanese section title patterns (e.g., ["機能要件", "機能要件(EARS)"])
        en_patterns: English section title patterns (e.g., ["Functional Requirements"])
        contains_requirements: Whether this section typically contains requirement items
        contains_tasks: Whether this section typically contains task items
    """

    section_type: SectionType
    ja_patterns: list[str]
    en_patterns: list[str]
    contains_requirements: bool = False
    contains_tasks: bool = False


# Section pattern definitions - each as individual object
# Requirements document sections
SUMMARY_PATTERN = SectionPattern(
    section_type=SectionType.SUMMARY,
    ja_patterns=["サマリー"],
    en_patterns=["Summary"],
)

GLOSSARY_PATTERN = SectionPattern(
    section_type=SectionType.GLOSSARY,
    ja_patterns=["用語集"],
    en_patterns=["Glossary"],
)

SCOPE_PATTERN = SectionPattern(
    section_type=SectionType.SCOPE,
    ja_patterns=["スコープ", "適用範囲"],
    en_patterns=["Scope"],
)

CONSTRAINTS_PATTERN = SectionPattern(
    section_type=SectionType.CONSTRAINTS,
    ja_patterns=["制約事項", "制約"],
    en_patterns=["Constraints"],
)

NON_FUNCTIONAL_REQUIREMENTS_PATTERN = SectionPattern(
    section_type=SectionType.NON_FUNCTIONAL_REQUIREMENTS,
    ja_patterns=["非機能要件"],
    en_patterns=["Non-Functional Requirements"],
    contains_requirements=True,
)

KPI_PATTERN = SectionPattern(
    section_type=SectionType.KPI,
    ja_patterns=["KPI"],
    en_patterns=["KPI", "Key Performance Indicators"],
    contains_requirements=True,
)

FUNCTIONAL_REQUIREMENTS_PATTERN = SectionPattern(
    section_type=SectionType.FUNCTIONAL_REQUIREMENTS,
    ja_patterns=["機能要件", "機能要件（EARS）"],
    en_patterns=["Functional Requirements"],
    contains_requirements=True,
)

TESTING_REQUIREMENTS_PATTERN = SectionPattern(
    section_type=SectionType.TESTING_REQUIREMENTS,
    ja_patterns=["テスト要件", "受入要件"],
    en_patterns=["Testing Requirements", "Test Requirements"],
    contains_requirements=True,
)

# Design document sections
ARCHITECTURE_PATTERN = SectionPattern(
    section_type=SectionType.ARCHITECTURE,
    ja_patterns=["アーキテクチャ", "システム構成"],
    en_patterns=["Architecture", "System Architecture"],
)

COMPONENT_DESIGN_PATTERN = SectionPattern(
    section_type=SectionType.COMPONENT_DESIGN,
    ja_patterns=["コンポーネント設計", "詳細設計"],
    en_patterns=["Component Design", "Detailed Design"],
)

DATA_PATTERN = SectionPattern(
    section_type=SectionType.DATA,
    ja_patterns=["データ", "データモデル"],
    en_patterns=["Data", "Data Model"],
)

API_PATTERN = SectionPattern(
    section_type=SectionType.API,
    ja_patterns=["API"],
    en_patterns=["API", "APIs"],
)

NON_FUNCTIONAL_PATTERN = SectionPattern(
    section_type=SectionType.NON_FUNCTIONAL,
    ja_patterns=["非機能"],
    en_patterns=["Non-Functional"],
)

TEST_PATTERN = SectionPattern(
    section_type=SectionType.TEST,
    ja_patterns=["テスト"],
    en_patterns=["Test", "Testing"],
)

TRACEABILITY_PATTERN = SectionPattern(
    section_type=SectionType.TRACEABILITY,
    ja_patterns=["トレーサビリティ", "要件追跡"],
    en_patterns=["Traceability"],
)

# Tasks document sections
OVERVIEW_PATTERN = SectionPattern(
    section_type=SectionType.OVERVIEW,
    ja_patterns=["概要"],
    en_patterns=["Overview"],
)

TASK_LIST_PATTERN = SectionPattern(
    section_type=SectionType.TASK_LIST,
    ja_patterns=["タスク一覧", "タスクリスト"],
    en_patterns=["Task List", "Tasks"],
    contains_tasks=True,
)

DEPENDENCIES_PATTERN = SectionPattern(
    section_type=SectionType.DEPENDENCIES,
    ja_patterns=["依存関係"],
    en_patterns=["Dependencies"],
)

MILESTONES_PATTERN = SectionPattern(
    section_type=SectionType.MILESTONES,
    ja_patterns=["マイルストーン"],
    en_patterns=["Milestones"],
)

# Common sections
REFERENCES_PATTERN = SectionPattern(
    section_type=SectionType.REFERENCES,
    ja_patterns=["参考資料", "参照"],
    en_patterns=["References"],
)

APPENDIX_PATTERN = SectionPattern(
    section_type=SectionType.APPENDIX,
    ja_patterns=["付録"],
    en_patterns=["Appendix"],
)

# All section patterns for iteration
SECTION_PATTERNS: list[SectionPattern] = [
    SUMMARY_PATTERN,
    GLOSSARY_PATTERN,
    SCOPE_PATTERN,
    CONSTRAINTS_PATTERN,
    NON_FUNCTIONAL_REQUIREMENTS_PATTERN,
    KPI_PATTERN,
    FUNCTIONAL_REQUIREMENTS_PATTERN,
    TESTING_REQUIREMENTS_PATTERN,
    ARCHITECTURE_PATTERN,
    COMPONENT_DESIGN_PATTERN,
    DATA_PATTERN,
    API_PATTERN,
    NON_FUNCTIONAL_PATTERN,
    TEST_PATTERN,
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


def get_section_pattern(section_type: SectionType) -> SectionPattern | None:
    """Get pattern definition for a section type.

    Args:
        section_type: Section type to look up

    Returns:
        SectionPattern or None if not found
    """
    for pattern in SECTION_PATTERNS:
        if pattern.section_type == section_type:
            return pattern
    return None
