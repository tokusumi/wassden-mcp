"""Integration tests for handlers."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from wassden.handlers import (
    code_analysis,
    completeness,
    design,
    requirements,
    tasks,
    traceability,
)
from wassden.types import Language, SpecDocuments


def get_correct_tasks() -> str:
    """Return correct tasks content for testing."""
    return """
## 概要
開発タスクの分解

## タスク一覧
- **TASK-01-01**: 環境構築とプロジェクト初期化
- **TASK-01-02**: データベース設計と実装
- **TASK-02-01**: API実装とテスト

## 依存関係
TASK-01-01 → TASK-01-02 → TASK-02-01

## マイルストーン
- M1: 基盤完成
"""


@pytest.mark.asyncio
async def test_check_completeness_handler():
    """Test completeness check handler."""
    result = await completeness.handle_check_completeness("Simple test project", Language.JAPANESE)

    assert result.content
    assert len(result.content) > 0
    assert result.content[0].text

    # Should ask for more information
    text = result.content[0].text
    assert "技術" in text or "ユーザー" in text or "制約" in text


@pytest.mark.asyncio
async def test_prompt_requirements_handler():
    """Test requirements prompt handler."""
    # Create a SpecDocuments instance for testing
    specs = SpecDocuments(
        requirements_path=Path("specs/requirements.md"),
        design_path=Path("specs/design.md"),
        tasks_path=Path("specs/tasks.md"),
        language=Language.JAPANESE,
    )

    result = await requirements.handle_prompt_requirements(specs, "Test project", "Basic features", "Python 3.12+")

    assert result.content
    assert len(result.content) > 0
    text = result.content[0].text
    assert "requirements.md" in text
    assert "EARS" in text


@pytest.mark.asyncio
async def test_validate_requirements_handler(temp_dir, correct_requirements):
    """Test requirements validation handler with valid content."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)

    specs = await SpecDocuments.from_paths(requirements_path=req_path, language=Language.JAPANESE)
    result = await requirements.handle_validate_requirements(specs)

    assert result.content
    text = result.content[0].text
    assert "✅" in text  # Should pass validation


@pytest.mark.asyncio
async def test_prompt_design_handler(temp_dir, correct_requirements):
    """Test design prompt handler."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)

    specs = await SpecDocuments.from_paths(requirements_path=req_path, language=Language.JAPANESE)
    result = await design.handle_prompt_design(specs)

    assert result.content
    text = result.content[0].text
    assert "design.md" in text
    assert "アーキテクチャ" in text


@pytest.mark.asyncio
async def test_validate_design_handler(temp_dir, correct_design, correct_requirements):
    """Test design validation handler with valid content."""
    design_path = temp_dir / "design.md"
    design_path.write_text(correct_design)
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)

    specs = await SpecDocuments.from_paths(
        requirements_path=req_path, design_path=design_path, language=Language.JAPANESE
    )
    result = await design.handle_validate_design(specs)

    assert result.content
    text = result.content[0].text
    assert "✅" in text  # Should pass validation


@pytest.mark.asyncio
async def test_prompt_tasks_handler(temp_dir, correct_design, correct_requirements):
    """Test tasks prompt handler."""
    design_path = temp_dir / "design.md"
    design_path.write_text(correct_design)
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)

    specs = await SpecDocuments.from_paths(
        requirements_path=req_path, design_path=design_path, language=Language.JAPANESE
    )
    result = await tasks.handle_prompt_tasks(specs)

    assert result.content
    text = result.content[0].text
    assert "tasks.md" in text
    assert "WBS" in text


@pytest.mark.asyncio
async def test_validate_tasks_handler_with_traceability_issues(temp_dir, incorrect_tasks):
    """Test tasks validation handler - should detect missing traceability (failure case)."""
    tasks_path = temp_dir / "tasks.md"
    tasks_path.write_text(incorrect_tasks)

    specs = await SpecDocuments.from_paths(tasks_path=tasks_path)
    result = await tasks.handle_validate_tasks(specs)

    assert result.content
    text = result.content[0].text

    # Without requirements/design files, validation should warn about missing references
    # This tests that the handler correctly identifies traceability issues
    assert "⚠️" in text  # Should show warnings about missing references
    assert "修正が必要" in text  # Should indicate fixes are needed
    assert "Requirements not referenced" in text  # Should detect missing REQ references


@pytest.mark.asyncio
async def test_validate_tasks_handler_success_case(temp_dir, correct_requirements, correct_design, correct_tasks):
    """Test tasks validation handler - should pass with valid documents (success case)."""
    # Create files in temp_dir for testing
    req_path = temp_dir / "requirements.md"
    design_path = temp_dir / "design.md"
    tasks_path = temp_dir / "tasks.md"

    req_path.write_text(correct_requirements)
    design_path.write_text(correct_design)
    tasks_path.write_text(correct_tasks)

    # Mock the file reading to use our temp files instead of hardcoded specs/ paths
    async def mock_read_file(path):
        path_str = str(path)
        if "requirements.md" in path_str:
            return correct_requirements
        if "design.md" in path_str:
            return correct_design
        if "tasks.md" in path_str:
            return correct_tasks
        raise FileNotFoundError(f"Mock: {path} not found")

    with patch("wassden.lib.fs_utils.read_file", side_effect=mock_read_file):
        specs = await SpecDocuments.from_paths(tasks_path=tasks_path, language=Language.JAPANESE)
        result = await tasks.handle_validate_tasks(specs)

    assert result.content
    text = result.content[0].text

    # For a success case with valid test fixtures, should pass validation
    assert "✅" in text  # Should show success
    assert "tasks.md" in text
    assert "検証に成功" in text  # Should indicate validation success


@pytest.mark.asyncio
async def test_prompt_code_handler(temp_dir, correct_requirements, correct_design, correct_tasks):
    """Test code prompt handler."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)
    design_path = temp_dir / "design.md"
    design_path.write_text(correct_design)
    tasks_path = temp_dir / "tasks.md"
    tasks_path.write_text(correct_tasks)

    specs = await SpecDocuments.from_paths(
        requirements_path=req_path, design_path=design_path, tasks_path=tasks_path, language=Language.JAPANESE
    )
    result = await code_analysis.handle_prompt_code(specs)

    assert result.content
    text = result.content[0].text
    assert "実装" in text
    assert "TASK-01-01" in text


