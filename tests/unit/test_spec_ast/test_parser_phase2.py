"""Unit tests for Phase 2 parser functionality (section classification and ID extraction)."""

from wassden.language_types import Language
from wassden.lib.spec_ast.blocks import BlockType, RequirementBlock, SectionBlock, TaskBlock
from wassden.lib.spec_ast.parser import SpecMarkdownParser


class TestSectionClassification:
    """Tests for section classification in parser."""

    def test_parse_functional_requirements_section_japanese(self) -> None:
        """Test parsing Japanese functional requirements section."""
        markdown = """## 機能要件

- REQ-01: システムは入力を検証すること
- REQ-02: システムは結果を表示すること
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert isinstance(section, SectionBlock)
        assert section.title == "機能要件"
        assert section.normalized_title == "functional_requirements"

    def test_parse_functional_requirements_section_english(self) -> None:
        """Test parsing English functional requirements section."""
        markdown = """## Functional Requirements

- REQ-01: The system shall validate input
- REQ-02: The system shall display results
"""
        parser = SpecMarkdownParser(Language.ENGLISH)
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert isinstance(section, SectionBlock)
        assert section.title == "Functional Requirements"
        assert section.normalized_title == "functional_requirements"

    def test_parse_task_list_section_japanese(self) -> None:
        """Test parsing Japanese task list section."""
        markdown = """## タスク一覧

- TASK-01-01: ログイン機能を実装
- TASK-01-02: テストを作成
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert isinstance(section, SectionBlock)
        assert section.title == "タスク一覧"
        assert section.normalized_title == "task_list"

    def test_parse_task_list_section_english(self) -> None:
        """Test parsing English task list section."""
        markdown = """## Task List

- TASK-01-01: Implement login feature
- TASK-01-02: Write tests
"""
        parser = SpecMarkdownParser(Language.ENGLISH)
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert isinstance(section, SectionBlock)
        assert section.title == "Task List"
        assert section.normalized_title == "task_list"


class TestRequirementExtraction:
    """Tests for requirement extraction with IDs."""

    def test_extract_requirements_with_ids(self) -> None:
        """Test extracting requirements with REQ-IDs."""
        markdown = """## 機能要件

- REQ-01: システムは入力を検証すること
- REQ-02: システムはエラーを表示すること
- REQ-03: システムは結果を保存すること
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert len(section.children) == 3

        req1 = section.children[0]
        assert isinstance(req1, RequirementBlock)
        assert req1.req_id == "REQ-01"
        assert req1.req_text == "システムは入力を検証すること"
        assert req1.req_type == "REQ"

        req2 = section.children[1]
        assert isinstance(req2, RequirementBlock)
        assert req2.req_id == "REQ-02"

        req3 = section.children[2]
        assert isinstance(req3, RequirementBlock)
        assert req3.req_id == "REQ-03"

    def test_extract_nfr_requirements(self) -> None:
        """Test extracting non-functional requirements."""
        markdown = """## 非機能要件

- NFR-01: Response time shall be < 100ms
- NFR-02: System shall support 1000 concurrent users
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert section.normalized_title == "non_functional_requirements"

        nfr1 = section.children[0]
        assert isinstance(nfr1, RequirementBlock)
        assert nfr1.req_id == "NFR-01"
        assert nfr1.req_type == "NFR"

        nfr2 = section.children[1]
        assert isinstance(nfr2, RequirementBlock)
        assert nfr2.req_id == "NFR-02"
        assert nfr2.req_type == "NFR"

    def test_extract_requirements_without_ids(self) -> None:
        """Test extracting requirements without explicit IDs."""
        markdown = """## Functional Requirements

- The system shall validate user input
- The system shall log all actions
"""
        parser = SpecMarkdownParser(Language.ENGLISH)
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert len(section.children) == 2

        req1 = section.children[0]
        assert isinstance(req1, RequirementBlock)
        assert req1.req_id is None
        assert "validate user input" in req1.req_text
        assert req1.req_type == "REQ"

    def test_skip_acceptance_criteria(self) -> None:
        """Test that acceptance criteria are skipped."""
        markdown = """## 機能要件

- REQ-01: システムは入力を検証すること
- 受け入れ観点: 正常な入力でエラーが出ないこと
- REQ-02: システムは結果を表示すること
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        section = doc.children[0]
        # Should only have 2 requirements, acceptance criteria skipped
        assert len(section.children) == 2

        req1 = section.children[0]
        assert isinstance(req1, RequirementBlock)
        assert req1.req_id == "REQ-01"

        req2 = section.children[1]
        assert isinstance(req2, RequirementBlock)
        assert req2.req_id == "REQ-02"


class TestTaskExtraction:
    """Tests for task extraction with IDs and references."""

    def test_extract_tasks_with_ids(self) -> None:
        """Test extracting tasks with TASK-IDs."""
        markdown = """## タスク一覧

