"""Unit tests for spec_ast parser."""

from wassden.language_types import Language
from wassden.lib.spec_ast.blocks import BlockType, ListItemBlock, SectionBlock
from wassden.lib.spec_ast.parser import SpecMarkdownParser


class TestSpecMarkdownParser:
    """Tests for SpecMarkdownParser."""

    def test_create_parser(self) -> None:
        """Test creating a parser."""
        parser = SpecMarkdownParser()
        assert parser.language == Language.JAPANESE

        parser_en = SpecMarkdownParser(Language.ENGLISH)
        assert parser_en.language == Language.ENGLISH

    def test_parse_empty_document(self) -> None:
        """Test parsing empty document."""
        parser = SpecMarkdownParser()
        doc = parser.parse("")

        assert doc.block_type == BlockType.DOCUMENT
        assert doc.language == Language.JAPANESE
        assert len(doc.children) == 0

    def test_parse_simple_sections(self) -> None:
        """Test parsing simple sections."""
        markdown = """## Overview
This is an overview.

## Requirements
Some requirements here.
"""
        parser = SpecMarkdownParser()
        doc = parser.parse(markdown)

        assert len(doc.children) == 2
        assert all(isinstance(child, SectionBlock) for child in doc.children)

        section1 = doc.children[0]
        assert isinstance(section1, SectionBlock)
        assert section1.title == "Overview"
        assert section1.level == 2

        section2 = doc.children[1]
        assert isinstance(section2, SectionBlock)
        assert section2.title == "Requirements"
        assert section2.level == 2

    def test_parse_numbered_sections(self) -> None:
        """Test parsing sections with numbers."""
        markdown = """## 1. Overview
Content here.

## 2. Requirements
More content.

## 6.1 Testing
Subsection.
"""
        parser = SpecMarkdownParser()
        doc = parser.parse(markdown)

        assert len(doc.children) == 3

        section1 = doc.children[0]
        assert isinstance(section1, SectionBlock)
        assert section1.section_number == "1"
        assert section1.title == "Overview"

        section2 = doc.children[1]
        assert isinstance(section2, SectionBlock)
        assert section2.section_number == "2"
        assert section2.title == "Requirements"

        section3 = doc.children[2]
        assert isinstance(section3, SectionBlock)
        assert section3.section_number == "6.1"
        assert section3.title == "Testing"

    def test_parse_section_with_list(self) -> None:
        """Test parsing section containing a list."""
        markdown = """## Requirements

- REQ-01: First requirement
- REQ-02: Second requirement
- REQ-03: Third requirement
"""
        parser = SpecMarkdownParser()
        doc = parser.parse(markdown)

        assert len(doc.children) == 1
        section = doc.children[0]
        assert isinstance(section, SectionBlock)
        assert section.title == "Requirements"

        # Check list items
        assert len(section.children) == 3
        assert all(isinstance(child, ListItemBlock) for child in section.children)

        item1 = section.children[0]
        assert isinstance(item1, ListItemBlock)
        assert "REQ-01: First requirement" in item1.content

    def test_parse_ordered_list(self) -> None:
        """Test parsing numbered list."""
        markdown = """## Tasks

1. First task
2. Second task
3. Third task
"""
        parser = SpecMarkdownParser()
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert isinstance(section, SectionBlock)

        assert len(section.children) == 3
        for item in section.children:
            assert isinstance(item, ListItemBlock)
            assert item.is_numbered is True

    def test_parse_unordered_list(self) -> None:
        """Test parsing bullet list."""
        markdown = """## Notes

- First note
- Second note
- Third note
"""
        parser = SpecMarkdownParser()
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert isinstance(section, SectionBlock)

        assert len(section.children) == 3
        for item in section.children:
            assert isinstance(item, ListItemBlock)
            assert item.is_numbered is False

    def test_parse_multiple_sections_with_lists(self) -> None:
        """Test parsing multiple sections each with lists."""
        markdown = """## Section 1

- Item 1A
- Item 1B

## Section 2

- Item 2A
- Item 2B
- Item 2C
"""
        parser = SpecMarkdownParser()
        doc = parser.parse(markdown)

        assert len(doc.children) == 2

        section1 = doc.children[0]
        assert isinstance(section1, SectionBlock)
        assert len(section1.children) == 2

        section2 = doc.children[1]
        assert isinstance(section2, SectionBlock)
        assert len(section2.children) == 3

    def test_parse_nested_headings(self) -> None:
        """Test parsing different heading levels."""
        markdown = """## Level 2

### Level 3

#### Level 4
"""
        parser = SpecMarkdownParser()
        doc = parser.parse(markdown)

        # All headings become sections at document level (no nesting yet in Phase 1)
        assert len(doc.children) == 3

        assert doc.children[0].level == 2  # type: ignore[attr-defined]
        assert doc.children[1].level == 3  # type: ignore[attr-defined]
        assert doc.children[2].level == 4  # type: ignore[attr-defined]

    def test_skip_level_1_heading(self) -> None:
        """Test that level 1 headings are skipped."""
        markdown = """# Document Title

## Section 1

Content here.
"""
        parser = SpecMarkdownParser()
        doc = parser.parse(markdown)

        # Level 1 heading should be skipped
        assert len(doc.children) == 1
        assert doc.children[0].title == "Section 1"  # type: ignore[attr-defined]

    def test_parse_japanese_content(self) -> None:
        """Test parsing Japanese content."""
        markdown = """## 概要

これは概要です。

## 機能要件

- REQ-01: システムは入力を検証すること
- REQ-02: システムは結果を表示すること
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        assert doc.language == Language.JAPANESE
        assert len(doc.children) == 2

        section1 = doc.children[0]
        assert isinstance(section1, SectionBlock)
        assert section1.title == "概要"

        section2 = doc.children[1]
        assert isinstance(section2, SectionBlock)
        assert section2.title == "機能要件"
        assert len(section2.children) == 2

    def test_parse_with_inline_code(self) -> None:
        """Test parsing text with inline code."""
        markdown = """## API

