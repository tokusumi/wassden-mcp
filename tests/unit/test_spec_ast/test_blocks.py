"""Unit tests for spec_ast block classes."""

from wassden.language_types import Language
from wassden.lib.spec_ast.blocks import (
    BlockType,
    DocumentBlock,
    ListItemBlock,
    RequirementBlock,
    SectionBlock,
    TaskBlock,
)


class TestDocumentBlock:
    """Tests for DocumentBlock."""

    def test_create_document_block(self) -> None:
        """Test creating a document block."""
        doc = DocumentBlock(
            line_start=1,
            line_end=100,
            raw_content="# Document",
            title="Test Document",
            language=Language.ENGLISH,
        )
        assert doc.block_type == BlockType.DOCUMENT
        assert doc.title == "Test Document"
        assert doc.language == Language.ENGLISH
        assert len(doc.children) == 0
        assert doc.parent is None

    def test_document_block_defaults(self) -> None:
        """Test document block with default values."""
        doc = DocumentBlock(line_start=1, line_end=1, raw_content="")
        assert doc.title == ""
        assert doc.language == Language.JAPANESE
        assert doc.block_type == BlockType.DOCUMENT

    def test_document_block_str(self) -> None:
        """Test string representation of document block."""
        doc = DocumentBlock(line_start=1, line_end=10, raw_content="", title="Test Doc", language=Language.ENGLISH)
        result = str(doc)
        assert "Document" in result
        assert "Test Doc" in result
        assert "en" in result
        assert "0 sections" in result


class TestSectionBlock:
    """Tests for SectionBlock."""

    def test_create_section_block(self) -> None:
        """Test creating a section block."""
        section = SectionBlock(
            line_start=5,
            line_end=20,
            raw_content="## Overview",
            level=2,
            title="Overview",
            normalized_title="overview",
        )
        assert section.block_type == BlockType.SECTION
        assert section.level == 2
        assert section.title == "Overview"
        assert section.normalized_title == "overview"
        assert section.section_number is None

    def test_section_block_with_number(self) -> None:
        """Test section block with section number."""
        section = SectionBlock(
            line_start=5,
            line_end=20,
            raw_content="## 1. Overview",
            level=2,
            title="Overview",
            section_number="1",
            normalized_title="overview",
        )
        assert section.section_number == "1"

    def test_section_block_str(self) -> None:
        """Test string representation of section block."""
        section = SectionBlock(
            line_start=5, line_end=20, raw_content="## Test", level=2, title="Test Section", section_number="3.1"
        )
        result = str(section)
        assert "Section" in result
        assert "3.1" in result
        assert "Test Section" in result
        assert "level=2" in result


class TestRequirementBlock:
    """Tests for RequirementBlock."""

    def test_create_requirement_block(self) -> None:
        """Test creating a requirement block."""
        req = RequirementBlock(
            line_start=10,
            line_end=10,
            raw_content="- REQ-01: System shall validate input",
            req_id="REQ-01",
            req_text="System shall validate input",
            req_type="REQ",
        )
        assert req.block_type == BlockType.REQUIREMENT
        assert req.req_id == "REQ-01"
        assert req.req_text == "System shall validate input"
        assert req.req_type == "REQ"

    def test_requirement_block_types(self) -> None:
        """Test different requirement types."""
        nfr = RequirementBlock(line_start=1, line_end=1, raw_content="", req_id="NFR-01", req_type="NFR")
        assert nfr.req_type == "NFR"

        kpi = RequirementBlock(line_start=1, line_end=1, raw_content="", req_id="KPI-01", req_type="KPI")
        assert kpi.req_type == "KPI"

        tr = RequirementBlock(line_start=1, line_end=1, raw_content="", req_id="TR-01", req_type="TR")
        assert tr.req_type == "TR"

    def test_requirement_block_str(self) -> None:
        """Test string representation of requirement block."""
        req = RequirementBlock(
            line_start=1,
            line_end=1,
            raw_content="",
            req_id="REQ-01",
            req_text="This is a test requirement with some text",
        )
        result = str(req)
        assert "Requirement" in result
        assert "REQ-01" in result
        assert "test requirement" in result

    def test_requirement_block_str_long_text(self) -> None:
        """Test string representation truncates long text."""
        long_text = "A" * 100
        req = RequirementBlock(line_start=1, line_end=1, raw_content="", req_id="REQ-01", req_text=long_text)
        result = str(req)
        assert len(result) < len(long_text) + 50
        assert "..." in result


