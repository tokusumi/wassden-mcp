"""Tests for structure validation rules."""

from wassden.lib.spec_ast.blocks import DocumentBlock, SectionBlock
from wassden.lib.spec_ast.section_patterns import SectionType
from wassden.lib.spec_ast.structure_rules import DesignStructureRule, RequirementsStructureRule, TasksStructureRule
from wassden.lib.spec_ast.validation_rules import ValidationContext


class TestRequirementsStructureRule:
    """Tests for RequirementsStructureRule."""

    def test_rule_properties(self):
        """Test rule properties."""
        rule = RequirementsStructureRule()

        assert rule.rule_id == "STRUCT-REQ-001"
        assert rule.rule_name == "Requirements Structure"
        assert "requirements document" in rule.description.lower()

    def test_valid_requirements_structure(self):
        """Test validation with all required sections."""
        # Create document with all required sections
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")

        # Add all required sections
        required_sections = [
            SectionType.SUMMARY,
            SectionType.GLOSSARY,
            SectionType.SCOPE,
            SectionType.CONSTRAINTS,
            SectionType.NON_FUNCTIONAL_REQUIREMENTS,
            SectionType.KPI,
            SectionType.FUNCTIONAL_REQUIREMENTS,
            SectionType.TESTING_REQUIREMENTS,
        ]

        for section_type in required_sections:
            section = SectionBlock(
                line_start=10,
                line_end=20,
                raw_content=f"## {section_type.value}",
                section_type=section_type,
                normalized_title=section_type.value,
                level=2,
            )
            document.children.append(section)

        rule = RequirementsStructureRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_required_sections(self):
        """Test validation with missing required sections."""
        # Create document with only some sections
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Requirements")

        # Add only Summary section
        section = SectionBlock(
            line_start=10,
            line_end=20,
            raw_content="## Summary",
            section_type=SectionType.SUMMARY,
            normalized_title="summary",
            level=2,
        )
        document.children.append(section)

        rule = RequirementsStructureRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert not result.is_valid
        assert len(result.errors) == 7  # Missing 7 out of 8 required sections
        assert any("glossary" in error.message.lower() for error in result.errors)
        assert any("scope" in error.message.lower() for error in result.errors)


class TestDesignStructureRule:
    """Tests for DesignStructureRule."""

    def test_rule_properties(self):
        """Test rule properties."""
        rule = DesignStructureRule()

        assert rule.rule_id == "STRUCT-DESIGN-001"
        assert rule.rule_name == "Design Structure"
        assert "design document" in rule.description.lower()

    def test_valid_design_structure(self):
        """Test validation with all required sections."""
        # Create document with all required sections
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Design")

        # Add all required sections
        required_sections = [
            SectionType.ARCHITECTURE,
            SectionType.COMPONENT_DESIGN,
            SectionType.DATA,
            SectionType.API,
            SectionType.NON_FUNCTIONAL,
            SectionType.TEST,
        ]

        for section_type in required_sections:
            section = SectionBlock(
                line_start=10,
                line_end=20,
                raw_content=f"## {section_type.value}",
                section_type=section_type,
                normalized_title=section_type.value,
                level=2,
            )
            document.children.append(section)

        rule = DesignStructureRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_design_sections(self):
        """Test validation with missing required sections."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Design")

        rule = DesignStructureRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert not result.is_valid
        assert len(result.errors) == 6  # All 6 required sections missing


class TestTasksStructureRule:
    """Tests for TasksStructureRule."""

    def test_rule_properties(self):
        """Test rule properties."""
        rule = TasksStructureRule()

        assert rule.rule_id == "STRUCT-TASKS-001"
        assert rule.rule_name == "Tasks Structure"
        assert "tasks document" in rule.description.lower()

    def test_valid_tasks_structure(self):
        """Test validation with all required sections."""
        # Create document with all required sections
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Tasks")

        # Add all required sections
        required_sections = [
            SectionType.OVERVIEW,
            SectionType.TASK_LIST,
            SectionType.DEPENDENCIES,
            SectionType.MILESTONES,
        ]

        for section_type in required_sections:
            section = SectionBlock(
                line_start=10,
                line_end=20,
                raw_content=f"## {section_type.value}",
                section_type=section_type,
                normalized_title=section_type.value,
                level=2,
            )
            document.children.append(section)

        rule = TasksStructureRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_tasks_sections(self):
        """Test validation with missing required sections."""
        document = DocumentBlock(line_start=1, line_end=100, raw_content="# Tasks")

        # Add only Overview
        section = SectionBlock(
            line_start=10,
            line_end=20,
            raw_content="## Overview",
            section_type=SectionType.OVERVIEW,
            normalized_title="overview",
            level=2,
        )
        document.children.append(section)

        rule = TasksStructureRule()
        context = ValidationContext()
        result = rule.validate(document, context)

        assert not result.is_valid
        assert len(result.errors) == 3  # Missing 3 out of 4 required sections
