"""Detailed prompt generation tests matching TypeScript version granularity."""

from wassden.lib import prompts


class TestRequirementsPromptGeneration:
    """Detailed requirements prompt generation tests."""

    def test_basic_requirements_prompt_structure(self):
        """Test basic structure of requirements prompt."""
        result = prompts.generate_requirements_prompt("Test project")

        # Check for key structural elements
        assert "EARS形式" in result
        assert "requirements.md" in result
        assert "Test project" in result
        assert "specs/requirements.md" in result
        assert "以下の指示に従って" in result

    def test_requirements_prompt_with_all_parameters(self):
        """Test requirements prompt with all optional parameters."""
        result = prompts.generate_requirements_prompt(
            "Complex project", scope="Enterprise web application", constraints="Python 3.12+, FastAPI, PostgreSQL"
        )

        assert "Complex project" in result
        assert "Enterprise web application" in result
        assert "Python 3.12+, FastAPI, PostgreSQL" in result
        assert "EARS形式" in result
        assert "requirements.md" in result

    def test_requirements_prompt_scope_placeholder(self):
        """Test requirements prompt when scope is not provided."""
        result = prompts.generate_requirements_prompt("Test project")
        assert "スコープ情報を分析して記載" in result

    def test_requirements_prompt_constraints_placeholder(self):
        """Test requirements prompt when constraints are not provided."""
        result = prompts.generate_requirements_prompt("Test project")
        assert "技術的・ビジネス制約を分析して記載" in result

    def test_requirements_prompt_empty_project_description(self):
        """Test requirements prompt with empty project description."""
        result = prompts.generate_requirements_prompt("")
        assert "EARS形式" in result
        assert "requirements.md" in result
        # Should still contain structural elements even with empty description

    def test_requirements_prompt_long_description(self):
        """Test requirements prompt with very long project description."""
        long_description = "A" * 10000
        result = prompts.generate_requirements_prompt(long_description)

        assert long_description in result
        assert "EARS形式" in result
        assert "requirements.md" in result

    def test_requirements_prompt_special_characters(self):
        """Test requirements prompt with special characters."""
        special_desc = "Project with symbols: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
        result = prompts.generate_requirements_prompt(special_desc)

        assert special_desc in result
        assert "EARS形式" in result

    def test_requirements_prompt_japanese_input(self):
        """Test requirements prompt with Japanese input."""
        japanese_desc = "日本語のプロジェクト説明です。Python、FastAPI、Reactを使用します。"
        result = prompts.generate_requirements_prompt(japanese_desc)

        assert japanese_desc in result
        assert "EARS形式" in result
        assert "requirements.md" in result


class TestDesignPromptGeneration:
    """Detailed design prompt generation tests."""

    def test_basic_design_prompt_structure(self):
        """Test basic structure of design prompt."""
        requirements = "# Requirements\n- REQ-01: Test requirement"
        result = prompts.generate_design_prompt(requirements)

        assert "design.md" in result
        assert requirements in result
        assert "design.mdファイルを作成" in result

    def test_design_prompt_with_complex_requirements(self):
        """Test design prompt with complex requirements content."""
        complex_requirements = """
# Requirements Document

## 0. サマリー
複雑なシステムの要件定義

## 1. 用語集
- **API**: Application Programming Interface
- **SDD**: Spec-Driven Development

## 6. 機能要件（EARS）
- **REQ-01**: システムは、ユーザーがログインするとき、認証を行うこと
- **REQ-02**: システムは、データを保存するとき、暗号化すること
- **REQ-03**: システムは、レポートを生成するとき、PDF形式で出力すること
"""

        result = prompts.generate_design_prompt(complex_requirements)

        assert complex_requirements in result
        assert "design.md" in result
        assert "REQ-01" in result
        assert "REQ-02" in result
        assert "REQ-03" in result

    def test_design_prompt_empty_requirements(self):
        """Test design prompt with empty requirements."""
        result = prompts.generate_design_prompt("")

        assert "design.md" in result
        assert "design.mdファイルを作成" in result

    def test_design_prompt_requirements_with_special_characters(self):
        """Test design prompt with requirements containing special characters."""
        special_requirements = "Requirements with symbols: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
        result = prompts.generate_design_prompt(special_requirements)

        assert special_requirements in result
        assert "design.md" in result

    def test_design_prompt_large_requirements(self):
        """Test design prompt with very large requirements content."""
        large_requirements = "# Large Requirements\n" + "Content line\n" * 1000
        result = prompts.generate_design_prompt(large_requirements)

        assert large_requirements in result
        assert "design.md" in result