class TestTaskBlock:
    """Tests for TaskBlock."""

    def test_create_task_block(self) -> None:
        """Test creating a task block."""
        task = TaskBlock(
            line_start=15,
            line_end=15,
            raw_content="- TASK-01-01: Implement feature",
            task_id="TASK-01-01",
            task_text="Implement feature",
        )
        assert task.block_type == BlockType.TASK
        assert task.task_id == "TASK-01-01"
        assert task.task_text == "Implement feature"
        assert len(task.dependencies) == 0
        assert len(task.req_refs) == 0
        assert len(task.design_refs) == 0

    def test_task_block_with_references(self) -> None:
        """Test task block with requirement and design references."""
        task = TaskBlock(
            line_start=1,
            line_end=1,
            raw_content="",
            task_id="TASK-01-01",
            task_text="Implement REQ-01 using DC-03",
            dependencies=["TASK-01-02"],
            req_refs=["REQ-01", "REQ-02"],
            design_refs=["DC-03"],
        )
        assert task.dependencies == ["TASK-01-02"]
        assert task.req_refs == ["REQ-01", "REQ-02"]
        assert task.design_refs == ["DC-03"]

    def test_task_block_str(self) -> None:
        """Test string representation of task block."""
        task = TaskBlock(
            line_start=1,
            line_end=1,
            raw_content="",
            task_id="TASK-01-01",
            task_text="Test task",
            dependencies=["TASK-02-01"],
        )
        result = str(task)
        assert "Task" in result
        assert "TASK-01-01" in result
        assert "Test task" in result
        assert "deps=1" in result


class TestListItemBlock:
    """Tests for ListItemBlock."""

    def test_create_list_item_block(self) -> None:
        """Test creating a list item block."""
        item = ListItemBlock(line_start=8, line_end=8, raw_content="- Generic item", content="Generic item")
        assert item.block_type == BlockType.LIST_ITEM
        assert item.content == "Generic item"
        assert item.is_numbered is False

    def test_numbered_list_item(self) -> None:
        """Test numbered list item."""
        item = ListItemBlock(
            line_start=1, line_end=1, raw_content="1. First item", content="First item", is_numbered=True
        )
        assert item.is_numbered is True

    def test_list_item_str(self) -> None:
        """Test string representation of list item."""
        item = ListItemBlock(line_start=1, line_end=1, raw_content="", content="Test item")
        result = str(item)
        assert "ListItem" in result
        assert "bullet" in result
        assert "Test item" in result


