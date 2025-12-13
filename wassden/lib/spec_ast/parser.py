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
from wassden.lib.spec_ast.id_extractor import IDExtractor
from wassden.lib.spec_ast.section_patterns import SectionType, classify_section, get_section_pattern

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
                    block = self._parse_heading(token, lines)
                    if block:
                        doc.add_child(block)
                        # Only update current_section if it's actually a SectionBlock
                        if isinstance(block, SectionBlock):
                            current_section = block

                elif token_type == "list" and current_section:
                    # Parse list items within current section
                    list_items = self._parse_list(token, lines, current_section)
                    for item in list_items:
                        current_section.add_child(item)

        return doc

    def _parse_heading(
        self, token: dict[str, Any], lines: list[str]
    ) -> SectionBlock | RequirementBlock | TaskBlock | None:
        """Parse heading token into SectionBlock, RequirementBlock, or TaskBlock.

        Args:
            token: Heading token from mistune
            lines: Document lines for line number tracking

        Returns:
            SectionBlock, RequirementBlock, TaskBlock, or None if level 1 (document title)
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

        # Check if this heading contains a requirement or task ID (e.g., "### REQ-01: Description")
        # This handles requirements/tasks written as headings instead of list items

        # Try to extract requirement ID
        req_id, req_text, req_type = IDExtractor.extract_req_id_from_text(clean_title)
        if req_id:
            # This is a requirement heading
            return RequirementBlock(
                line_start=line_num,
                line_end=line_num,
                raw_content=heading_text,
                req_id=req_id,
                req_text=req_text,
                req_type=req_type,
            )

        # Try to extract task ID
        task_id, task_text = IDExtractor.extract_task_id_from_text(clean_title)
        if task_id:
            # This is a task heading
            # Extract references and dependencies from the task text
            req_refs = list(IDExtractor.extract_all_req_ids(task_text))
            design_refs = list(IDExtractor.extract_all_dc_refs(task_text))
            dependencies = IDExtractor.extract_task_dependencies(task_text)

            return TaskBlock(
                line_start=line_num,
                line_end=line_num,
                raw_content=heading_text,
                task_id=task_id,
                task_text=task_text,
                dependencies=dependencies,
                req_refs=req_refs,
                design_refs=design_refs,
            )

        # Not a requirement or task - classify as regular section
        section_type = classify_section(clean_title, self.language.value)
        normalized_title = section_type.value

        # Create section block
        return SectionBlock(
            line_start=line_num,
            line_end=line_num,
            raw_content=heading_text,
            level=level,
            title=clean_title,
            section_number=section_number,
            normalized_title=normalized_title,
            section_type=section_type,
        )

    def _parse_list(
        self, token: dict[str, Any], lines: list[str], parent_section: SectionBlock
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

        # Get section pattern to determine if it contains requirements or tasks
        section_type = SectionType(parent_section.normalized_title) if parent_section.normalized_title else None
        section_pattern = get_section_pattern(section_type) if section_type else None

        for child in list_children:
            if isinstance(child, dict) and child.get("type") == "list_item":
                # Extract item text
                item_text = self._extract_text_from_children(child.get("children", []))

                # Find line number
                line_num = self._find_line_number(lines, item_text[:50])

                # Skip acceptance criteria items
                if IDExtractor.is_acceptance_criteria(item_text):
                    continue

                # Classify into RequirementBlock, TaskBlock, or ListItemBlock
                if section_pattern and section_pattern.contains_requirements:
                    # This section contains requirements
                    req_id, req_text, req_type = IDExtractor.extract_req_id_from_text(item_text)
                    req_block = RequirementBlock(
                        line_start=line_num,
                        line_end=line_num,
                        raw_content=item_text,
                        req_id=req_id,
                        req_text=req_text,
                        req_type=req_type,
                    )
                    items.append(req_block)

                elif section_pattern and section_pattern.contains_tasks:
                    # This section contains tasks
                    task_id, task_text = IDExtractor.extract_task_id_from_text(item_text)

                    # Extract references and dependencies
                    req_refs = list(IDExtractor.extract_all_req_ids(task_text))

                    # Extract design component references (DC-XX format)
                    design_refs = list(IDExtractor.extract_all_dc_refs(task_text))

                    # Also extract test scenario references (test-xxx format)
                    import re
                    test_pattern = r"(test-[a-z0-9]+(?:-[a-z0-9]+)*)"
                    test_scenarios = re.findall(test_pattern, task_text)
                    design_refs.extend(test_scenarios)

                    dependencies = IDExtractor.extract_task_dependencies(task_text)

                    task_block = TaskBlock(
                        line_start=line_num,
                        line_end=line_num,
                        raw_content=item_text,
                        task_id=task_id,
                        task_text=task_text,
                        dependencies=dependencies,
                        req_refs=req_refs,
                        design_refs=design_refs,
                    )
                    items.append(task_block)

                else:
                    # Generic list item
                    list_item = ListItemBlock(
                        line_start=line_num,
                        line_end=line_num,
                        raw_content=item_text,
                        content=item_text,
                        is_numbered=is_ordered,
                    )
                    items.append(list_item)

        return items

    def _extract_text_from_children(self, children: list[Any], skip_acceptance_criteria: bool = True) -> str:
        """Recursively extract text from token children.

        Args:
            children: List of child tokens
            skip_acceptance_criteria: Whether to skip acceptance criteria lists

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
                    text_parts.append(self._extract_text_from_children(child.get("children", []), skip_acceptance_criteria))
                elif child_type == "list":
                    # Extract list content to check if it's acceptance criteria
                    list_text = self._extract_text_from_children(child.get("children", []), skip_acceptance_criteria=False)
                    # Skip only if it contains acceptance criteria keywords
                    if skip_acceptance_criteria and IDExtractor.is_acceptance_criteria(list_text):
                        continue
                    # Include nested lists (for REQ/DC/dependencies)
                    text_parts.append(" " + list_text)
                elif "children" in child:
                    text_parts.append(self._extract_text_from_children(child["children"], skip_acceptance_criteria))
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