class TestTasksPromptGeneration:
    """Detailed tasks prompt generation tests."""

    def test_basic_tasks_prompt_structure(self):
        """Test basic structure of tasks prompt."""
        design = "# Design\n- Component: Test component"
        requirements = "# Requirements\n- REQ-01: Test requirement"

        result = prompts.generate_tasks_prompt(design, requirements)

        assert "tasks.md" in result
        assert "WBS" in result
        assert design in result
        assert requirements in result

    def test_tasks_prompt_with_comprehensive_inputs(self):
        """Test tasks prompt with comprehensive design and requirements."""
        comprehensive_design = """
# Design Document

## 1. アーキテクチャ概要
システムアーキテクチャの詳細 [REQ-01, REQ-02]

## 2. コンポーネント設計
- **auth-service**: 認証サービス [REQ-01]
- **data-service**: データ管理サービス [REQ-02]
- **report-service**: レポート生成サービス [REQ-03]
"""

        comprehensive_requirements = """
# Requirements Document

## 6. 機能要件（EARS）
- **REQ-01**: システムは、ユーザー認証を行うこと
- **REQ-02**: システムは、データを管理すること
- **REQ-03**: システムは、レポートを生成すること
"""

        result = prompts.generate_tasks_prompt(comprehensive_design, comprehensive_requirements)

        assert comprehensive_design in result
        assert comprehensive_requirements in result
        assert "tasks.md" in result
        assert "WBS" in result
        assert "REQ-01" in result
        assert "REQ-02" in result
        assert "REQ-03" in result

    def test_tasks_prompt_empty_inputs(self):
        """Test tasks prompt with empty design and requirements."""
        result = prompts.generate_tasks_prompt("", "")

        assert "tasks.md" in result
        assert "WBS" in result

    def test_tasks_prompt_mismatched_requirements_design(self):
        """Test tasks prompt when design and requirements don't perfectly match."""
        design = "# Design\n- Component for Feature X"
        requirements = "# Requirements\n- REQ-01: Feature Y requirement"

        result = prompts.generate_tasks_prompt(design, requirements)

        assert design in result
        assert requirements in result
        assert "tasks.md" in result
        assert "WBS" in result


class TestValidationFixPromptGeneration:
    """Detailed validation fix prompt generation tests."""

    def test_requirements_validation_fix_prompt(self):
        """Test validation fix prompt for requirements."""
        issues = ["Missing section: サマリー", "Invalid REQ-ID format: REQ-001", "Duplicate REQ-IDs found: REQ-01"]

        result = prompts.generate_validation_fix_prompt("requirements", issues)

        assert "requirements.md に修正が必要です" in result
        assert "Missing section: サマリー" in result
        assert "Invalid REQ-ID format: REQ-001" in result
        assert "Duplicate REQ-IDs found: REQ-01" in result
        assert "validate_requirements" in result

    def test_design_validation_fix_prompt(self):
        """Test validation fix prompt for design."""
        issues = ["Missing section: データモデル", "Missing REQ-ID references in section"]

        result = prompts.generate_validation_fix_prompt("design", issues)

        assert "design.md に修正が必要です" in result
        assert "Missing section: データモデル" in result
        assert "Missing REQ-ID references in section" in result

    def test_tasks_validation_fix_prompt(self):
        """Test validation fix prompt for tasks."""
        issues = ["Invalid TASK-ID format: TASK-1-01", "Duplicate TASK-IDs found: TASK-01-01"]

        result = prompts.generate_validation_fix_prompt("tasks", issues)

        assert "tasks.md に修正が必要です" in result
        assert "Invalid TASK-ID format: TASK-1-01" in result
        assert "Duplicate TASK-IDs found: TASK-01-01" in result

    def test_validation_fix_prompt_single_issue(self):
        """Test validation fix prompt with single issue."""
        issues = ["Missing section: 用語集"]

        result = prompts.generate_validation_fix_prompt("requirements", issues)

        assert "requirements.md に修正が必要です" in result
        assert "Missing section: 用語集" in result

    def test_validation_fix_prompt_many_issues(self):
        """Test validation fix prompt with many issues."""
        issues = [f"Issue {i}: Description of issue {i}" for i in range(1, 11)]

        result = prompts.generate_validation_fix_prompt("requirements", issues)

        assert "requirements.md に修正が必要です" in result
        for issue in issues:
            assert issue in result

    def test_validation_fix_prompt_empty_issues(self):
        """Test validation fix prompt with empty issues list."""
        result = prompts.generate_validation_fix_prompt("design", [])

        assert "design.md に修正が必要です" in result
        assert "検出された問題" in result


