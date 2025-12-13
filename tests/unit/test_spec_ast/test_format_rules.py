"""Tests for format validation rules."""


from wassden.lib.spec_ast.blocks import DocumentBlock, RequirementBlock, TaskBlock
from wassden.lib.spec_ast.format_rules import (
    DuplicateRequirementIDRule,
    DuplicateTaskIDRule,
    RequirementIDFormatRule,
    TaskIDFormatRule,
)
from wassden.lib.spec_ast.validation_rules import ValidationContext


class TestRequirementIDFormatRule:
    """Tests for RequirementIDFormatRule."""

    def test_rule_properties(self):
        """Test rule properties."""
        rule = RequirementIDFormatRule()

        assert rule.rule_id == "FORMAT-REQ-001"
        assert rule.rule_name == "Requirement ID Format"
        assert "REQ-XX" in rule.description

    def test_valid_req_ids(self):
        """Test validation with valid requirement IDs."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")

        # Add requirement blocks with valid IDs
        valid_ids = ["REQ-01", "REQ-10", "REQ-99"]
        for req_id in valid_ids:
            req_block = RequirementBlock(
                line_start=10,
                line_end=11,
                raw_content=f"- {req_id}: Test requirement",
                req_id=req_id,
                req_text="Test requirement",
            )
            document.children.append(req_block)

        rule = RequirementIDFormatRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_invalid_req_ids(self):
        """Test validation with invalid requirement IDs."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")

        # Add requirement blocks with invalid IDs
        invalid_ids = ["REQ-00", "REQ-ABC", "REQ-1", "REQ-100"]
        for req_id in invalid_ids:
            req_block = RequirementBlock(
                line_start=10,
                line_end=11,
                raw_content=f"- {req_id}: Test requirement",
                req_id=req_id,
                req_text="Test requirement",
            )
            document.children.append(req_block)

        rule = RequirementIDFormatRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert not result.is_valid
        assert len(result.errors) == 4  # All 4 invalid IDs should be reported


class TestTaskIDFormatRule:
    """Tests for TaskIDFormatRule."""

    def test_rule_properties(self):
        """Test rule properties."""
        rule = TaskIDFormatRule()

        assert rule.rule_id == "FORMAT-TASK-001"
        assert rule.rule_name == "Task ID Format"
        assert "TASK-XX-XX" in rule.description

    def test_valid_task_ids(self):
        """Test validation with valid task IDs."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Tasks")

        # Add task blocks with valid IDs
        valid_ids = ["TASK-01-01", "TASK-10-20", "TASK-99-99", "TASK-01-01-01"]
        for task_id in valid_ids:
            task_block = TaskBlock(
                line_start=10,
                line_end=11,
                raw_content=f"- {task_id}: Test task",
                task_id=task_id,
                task_text="Test task",
            )
            document.children.append(task_block)

        rule = TaskIDFormatRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_invalid_task_ids(self):
        """Test validation with invalid task IDs."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Tasks")

        # Add task blocks with invalid IDs
        invalid_ids = ["TASK-00-01", "TASK-01-00", "TASK-ABC-01", "TASK-01"]
        for task_id in invalid_ids:
            task_block = TaskBlock(
                line_start=10,
                line_end=11,
                raw_content=f"- {task_id}: Test task",
                task_id=task_id,
                task_text="Test task",
            )
            document.children.append(task_block)

        rule = TaskIDFormatRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert not result.is_valid
        assert len(result.errors) == 4


class TestDuplicateRequirementIDRule:
    """Tests for DuplicateRequirementIDRule."""

    def test_rule_properties(self):
        """Test rule properties."""
        rule = DuplicateRequirementIDRule()

        assert rule.rule_id == "FORMAT-REQ-002"
        assert rule.rule_name == "Duplicate Requirement ID"
        assert "duplicate" in rule.description.lower()

    def test_no_duplicates(self):
        """Test validation with no duplicate IDs."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")

        # Add unique requirement IDs
        unique_ids = ["REQ-01", "REQ-02", "REQ-03"]
        for req_id in unique_ids:
            req_block = RequirementBlock(
                line_start=10,
                line_end=11,
                raw_content=f"- {req_id}: Test requirement",
                req_id=req_id,
                req_text="Test requirement",
            )
            document.children.append(req_block)

        rule = DuplicateRequirementIDRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_with_duplicates(self):
        """Test validation with duplicate IDs."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")

        # Add duplicate requirement IDs
        duplicate_ids = ["REQ-01", "REQ-02", "REQ-01", "REQ-02"]
        for req_id in duplicate_ids:
            req_block = RequirementBlock(
                line_start=10,
                line_end=11,
                raw_content=f"- {req_id}: Test requirement",
                req_id=req_id,
                req_text="Test requirement",
            )
            document.children.append(req_block)

        rule = DuplicateRequirementIDRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert not result.is_valid
        assert len(result.errors) == 4  # All occurrences of duplicates reported
        assert all("Duplicate REQ-ID" in error.message for error in result.errors)


class TestDuplicateTaskIDRule:
    """Tests for DuplicateTaskIDRule."""

    def test_rule_properties(self):
        """Test rule properties."""
        rule = DuplicateTaskIDRule()

        assert rule.rule_id == "FORMAT-TASK-002"
        assert rule.rule_name == "Duplicate Task ID"
        assert "duplicate" in rule.description.lower()

    def test_no_duplicates(self):
        """Test validation with no duplicate IDs."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Tasks")

        # Add unique task IDs
        unique_ids = ["TASK-01-01", "TASK-01-02", "TASK-02-01"]
        for task_id in unique_ids:
            task_block = TaskBlock(
                line_start=10,
                line_end=11,
                raw_content=f"- {task_id}: Test task",
                task_id=task_id,
                task_text="Test task",
            )
            document.children.append(task_block)

        rule = DuplicateTaskIDRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_with_duplicates(self):
        """Test validation with duplicate IDs."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Tasks")

        # Add duplicate task IDs
        duplicate_ids = ["TASK-01-01", "TASK-01-02", "TASK-01-01"]
        for task_id in duplicate_ids:
            task_block = TaskBlock(
                line_start=10,
                line_end=11,
                raw_content=f"- {task_id}: Test task",
                task_id=task_id,
                task_text="Test task",
            )
            document.children.append(task_block)

        rule = DuplicateTaskIDRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert not result.is_valid
        assert len(result.errors) == 2  # Two occurrences of TASK-01-01
        assert all("Duplicate TASK-ID" in error.message for error in result.errors)