- TASK-01-01: ログイン機能を実装
- TASK-01-02: ユニットテストを作成
- TASK-02-01: API設計を作成
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert len(section.children) == 3

        task1 = section.children[0]
        assert isinstance(task1, TaskBlock)
        assert task1.task_id == "TASK-01-01"
        assert task1.task_text == "ログイン機能を実装"

        task2 = section.children[1]
        assert isinstance(task2, TaskBlock)
        assert task2.task_id == "TASK-01-02"

        task3 = section.children[2]
        assert isinstance(task3, TaskBlock)
        assert task3.task_id == "TASK-02-01"

    def test_extract_task_with_req_references(self) -> None:
        """Test extracting task with requirement references."""
        markdown = """## Task List

- TASK-01-01: Implement REQ-01 and REQ-02 features
"""
        parser = SpecMarkdownParser(Language.ENGLISH)
        doc = parser.parse(markdown)

        section = doc.children[0]
        task = section.children[0]
        assert isinstance(task, TaskBlock)
        assert task.task_id == "TASK-01-01"
        assert "REQ-01" in task.req_refs
        assert "REQ-02" in task.req_refs

    def test_extract_task_with_design_references(self) -> None:
        """Test extracting task with design component references."""
        markdown = """## Task List

- TASK-01-01: Implement DC-03 authentication module using DC-05
"""
        parser = SpecMarkdownParser(Language.ENGLISH)
        doc = parser.parse(markdown)

        section = doc.children[0]
        task = section.children[0]
        assert isinstance(task, TaskBlock)
        assert "DC-03" in task.design_refs
        assert "DC-05" in task.design_refs

    def test_extract_task_with_dependencies(self) -> None:
        """Test extracting task with dependencies."""
        markdown = """## Task List

- TASK-01-01: Setup database
- TASK-01-02: Create models, depends on TASK-01-01
- TASK-01-03: Write tests, requires TASK-01-02
"""
        parser = SpecMarkdownParser(Language.ENGLISH)
        doc = parser.parse(markdown)

        section = doc.children[0]

        task1 = section.children[0]
        assert isinstance(task1, TaskBlock)
        assert len(task1.dependencies) == 0

        task2 = section.children[1]
        assert isinstance(task2, TaskBlock)
        assert "TASK-01-01" in task2.dependencies

        task3 = section.children[2]
        assert isinstance(task3, TaskBlock)
        assert "TASK-01-02" in task3.dependencies

    def test_extract_task_without_id(self) -> None:
        """Test extracting task without explicit ID."""
        markdown = """## Task List

- Implement login feature
- Write unit tests
"""
        parser = SpecMarkdownParser(Language.ENGLISH)
        doc = parser.parse(markdown)

        section = doc.children[0]
        assert len(section.children) == 2

        task1 = section.children[0]
        assert isinstance(task1, TaskBlock)
        assert task1.task_id is None
        assert "Implement login feature" in task1.task_text