class TestImplementationPromptGeneration:
    """Detailed implementation prompt generation tests."""

    def test_basic_implementation_prompt_structure(self):
        """Test basic structure of implementation prompt."""
        requirements = "# Requirements\n- REQ-01: Test"
        design = "# Design\n- Component: Test"
        tasks = "# Tasks\n- TASK-01-01: Test task"

        result = prompts.generate_implementation_prompt(requirements, design, tasks)

        assert "段階的に実装を進めて" in result
        assert "TASK-01-01" in result
        assert requirements in result
        assert design in result
        assert tasks in result

    def test_implementation_prompt_comprehensive_inputs(self):
        """Test implementation prompt with comprehensive inputs."""
        requirements = """
# Requirements Document

## 6. 機能要件（EARS）
- **REQ-01**: システムは、ユーザー認証を行うこと
- **REQ-02**: システムは、データ管理を行うこと
- **REQ-03**: システムは、レポート生成を行うこと
"""

        design = """
# Design Document

## 1. アーキテクチャ概要
マイクロサービスアーキテクチャ [REQ-01, REQ-02, REQ-03]

## 2. コンポーネント設計
- **auth-service**: 認証マイクロサービス [REQ-01]
- **data-service**: データ管理マイクロサービス [REQ-02]
- **report-service**: レポート生成マイクロサービス [REQ-03]
"""

        tasks = """
# Tasks Document

## 2. タスク一覧
- **TASK-01-01**: 環境セットアップ
- **TASK-01-02**: 認証サービス実装 [REQ-01]
- **TASK-01-03**: データサービス実装 [REQ-02]
- **TASK-01-04**: レポートサービス実装 [REQ-03]
- **TASK-02-01**: 統合テスト
"""

        result = prompts.generate_implementation_prompt(requirements, design, tasks)

        assert requirements in result
        assert design in result
        assert tasks in result
        assert "TASK-01-01" in result
        assert "REQ-01" in result
        assert "REQ-02" in result
        assert "REQ-03" in result
        assert "段階的に実装" in result

    def test_implementation_prompt_empty_inputs(self):
        """Test implementation prompt with empty inputs."""
        result = prompts.generate_implementation_prompt("", "", "")

        assert "段階的に実装" in result
        # Should still provide basic implementation guidance

    def test_implementation_prompt_partial_inputs(self):
        """Test implementation prompt with some missing inputs."""
        requirements = "# Requirements\n- REQ-01: Test requirement"
        design = ""  # Empty design
        tasks = "# Tasks\n- TASK-01-01: Test task"

        result = prompts.generate_implementation_prompt(requirements, design, tasks)

        assert requirements in result
        assert tasks in result
        assert "TASK-01-01" in result
        assert "段階的に実装" in result


class TestCompletenessQuestionsGeneration:
    """Detailed completeness questions generation tests."""

    def test_generates_questions_for_single_missing_info(self):
        """Test generation of questions for single missing information."""
        missing_info = ["技術スタック"]

        result = prompts.generate_completeness_questions(missing_info)

        assert "特に以下の点が不明です" in result
        assert "1. 技術スタック" in result

    def test_generates_questions_for_multiple_missing_info(self):
        """Test generation of questions for multiple missing information."""
        missing_info = ["技術スタック", "ユーザー", "制約", "スコープ"]

        result = prompts.generate_completeness_questions(missing_info)

        assert "特に以下の点が不明です" in result
        assert "1. 技術スタック" in result
        assert "2. ユーザー" in result
        assert "3. 制約" in result
        assert "4. スコープ" in result

    def test_generates_questions_for_many_missing_info(self):
        """Test generation of questions for many missing information items."""
        missing_info = [
            "技術スタック",
            "ユーザー",
            "制約",
            "スコープ",
            "予算",
            "期限",
            "チーム構成",
            "インフラ",
            "セキュリティ",
            "パフォーマンス",
        ]

        result = prompts.generate_completeness_questions(missing_info)

        assert "特に以下の点が不明です" in result
        for i, info in enumerate(missing_info, 1):
            assert f"{i}. {info}" in result

    def test_generates_empty_string_for_empty_missing_info(self):
        """Test generation returns empty string for empty missing info."""
        result = prompts.generate_completeness_questions([])

        assert result == ""

    def test_generates_questions_with_special_characters(self):
        """Test generation of questions with special characters in missing info."""
        missing_info = ["技術スタック（Python/FastAPI）", "ユーザー&権限"]

        result = prompts.generate_completeness_questions(missing_info)

        assert "特に以下の点が不明です" in result
        assert "1. 技術スタック（Python/FastAPI）" in result
        assert "2. ユーザー&権限" in result


