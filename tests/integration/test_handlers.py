"""Integration tests for handlers."""

import tempfile
from pathlib import Path

import pytest

from wassden.handlers import (
    code_analysis,
    completeness,
    design,
    requirements,
    tasks,
    traceability,
)


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
    result = await completeness.handle_check_completeness({"userInput": "Simple test project"})

    assert "content" in result
    assert len(result["content"]) > 0
    assert "text" in result["content"][0]

    # Should ask for more information
    text = result["content"][0]["text"]
    assert "技術" in text or "ユーザー" in text or "制約" in text


@pytest.mark.asyncio
async def test_prompt_requirements_handler():
    """Test requirements prompt handler."""
    result = await requirements.handle_prompt_requirements(
        {
            "projectDescription": "Test project",
            "scope": "Basic features",
            "constraints": "Python 3.12+",
        }
    )

    assert "content" in result
    assert len(result["content"]) > 0
    text = result["content"][0]["text"]
    assert "requirements.md" in text
    assert "EARS" in text


@pytest.mark.asyncio
async def test_validate_requirements_handler(temp_dir, correct_requirements):
    """Test requirements validation handler with valid content."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)

    result = await requirements.handle_validate_requirements({"requirementsPath": str(req_path)})

    assert "content" in result
    text = result["content"][0]["text"]
    assert "✅" in text  # Should pass validation


@pytest.mark.asyncio
async def test_prompt_design_handler(temp_dir, correct_requirements):
    """Test design prompt handler."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)

    result = await design.handle_prompt_design({"requirementsPath": str(req_path)})

    assert "content" in result
    text = result["content"][0]["text"]
    assert "design.md" in text
    assert "アーキテクチャ" in text


@pytest.mark.asyncio
async def test_validate_design_handler(temp_dir, correct_design, correct_requirements):
    """Test design validation handler with valid content."""
    design_path = temp_dir / "design.md"
    design_path.write_text(correct_design)
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)

    result = await design.handle_validate_design(
        {
            "designPath": str(design_path),
            "requirementsPath": str(req_path),
        }
    )

    assert "content" in result
    text = result["content"][0]["text"]
    assert "✅" in text  # Should pass validation


@pytest.mark.asyncio
async def test_prompt_tasks_handler(temp_dir, correct_design, correct_requirements):
    """Test tasks prompt handler."""
    design_path = temp_dir / "design.md"
    design_path.write_text(correct_design)
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)

    result = await tasks.handle_prompt_tasks(
        {
            "designPath": str(design_path),
            "requirementsPath": str(req_path),
        }
    )

    assert "content" in result
    text = result["content"][0]["text"]
    assert "tasks.md" in text
    assert "WBS" in text


@pytest.mark.asyncio
async def test_validate_tasks_handler_with_traceability_issues(temp_dir, incorrect_tasks):
    """Test tasks validation handler - should detect missing traceability (failure case)."""
    tasks_path = temp_dir / "tasks.md"
    tasks_path.write_text(incorrect_tasks)

    result = await tasks.handle_validate_tasks({"tasksPath": str(tasks_path)})

    assert "content" in result
    text = result["content"][0]["text"]

    # Without requirements/design files, validation should warn about missing references
    # This tests that the handler correctly identifies traceability issues
    assert "⚠️" in text  # Should show warnings about missing references
    assert "修正が必要" in text  # Should indicate fixes are needed
    assert "Requirements not referenced" in text  # Should detect missing REQ references


@pytest.mark.asyncio
async def test_validate_tasks_handler_success_case(temp_dir, correct_requirements, correct_design, correct_tasks):
    """Test tasks validation handler - should pass with complete traceability (success case)."""
    # Create files using correct fixtures
    req_path = temp_dir / "requirements.md"
    design_path = temp_dir / "design.md"
    tasks_path = temp_dir / "tasks.md"

    req_path.write_text(correct_requirements)
    design_path.write_text(correct_design)
    tasks_path.write_text(correct_tasks)

    # Test with all files present for complete traceability validation
    result = await tasks.handle_validate_tasks(
        {"tasksPath": str(tasks_path), "requirementsPath": str(req_path), "designPath": str(design_path)}
    )

    assert "content" in result
    text = result["content"][0]["text"]

    # Should pass validation with 100% traceability
    assert "✅" in text  # Should show success
    assert "検証に成功" in text  # Should indicate success
    assert "タスク数: 6" in text  # Should detect the 6 tasks in correct_tasks
    assert "実装フェーズに進むことができます" in text  # Should allow proceeding to implementation


@pytest.mark.asyncio
async def test_prompt_code_handler(temp_dir, correct_requirements, correct_design, correct_tasks):
    """Test code prompt handler."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(correct_requirements)
    design_path = temp_dir / "design.md"
    design_path.write_text(correct_design)
    tasks_path = temp_dir / "tasks.md"
    tasks_path.write_text(correct_tasks)

    result = await code_analysis.handle_prompt_code(
        {
            "requirementsPath": str(req_path),
            "designPath": str(design_path),
            "tasksPath": str(tasks_path),
        }
    )

    assert "content" in result
    text = result["content"][0]["text"]
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

    result = await code_analysis.handle_generate_review_prompt(
        {
            "taskId": "TASK-01-01",
            "requirementsPath": str(req_path),
            "designPath": str(design_path),
            "tasksPath": str(tasks_path),
        }
    )

    assert "content" in result
    text = result["content"][0]["text"]

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
    result = await code_analysis.handle_generate_review_prompt({})

    assert "content" in result
    text = result["content"][0]["text"]
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
        result = await code_analysis.handle_generate_review_prompt(
            {
                "taskId": "TASK-99-99",  # Non-existent task
                "tasksPath": tasks_path,
                "requirementsPath": req_path,
                "designPath": design_path,
            }
        )

        assert "content" in result
        text = result["content"][0]["text"]
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

    result = await traceability.handle_get_traceability(
        {
            "requirementsPath": str(req_path),
            "designPath": str(design_path),
            "tasksPath": str(tasks_path),
        }
    )

    assert "content" in result
    text = result["content"][0]["text"]
    assert "トレーサビリティレポート" in text
    assert "REQ-01" in text
    assert "REQ-02" in text


@pytest.mark.asyncio
async def test_analyze_changes_handler():
    """Test change analysis handler."""
    result = await traceability.handle_analyze_changes(
        {
            "changedFile": "specs/requirements.md",
            "changeDescription": "Added REQ-03 for new feature",
        }
    )

    assert "content" in result
    text = result["content"][0]["text"]
    assert "変更影響分析" in text
    assert "REQ-03" in text


@pytest.mark.asyncio
async def test_validate_requirements_handler_failure_case(temp_dir, incorrect_requirements):
    """Test requirements validation handler with invalid content (failure case)."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(incorrect_requirements)

    result = await requirements.handle_validate_requirements({"requirementsPath": str(req_path)})

    assert "content" in result
    text = result["content"][0]["text"]
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

    result = await design.handle_validate_design(
        {
            "designPath": str(design_path),
            "requirementsPath": str(req_path),
        }
    )

    assert "content" in result
    text = result["content"][0]["text"]
    assert "⚠️" in text or "修正が必要" in text  # Should show validation errors
    assert "REQ-02" in text  # Should detect missing REQ-02 reference