class TestComplexDocument:
    """Tests for parsing complex documents with multiple sections."""

    def test_parse_requirements_document_japanese(self) -> None:
        """Test parsing complete Japanese requirements document."""
        markdown = """## 概要

プロジェクトの概要です。

## 用語集

- API: Application Programming Interface

## 機能要件

- REQ-01: システムはユーザー認証を行うこと
- REQ-02: システムはデータを保存すること
- REQ-03: システムはログを記録すること

## 非機能要件

- NFR-01: レスポンスタイムは100ms以下であること
- NFR-02: 同時接続数は1000まで対応すること
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        assert len(doc.children) == 4

        # Overview section (概要 in Japanese maps to "overview")
        overview = doc.children[0]
        assert isinstance(overview, SectionBlock)
        assert overview.normalized_title == "overview"

        # Glossary section
        glossary = doc.children[1]
        assert isinstance(glossary, SectionBlock)
        assert glossary.normalized_title == "glossary"

        # Functional requirements section
        func_req = doc.children[2]
        assert isinstance(func_req, SectionBlock)
        assert func_req.normalized_title == "functional_requirements"
        assert len(func_req.children) == 3
        assert all(isinstance(child, RequirementBlock) for child in func_req.children)

        # Non-functional requirements section
        nfr = doc.children[3]
        assert isinstance(nfr, SectionBlock)
        assert nfr.normalized_title == "non_functional_requirements"
        assert len(nfr.children) == 2
        assert all(isinstance(child, RequirementBlock) for child in nfr.children)

    def test_parse_tasks_document_english(self) -> None:
        """Test parsing complete English tasks document."""
        markdown = """## Overview

This document describes implementation tasks.

## Task List

- TASK-01-01: Setup project structure
- TASK-01-02: Implement REQ-01 authentication, depends on TASK-01-01
- TASK-02-01: Write tests for DC-03 module
- TASK-03-01: Deploy to staging, requires TASK-01-02 and TASK-02-01

## Dependencies

Dependency graph visualization.
"""
        parser = SpecMarkdownParser(Language.ENGLISH)
        doc = parser.parse(markdown)

        assert len(doc.children) == 3

        # Overview
        overview = doc.children[0]
        assert isinstance(overview, SectionBlock)
        assert overview.normalized_title == "overview"

        # Task List
        task_list = doc.children[1]
        assert isinstance(task_list, SectionBlock)
        assert task_list.normalized_title == "task_list"
        assert len(task_list.children) == 4

        # Check first task
        task1 = task_list.children[0]
        assert isinstance(task1, TaskBlock)
        assert task1.task_id == "TASK-01-01"
        assert len(task1.dependencies) == 0

        # Check second task with dependencies and req refs
        task2 = task_list.children[1]
        assert isinstance(task2, TaskBlock)
        assert task2.task_id == "TASK-01-02"
        assert "TASK-01-01" in task2.dependencies
        assert "REQ-01" in task2.req_refs

        # Check third task with design refs
        task3 = task_list.children[2]
        assert isinstance(task3, TaskBlock)
        assert task3.task_id == "TASK-02-01"
        assert "DC-03" in task3.design_refs

        # Dependencies section
        deps = doc.children[2]
        assert isinstance(deps, SectionBlock)
        assert deps.normalized_title == "dependencies"


class TestBlockTypeFiltering:
    """Tests for filtering blocks by type."""

    def test_get_all_requirements_from_document(self) -> None:
        """Test getting all requirements from parsed document."""
        markdown = """## 機能要件

- REQ-01: 要件1
- REQ-02: 要件2

## 非機能要件

- NFR-01: 非機能要件1
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        # Get all requirements
        requirements = doc.get_blocks_by_type(BlockType.REQUIREMENT)
        assert len(requirements) == 3

        req_ids = [r.req_id for r in requirements if isinstance(r, RequirementBlock)]
        assert "REQ-01" in req_ids
        assert "REQ-02" in req_ids
        assert "NFR-01" in req_ids

    def test_get_all_tasks_from_document(self) -> None:
        """Test getting all tasks from parsed document."""
        markdown = """## タスク一覧

- TASK-01-01: タスク1
- TASK-01-02: タスク2
- TASK-02-01: タスク3
"""
        parser = SpecMarkdownParser(Language.JAPANESE)
        doc = parser.parse(markdown)

        # Get all tasks
        tasks = doc.get_blocks_by_type(BlockType.TASK)
        assert len(tasks) == 3

        task_ids = [t.task_id for t in tasks if isinstance(t, TaskBlock)]
        assert "TASK-01-01" in task_ids
        assert "TASK-01-02" in task_ids
        assert "TASK-02-01" in task_ids