class TestTraceabilityReportFormatting:
    """Detailed traceability report formatting tests."""

    def test_formats_complete_traceability_matrix(self):
        """Test formatting of complete traceability matrix."""
        matrix = {
            "requirements": {"REQ-01", "REQ-02", "REQ-03"},
            "design_components": {"component-a", "component-b", "component-c"},
            "tasks": {"TASK-01-01", "TASK-01-02", "TASK-02-01"},
            "req_to_design": {"REQ-01": {"component-a"}, "REQ-02": {"component-b"}, "REQ-03": {"component-c"}},
        }

        result = prompts.format_traceability_report(matrix)

        assert "トレーサビリティレポート" in result
        assert "要件数: 3" in result
        assert "設計要素数: 3" in result
        assert "タスク数: 3" in result
        assert "REQ-01" in result
        assert "REQ-02" in result
        assert "REQ-03" in result
        assert "component-a" in result
        assert "component-b" in result
        assert "component-c" in result

    def test_formats_partial_traceability_matrix(self):
        """Test formatting of partial traceability matrix."""
        matrix = {
            "requirements": {"REQ-01", "REQ-02"},
            "design_components": {"component-a"},
            "tasks": set(),
            "req_to_design": {
                "REQ-01": {"component-a"},
                # REQ-02 has no design mapping
            },
        }

        result = prompts.format_traceability_report(matrix)

        assert "トレーサビリティレポート" in result
        assert "要件数: 2" in result
        assert "設計要素数: 1" in result
        assert "タスク数: 0" in result

    def test_formats_empty_traceability_matrix(self):
        """Test formatting of empty traceability matrix."""
        matrix = {"requirements": set(), "design_components": set(), "tasks": set(), "req_to_design": {}}

        result = prompts.format_traceability_report(matrix)

        assert "要件数: 0" in result
        assert "設計要素数: 0" in result
        assert "タスク数: 0" in result

    def test_formats_large_traceability_matrix(self):
        """Test formatting of large traceability matrix."""
        # Generate large matrix
        requirements = {f"REQ-{i:02d}" for i in range(1, 51)}  # 50 requirements
        design_components = {f"component-{i}" for i in range(1, 31)}  # 30 components
        tasks = {f"TASK-{i:02d}-{j:02d}" for i in range(1, 11) for j in range(1, 6)}  # 50 tasks
        req_to_design = {req: {f"component-{(i % 30) + 1}"} for i, req in enumerate(requirements)}

        matrix = {
            "requirements": requirements,
            "design_components": design_components,
            "tasks": tasks,
            "req_to_design": req_to_design,
        }

        result = prompts.format_traceability_report(matrix)

        assert "要件数: 50" in result
        assert "設計要素数: 30" in result
        assert "タスク数: 50" in result

    def test_formats_matrix_with_complex_mappings(self):
        """Test formatting of matrix with complex requirement-to-design mappings."""
        matrix = {
            "requirements": {"REQ-01", "REQ-02", "REQ-03"},
            "design_components": {"component-a", "component-b", "component-c", "component-d"},
            "tasks": {"TASK-01-01", "TASK-01-02"},
            "req_to_design": {
                "REQ-01": {"component-a", "component-b"},  # One req maps to multiple components
                "REQ-02": {"component-a"},  # Multiple reqs map to same component
                "REQ-03": {"component-a"},  # component-d has no req mapping
            },
        }

        result = prompts.format_traceability_report(matrix)

        assert "要件数: 3" in result
        assert "設計要素数: 4" in result
        assert "タスク数: 2" in result
