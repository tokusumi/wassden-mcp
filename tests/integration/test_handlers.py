"""Integration tests for handlers."""

import pytest

from wassden.handlers import (
    code_analysis,
    completeness,
    design,
    requirements,
    tasks,
    traceability,
)


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
async def test_validate_requirements_handler(temp_dir, sample_requirements):
    """Test requirements validation handler."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(sample_requirements)

    result = await requirements.handle_validate_requirements({"requirementsPath": str(req_path)})

    assert "content" in result
    text = result["content"][0]["text"]
    assert "✅" in text  # Should pass validation


@pytest.mark.asyncio
async def test_prompt_design_handler(temp_dir, sample_requirements):
    """Test design prompt handler."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(sample_requirements)

    result = await design.handle_prompt_design({"requirementsPath": str(req_path)})

    assert "content" in result
    text = result["content"][0]["text"]
    assert "design.md" in text
    assert "アーキテクチャ" in text


@pytest.mark.asyncio
async def test_validate_design_handler(temp_dir, sample_design, sample_requirements):
    """Test design validation handler."""
    design_path = temp_dir / "design.md"
    design_path.write_text(sample_design)
    req_path = temp_dir / "requirements.md"
    req_path.write_text(sample_requirements)

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
async def test_prompt_tasks_handler(temp_dir, sample_design, sample_requirements):
    """Test tasks prompt handler."""
    design_path = temp_dir / "design.md"
    design_path.write_text(sample_design)
    req_path = temp_dir / "requirements.md"
    req_path.write_text(sample_requirements)

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
async def test_validate_tasks_handler(temp_dir, sample_tasks):
    """Test tasks validation handler."""
    tasks_path = temp_dir / "tasks.md"
    tasks_path.write_text(sample_tasks)

    result = await tasks.handle_validate_tasks({"tasksPath": str(tasks_path)})

    assert "content" in result
    text = result["content"][0]["text"]
    assert "✅" in text  # Should pass validation


@pytest.mark.asyncio
async def test_prompt_code_handler(temp_dir, sample_requirements, sample_design, sample_tasks):
    """Test code prompt handler."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(sample_requirements)
    design_path = temp_dir / "design.md"
    design_path.write_text(sample_design)
    tasks_path = temp_dir / "tasks.md"
    tasks_path.write_text(sample_tasks)

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
async def test_get_traceability_handler(temp_dir, sample_requirements, sample_design, sample_tasks):
    """Test traceability report handler."""
    req_path = temp_dir / "requirements.md"
    req_path.write_text(sample_requirements)
    design_path = temp_dir / "design.md"
    design_path.write_text(sample_design)
    tasks_path = temp_dir / "tasks.md"
    tasks_path.write_text(sample_tasks)

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
