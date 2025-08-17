"""Unit tests for prompts module."""

from wassden.lib import prompts


def test_generate_requirements_prompt_basic():
    """Test basic requirements prompt generation."""
    result = prompts.generate_requirements_prompt("Test project")

    assert "EARS形式" in result
    assert "requirements.md" in result
    assert "Test project" in result
    assert "specs/requirements.md" in result


def test_generate_requirements_prompt_with_scope_and_constraints():
    """Test requirements prompt with scope and constraints."""
    result = prompts.generate_requirements_prompt(
        "Test project", scope="Web application only", constraints="Python 3.12+"
    )

    assert "Test project" in result
    assert "Web application only" in result
    assert "Python 3.12+" in result


def test_generate_requirements_prompt_no_scope():
    """Test requirements prompt without scope."""
    result = prompts.generate_requirements_prompt("Test project")

    assert "スコープ情報を分析して記載" in result


def test_generate_requirements_prompt_no_constraints():
    """Test requirements prompt without constraints."""
    result = prompts.generate_requirements_prompt("Test project")

    assert "技術的・ビジネス制約を分析して記載" in result


def test_generate_design_prompt():
    """Test design prompt generation."""
    requirements = "# Requirements\n- REQ-01: Test requirement"
    result = prompts.generate_design_prompt(requirements)

    assert "design.md" in result
    assert "設計書の構造テンプレート" in result
    assert requirements in result


def test_generate_tasks_prompt():
    """Test tasks prompt generation."""
    design = "# Design\n- Component: Test component"
    requirements = "# Requirements\n- REQ-01: Test requirement"

    result = prompts.generate_tasks_prompt(design, requirements)

    assert "tasks.md" in result
    assert "WBS" in result
    assert design in result
    assert requirements in result


def test_generate_validation_fix_prompt():
    """Test validation fix prompt generation."""
    issues = ["Missing section: Summary", "Invalid REQ-ID format: REQ-001"]

    result = prompts.generate_validation_fix_prompt("requirements", issues)

    assert "requirements.md に修正が必要です" in result
    assert "Missing section: Summary" in result
    assert "Invalid REQ-ID format: REQ-001" in result
    assert "validate_requirements" in result


def test_generate_validation_fix_prompt_empty_issues():
    """Test validation fix prompt with empty issues."""
    result = prompts.generate_validation_fix_prompt("design", [])

    assert "design.md に修正が必要です" in result
    assert "検出された問題" in result


def test_generate_implementation_prompt():
    """Test implementation prompt generation."""
    requirements = "# Requirements\n- REQ-01: Test"
    design = "# Design\n- Component: Test"
    tasks = "# Tasks\n- TASK-01-01: Test task"

    result = prompts.generate_implementation_prompt(requirements, design, tasks)

    assert "段階的に実装を進めて" in result
    assert "TASK-01-01" in result
    assert requirements in result
    assert design in result
    assert tasks in result


def test_generate_completeness_questions():
    """Test completeness questions generation."""
    missing_info = ["技術スタック", "ユーザー", "制約"]

    result = prompts.generate_completeness_questions(missing_info)

    assert "特に以下の点が不明です" in result
    assert "1. 技術スタック" in result
    assert "2. ユーザー" in result
    assert "3. 制約" in result


def test_generate_completeness_questions_empty():
    """Test completeness questions with empty list."""
    result = prompts.generate_completeness_questions([])

    assert result == ""


def test_format_traceability_report():
    """Test traceability report formatting."""
    matrix = {
        "requirements": {"REQ-01", "REQ-02"},
        "design_components": {"component-a", "component-b"},
        "tasks": {"TASK-01-01", "TASK-01-02"},
        "req_to_design": {"REQ-01": {"component-a"}, "REQ-02": {"component-b"}},
    }

    result = prompts.format_traceability_report(matrix)

    assert "トレーサビリティレポート" in result
    assert "要件数: 2" in result
    assert "設計要素数: 2" in result
    assert "タスク数: 2" in result
    assert "REQ-01" in result
    assert "component-a" in result


def test_format_traceability_report_empty():
    """Test traceability report with empty matrix."""
    matrix = {"requirements": set(), "design_components": set(), "tasks": set(), "req_to_design": {}}

    result = prompts.format_traceability_report(matrix)

    assert "要件数: 0" in result
    assert "設計要素数: 0" in result
    assert "タスク数: 0" in result


def test_all_prompts_contain_japanese():
    """Test that all prompts contain proper Japanese text."""
    # Test requirements prompt
    req_prompt = prompts.generate_requirements_prompt("Test")
    assert "以下の指示に従って" in req_prompt

    # Test design prompt
    design_prompt = prompts.generate_design_prompt("Requirements")
    assert "design.mdファイルを作成" in design_prompt

    # Test tasks prompt
    tasks_prompt = prompts.generate_tasks_prompt("Design", "Requirements")
    assert "WBS形式" in tasks_prompt

    # Test implementation prompt
    impl_prompt = prompts.generate_implementation_prompt("Req", "Design", "Tasks")
    assert "段階的に実装" in impl_prompt


def test_prompt_structure_consistency():
    """Test that all prompts follow consistent structure."""
    prompts_to_test = [
        prompts.generate_requirements_prompt("Test"),
        prompts.generate_design_prompt("Requirements"),
        prompts.generate_tasks_prompt("Design", "Requirements"),
        prompts.generate_implementation_prompt("Req", "Design", "Tasks"),
    ]

    for prompt in prompts_to_test:
        # Each prompt should have sections marked with ##
        assert "##" in prompt
        # Each should mention file creation or implementation
        assert "作成" in prompt or "生成" in prompt or "実装" in prompt