class TestBlockTreeNavigation:
    """Tests for block tree navigation methods."""

    def test_add_child(self) -> None:
        """Test adding child blocks."""
        doc = DocumentBlock(line_start=1, line_end=100, raw_content="")
        section = SectionBlock(line_start=5, line_end=20, raw_content="", title="Test Section")

        doc.add_child(section)

        assert len(doc.children) == 1
        assert doc.children[0] == section
        assert section.parent == doc

    def test_get_context_path_simple(self) -> None:
        """Test getting context path for simple hierarchy."""
        doc = DocumentBlock(line_start=1, line_end=100, raw_content="", title="Main Doc")
        section = SectionBlock(line_start=5, line_end=20, raw_content="", title="Section 1")
        req = RequirementBlock(line_start=10, line_end=10, raw_content="", req_id="REQ-01")

        doc.add_child(section)
        section.add_child(req)

        path = req.get_context_path()
        assert path == ["Main Doc", "Section 1", "REQ-01"]

    def test_get_context_path_deep(self) -> None:
        """Test getting context path for deep hierarchy."""
        doc = DocumentBlock(line_start=1, line_end=100, raw_content="", title="Root")
        section1 = SectionBlock(line_start=5, line_end=50, raw_content="", title="Level 1")
        section2 = SectionBlock(line_start=10, line_end=30, raw_content="", title="Level 2")
        task = TaskBlock(line_start=15, line_end=15, raw_content="", task_id="TASK-01-01")

        doc.add_child(section1)
        section1.add_child(section2)
        section2.add_child(task)

        path = task.get_context_path()
        assert path == ["Root", "Level 1", "Level 2", "TASK-01-01"]

    def test_get_all_descendants(self) -> None:
        """Test getting all descendants."""
        doc = DocumentBlock(line_start=1, line_end=100, raw_content="")
        section1 = SectionBlock(line_start=5, line_end=30, raw_content="", title="Section 1")
        section2 = SectionBlock(line_start=35, line_end=60, raw_content="", title="Section 2")
        req1 = RequirementBlock(line_start=10, line_end=10, raw_content="", req_id="REQ-01")
        req2 = RequirementBlock(line_start=40, line_end=40, raw_content="", req_id="REQ-02")

        doc.add_child(section1)
        doc.add_child(section2)
        section1.add_child(req1)
        section2.add_child(req2)

        descendants = doc.get_all_descendants()
        assert len(descendants) == 4
        assert section1 in descendants
        assert section2 in descendants
        assert req1 in descendants
        assert req2 in descendants

    def test_get_blocks_by_type(self) -> None:
        """Test filtering blocks by type."""
        doc = DocumentBlock(line_start=1, line_end=100, raw_content="")
        section1 = SectionBlock(line_start=5, line_end=30, raw_content="", title="Section 1")
        section2 = SectionBlock(line_start=35, line_end=60, raw_content="", title="Section 2")
        req1 = RequirementBlock(line_start=10, line_end=10, raw_content="", req_id="REQ-01")
        req2 = RequirementBlock(line_start=40, line_end=40, raw_content="", req_id="REQ-02")
        task = TaskBlock(line_start=15, line_end=15, raw_content="", task_id="TASK-01-01")

        doc.add_child(section1)
        doc.add_child(section2)
        section1.add_child(req1)
        section1.add_child(task)
        section2.add_child(req2)

        # Get all sections
        sections = doc.get_blocks_by_type(BlockType.SECTION)
        assert len(sections) == 2
        assert all(isinstance(s, SectionBlock) for s in sections)

        # Get all requirements
        requirements = doc.get_blocks_by_type(BlockType.REQUIREMENT)
        assert len(requirements) == 2
        assert all(isinstance(r, RequirementBlock) for r in requirements)

        # Get all tasks
        tasks = doc.get_blocks_by_type(BlockType.TASK)
        assert len(tasks) == 1
        assert isinstance(tasks[0], TaskBlock)

    def test_empty_tree(self) -> None:
        """Test navigation methods on empty tree."""
        doc = DocumentBlock(line_start=1, line_end=1, raw_content="")

        assert len(doc.get_all_descendants()) == 0
        assert len(doc.get_blocks_by_type(BlockType.SECTION)) == 0
        # Empty title results in empty path
        assert doc.get_context_path() == []


class TestBlockMetadata:
    """Tests for block metadata."""

    def test_metadata_storage(self) -> None:
        """Test storing arbitrary metadata."""
        block = SectionBlock(line_start=1, line_end=10, raw_content="", title="Test")
        block.metadata["custom_key"] = "custom_value"
        block.metadata["count"] = 42

        assert block.metadata["custom_key"] == "custom_value"
        assert block.metadata["count"] == 42

    def test_metadata_defaults_empty(self) -> None:
        """Test metadata defaults to empty dict."""
        block = RequirementBlock(line_start=1, line_end=1, raw_content="")
        assert isinstance(block.metadata, dict)
        assert len(block.metadata) == 0
