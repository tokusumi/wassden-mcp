"""Spec block classes for structured document representation.

This module defines the object hierarchy for representing specification documents as AST.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from wassden.language_types import Language

if TYPE_CHECKING:
    from .section_patterns import SectionType

# Constants for string representation
_TEXT_PREVIEW_LENGTH = 50


class BlockType(Enum):
    """Types of spec blocks."""

    DOCUMENT = "document"
    SECTION = "section"
    REQUIREMENT = "requirement"
    TASK = "task"
    LIST_ITEM = "list_item"
    PARAGRAPH = "paragraph"
    HEADING = "heading"


@dataclass
class SpecBlock(ABC):
    """Base class for all spec document blocks.

    Attributes:
        block_type: Type of this block
        line_start: Starting line number in source document (1-indexed)
        line_end: Ending line number in source document (1-indexed)
        raw_content: Raw markdown content of this block
        parent: Parent block in the tree (None for root)
        children: Child blocks
        metadata: Additional metadata for this block
    """

    block_type: BlockType
    line_start: int
    line_end: int
    raw_content: str
    parent: SpecBlock | None = None
    children: list[SpecBlock] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_child(self, child: SpecBlock) -> None:
        """Add a child block and set its parent reference."""
        child.parent = self
        self.children.append(child)

    def get_context_path(self) -> list[str]:
        """Get path from root to this block.

        Returns:
            List of titles/identifiers from root to this block
        """
        path: list[str] = []
        current: SpecBlock | None = self
        while current:
            if hasattr(current, "title") and current.title:
                path.insert(0, current.title)
            elif hasattr(current, "req_id") and current.req_id:
                path.insert(0, current.req_id)
            elif hasattr(current, "task_id") and current.task_id:
                path.insert(0, current.task_id)
            current = current.parent
        return path

    def get_all_descendants(self) -> list[SpecBlock]:
        """Get all descendant blocks recursively.

        Returns:
            List of all descendant blocks
        """
        descendants: list[SpecBlock] = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def get_blocks_by_type(self, block_type: BlockType) -> list[SpecBlock]:
        """Get all descendant blocks of a specific type.

        Args:
            block_type: Type of blocks to find

        Returns:
            List of blocks matching the type
        """
        return [block for block in self.get_all_descendants() if block.block_type == block_type]

    @abstractmethod
    def __str__(self) -> str:
        """String representation of the block."""
        ...


@dataclass
class DocumentBlock(SpecBlock):
    """Root document block.

    Attributes:
        title: Document title
        language: Document language
    """

    title: str = ""
    language: Language = Language.JAPANESE
    block_type: BlockType = field(init=False, default=BlockType.DOCUMENT)

    def __str__(self) -> str:
        """String representation of the document block."""
        return f"Document({self.title}, {self.language.value}, {len(self.children)} sections)"


@dataclass
class SectionBlock(SpecBlock):
    """Section block (## heading).

    Attributes:
        level: Heading level (2 for ##, 3 for ###, etc.)
        title: Section title
        section_number: Optional section number (e.g., "1", "6.1")
        normalized_title: Normalized section name (e.g., "functional_requirements")
        section_type: Section type enum (from SectionType)
    """

    level: int = 2
    title: str = ""
    section_number: str | None = None
    normalized_title: str = ""
    section_type: SectionType | None = None
    block_type: BlockType = field(init=False, default=BlockType.SECTION)

    def __str__(self) -> str:
        """String representation of the section block."""
        section_id = f"{self.section_number}. " if self.section_number else ""
        return f"Section({section_id}{self.title}, level={self.level}, {len(self.children)} items)"


@dataclass
class RequirementBlock(SpecBlock):
    """Requirement item block.

    Attributes:
        req_id: Requirement ID (REQ-01, NFR-02, KPI-03, TR-04, etc.)
        req_text: Actual requirement text (without ID prefix)
        req_type: Requirement type prefix (REQ, NFR, KPI, TR)
    """

    req_id: str | None = None
    req_text: str = ""
    req_type: str = "REQ"
    block_type: BlockType = field(init=False, default=BlockType.REQUIREMENT)

    def __str__(self) -> str:
        """String representation of the requirement block."""
        text_preview = (
            self.req_text[:_TEXT_PREVIEW_LENGTH] + "..." if len(self.req_text) > _TEXT_PREVIEW_LENGTH else self.req_text
        )
        return f"Requirement({self.req_id}: {text_preview})"


@dataclass
class TaskBlock(SpecBlock):
    """Task item block.

    Attributes:
        task_id: Task ID (TASK-01-01, TASK-02-03-05, etc.)
        task_text: Task description text
        dependencies: List of task IDs this task depends on
        req_refs: List of requirement IDs referenced (REQ-XX)
        design_refs: List of design component references (DC-XX)
    """

    task_id: str | None = None
    task_text: str = ""
    dependencies: list[str] = field(default_factory=list)
    req_refs: list[str] = field(default_factory=list)
    design_refs: list[str] = field(default_factory=list)
    block_type: BlockType = field(init=False, default=BlockType.TASK)

    def __str__(self) -> str:
        """String representation of the task block."""
        text_preview = (
            self.task_text[:_TEXT_PREVIEW_LENGTH] + "..."
            if len(self.task_text) > _TEXT_PREVIEW_LENGTH
            else self.task_text
        )
        deps_info = f", deps={len(self.dependencies)}" if self.dependencies else ""
        return f"Task({self.task_id}: {text_preview}{deps_info})"


@dataclass
class ListItemBlock(SpecBlock):
    """Generic list item block (not classified as requirement or task).

    Attributes:
        content: List item content
        is_numbered: Whether this is a numbered list item
    """

    content: str = ""
    is_numbered: bool = False
    block_type: BlockType = field(init=False, default=BlockType.LIST_ITEM)

    def __str__(self) -> str:
        """String representation of the list item block."""
        content_preview = (
            self.content[:_TEXT_PREVIEW_LENGTH] + "..." if len(self.content) > _TEXT_PREVIEW_LENGTH else self.content
        )
        list_type = "numbered" if self.is_numbered else "bullet"
        return f"ListItem({list_type}: {content_preview})"
