"""Spec markdown parser using mistune for AST-based document parsing."""

import re
from typing import Any

import mistune

from wassden.language_types import Language
from wassden.lib.spec_ast.blocks import (
    DocumentBlock,
    ListItemBlock,
    RequirementBlock,
    SectionBlock,
    TaskBlock,
)

# Constants
_LINE_SEARCH_LENGTH = 30


class SpecMarkdownParser:
    """AST-based markdown parser for spec documents.

    Uses mistune v3 to parse markdown into a structured block tree.
    """

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize parser.

        Args:
            language: Document language for section classification
        """
        self.language = language
        self._markdown = mistune.create_markdown(renderer="ast")

    def parse(self, markdown_text: str) -> DocumentBlock:
        """Parse markdown text into structured block tree.

        Args:
            markdown_text: Markdown document text

        Returns:
            DocumentBlock root node
        """
        # Parse markdown to AST tokens
        tokens = self._markdown(markdown_text)

        # Create document block
        lines = markdown_text.split("\n")
        doc = DocumentBlock(
            line_start=1,
            line_end=len(lines),
            raw_content=markdown_text,
            title="",  # Will be set if first heading is level 1
            language=self.language,
        )

        # Track current section for list items
        current_section: SectionBlock | None = None

        # Process tokens and build tree
        for token in tokens:
            if isinstance(token, dict):
                token_type = token.get("type", "")

                if token_type == "heading":
                    section = self._parse_heading(token, lines)
                    if section:
                        doc.add_child(section)
                        current_section = section

                elif token_type == "list" and current_section:
                    # Parse list items within current section
                    list_items = self._parse_list(token, lines, current_section)
                    for item in list_items:
                        current_section.add_child(item)

        return doc

    def _parse_heading(self, token: dict[str, Any], lines: list[str]) -> SectionBlock | None:
        """Parse heading token into SectionBlock.

        Args:
            token: Heading token from mistune
            lines: Document lines for line number tracking

        Returns:
            SectionBlock or None if level 1 (document title)
        """
        # In mistune v3, level is in attrs dict
        attrs = token.get("attrs", {})
        level = attrs.get("level", 2)

        # Extract heading text from children
        heading_text = self._extract_text_from_children(token.get("children", []))

        # Skip level 1 headings (treated as document title)
        if level == 1:
            return None

        # Estimate line number by searching in original text
        line_num = self._find_line_number(lines, heading_text)

        # Extract section number if present (e.g., "1. Overview" -> "1")
        section_number, clean_title = self._extract_section_number(heading_text)

        # Create section block
        return SectionBlock(
            line_start=line_num,
            line_end=line_num,
            raw_content=heading_text,
            level=level,
            title=clean_title,
            section_number=section_number,
            normalized_title="",  # Will be set in Phase 2
        )

    def _parse_list(
        self, token: dict[str, Any], lines: list[str], _parent_section: SectionBlock
    ) -> list[RequirementBlock | TaskBlock | ListItemBlock]:
        """Parse list token into list item blocks.

        Args:
            token: List token from mistune
            lines: Document lines for line number tracking
            parent_section: Parent section containing this list

        Returns:
            List of parsed blocks (RequirementBlock, TaskBlock, or ListItemBlock)
        """
        items: list[RequirementBlock | TaskBlock | ListItemBlock] = []
        list_children = token.get("children", [])
        # In mistune v3, ordered is in attrs dict
        attrs = token.get("attrs", {})
        is_ordered = attrs.get("ordered", False)

        for child in list_children:
            if isinstance(child, dict) and child.get("type") == "list_item":
                # Extract item text
                item_text = self._extract_text_from_children(child.get("children", []))

                # Find line number
                line_num = self._find_line_number(lines, item_text[:50])

                # Create generic list item for now
                # In Phase 2, we'll classify into RequirementBlock or TaskBlock
                item = ListItemBlock(
                    line_start=line_num,
                    line_end=line_num,
                    raw_content=item_text,
                    content=item_text,
                    is_numbered=is_ordered,
                )
                items.append(item)

        return items

    def _extract_text_from_children(self, children: list[Any]) -> str:
        """Recursively extract text from token children.

        Args:
            children: List of child tokens

        Returns:
            Extracted text content
        """
        text_parts: list[str] = []
        for child in children:
            if isinstance(child, dict):
                child_type = child.get("type", "")
                if child_type in ("text", "codespan"):
                    text_parts.append(child.get("raw", ""))
                elif child_type == "block_text":
                    # mistune v3 wraps list item content in block_text
                    text_parts.append(self._extract_text_from_children(child.get("children", [])))
                elif "children" in child:
                    text_parts.append(self._extract_text_from_children(child["children"]))
            elif isinstance(child, str):
                text_parts.append(child)

        return "".join(text_parts).strip()

    def _find_line_number(self, lines: list[str], text_snippet: str) -> int:
        """Find line number by searching for text snippet.

        Args:
            lines: Document lines
            text_snippet: Text to search for

        Returns:
            Line number (1-indexed), defaults to 1 if not found
        """
        # Search for the snippet in lines
        search_text = text_snippet[:_LINE_SEARCH_LENGTH] if len(text_snippet) > _LINE_SEARCH_LENGTH else text_snippet
        for i, line in enumerate(lines, 1):
            if search_text in line:
                return i
        return 1

    def _extract_section_number(self, heading_text: str) -> tuple[str | None, str]:
        """Extract section number from heading text.

        Args:
            heading_text: Raw heading text (e.g., "1. Overview" or "6.1 Testing")

        Returns:
            Tuple of (section_number, clean_title)
        """
        # Pattern: "1. Title" or "1 Title" or "6.1 Title"
        pattern = r"^(\d+(?:\.\d+)*)[.\s]+(.+)$"
        match = re.match(pattern, heading_text.strip())

        if match:
            section_number = match.group(1)
            clean_title = match.group(2).strip()
            return section_number, clean_title

        return None, heading_text.strip()