@pytest.mark.asyncio
async def test_generate_review_prompt_handler(temp_dir, correct_requirements, correct_design, correct_tasks):
    """Test generate review prompt handler."""
    # Create spec files
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)
    design_path = temp_dir / "design.md"
    design_path.write_text(correct_design)
    tasks_path = temp_dir / "tasks.md"
    tasks_path.write_text(correct_tasks)

    specs = await SpecDocuments.from_paths(
        requirements_path=req_path, design_path=design_path, tasks_path=tasks_path, language=Language.JAPANESE
    )
    result = await code_analysis.handle_generate_review_prompt("TASK-01-01", specs)

    assert result.content
    text = result.content[0].text

    # Check basic structure
    assert "TASK-01-01" in text
    assert "実装レビュープロンプト" in text
    assert "品質ガードレール" in text
    assert "静的品質チェック" in text
    assert "合格判定基準" in text

    # Check specific sections
    assert "テストケース改竄" in text
    assert "TODO/FIXME" in text
    assert "プロジェクト品質基準の特定" in text


@pytest.mark.asyncio
async def test_generate_review_prompt_missing_task_id():
    """Test generate review prompt with missing task ID."""
    specs = await SpecDocuments.from_paths(
        requirements_path=Path("specs/requirements.md"),
        design_path=Path("specs/design.md"),
        tasks_path=Path("specs/tasks.md"),
        language=Language.JAPANESE,
    )
    result = await code_analysis.handle_generate_review_prompt("", specs)

    assert result.content
    text = result.content[0].text
    assert "taskId パラメータが必要です" in text


@pytest.mark.asyncio
async def test_generate_review_prompt_nonexistent_task():
    """Test generate review prompt with nonexistent task ID."""

    # Create temporary files with tasks content
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(get_correct_tasks())
        tasks_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Dummy requirements")
        req_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Dummy design")
        design_path = f.name

    try:
        specs = await SpecDocuments.from_paths(
            requirements_path=Path(req_path),
            design_path=Path(design_path),
            tasks_path=Path(tasks_path),
            language=Language.JAPANESE,
        )
        result = await code_analysis.handle_generate_review_prompt("TASK-99-99", specs)

        assert result.content
        text = result.content[0].text
        assert "TASK-99-99 が tasks.md で見つかりません" in text
    finally:
        Path(tasks_path).unlink()
        Path(req_path).unlink()
        Path(design_path).unlink()


@pytest.mark.asyncio
async def test_get_traceability_handler(temp_dir, correct_requirements, correct_design, correct_tasks):
    """Test traceability report handler."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)
    design_path = temp_dir / "design.md"
    design_path.write_text(correct_design)
    tasks_path = temp_dir / "tasks.md"
    tasks_path.write_text(correct_tasks)

    specs = await SpecDocuments.from_paths(
        requirements_path=req_path, design_path=design_path, tasks_path=tasks_path, language=Language.JAPANESE
    )
    result = await traceability.handle_get_traceability(specs)

    assert result.content
    text = result.content[0].text
    assert "トレーサビリティレポート" in text
    assert "REQ-01" in text
    assert "REQ-02" in text


@pytest.mark.asyncio
async def test_analyze_changes_handler():
    """Test change analysis handler."""
    result = await traceability.handle_analyze_changes(
        Path("specs/requirements.md"), "Added REQ-03 for new feature", Language.JAPANESE
    )

    assert result.content
    text = result.content[0].text
    assert "変更影響分析" in text
    assert "REQ-03" in text


@pytest.mark.asyncio
async def test_validate_requirements_handler_failure_case(temp_dir, incorrect_requirements):
    """Test requirements validation handler with invalid content (failure case)."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(incorrect_requirements)

    specs = await SpecDocuments.from_paths(requirements_path=req_path, language=Language.JAPANESE)
    result = await requirements.handle_validate_requirements(specs)

    assert result.content
    text = result.content[0].text
    assert "⚠️" in text or "修正が必要" in text  # Should show validation errors
    assert "REQ-001" in text  # Should detect invalid format
    assert "REQ-1" in text
    assert "INVALID-01" in text


@pytest.mark.asyncio
async def test_validate_design_handler_failure_case(temp_dir, incorrect_design, correct_requirements):
    """Test design validation handler with incomplete traceability (failure case)."""
    design_path = temp_dir / "design.md"
    design_path.write_text(incorrect_design)
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)

    specs = await SpecDocuments.from_paths(
        requirements_path=req_path, design_path=design_path, language=Language.JAPANESE
    )
    result = await design.handle_validate_design(specs)

    assert result.content
    text = result.content[0].text
    assert "⚠️" in text or "修正が必要" in text  # Should show validation errors
    assert "REQ-02" in text  # Should detect missing REQ-02 reference