- REQ-01: System shall provide `GET /api/users` endpoint
- REQ-02: Return `application/json` content type
"""
        parser = SpecMarkdownParser()
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert isinstance(section, SectionBlock)

        item1 = section.children[0]
        assert isinstance(item1, ListItemBlock)
        # Inline code should be included in content
        assert "GET /api/users" in item1.content or "`GET /api/users`" in item1.content


class TestParserHelperMethods:
    """Tests for parser helper methods."""

    def test_extract_section_number_dotted(self) -> None:
        """Test extracting section number with dot."""
        parser = SpecMarkdownParser()
        number, title = parser._extract_section_number("1. Overview")
        assert number == "1"
        assert title == "Overview"

        number, title = parser._extract_section_number("6.1 Testing")
        assert number == "6.1"
        assert title == "Testing"

    def test_extract_section_number_no_number(self) -> None:
        """Test extracting section when no number present."""
        parser = SpecMarkdownParser()
        number, title = parser._extract_section_number("Overview")
        assert number is None
        assert title == "Overview"

    def test_extract_section_number_complex(self) -> None:
        """Test extracting complex section numbers."""
        parser = SpecMarkdownParser()

        number, title = parser._extract_section_number("3.2.1. Detailed Requirements")
        assert number == "3.2.1"
        assert title == "Detailed Requirements"

    def test_find_line_number(self) -> None:
        """Test finding line number for text."""
        parser = SpecMarkdownParser()
        lines = ["First line", "Second line with unique text", "Third line"]

        line_num = parser._find_line_number(lines, "unique text")
        assert line_num == 2

        line_num = parser._find_line_number(lines, "First")
        assert line_num == 1

    def test_find_line_number_not_found(self) -> None:
        """Test finding line number when text not found."""
        parser = SpecMarkdownParser()
        lines = ["First line", "Second line"]

        line_num = parser._find_line_number(lines, "nonexistent")
        assert line_num == 1  # Default to 1

    def test_extract_text_from_children(self) -> None:
        """Test extracting text from token children."""
        parser = SpecMarkdownParser()

        # Simple text token
        children = [{"type": "text", "raw": "Hello World"}]
        text = parser._extract_text_from_children(children)
        assert text == "Hello World"

        # Nested children
        children = [{"type": "paragraph", "children": [{"type": "text", "raw": "Nested text"}]}]
        text = parser._extract_text_from_children(children)
        assert text == "Nested text"

        # Multiple children
        children = [{"type": "text", "raw": "Hello "}, {"type": "text", "raw": "World"}]
        text = parser._extract_text_from_children(children)
        assert text == "Hello World"
