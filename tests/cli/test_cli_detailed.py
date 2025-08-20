"""Detailed CLI tests matching TypeScript version granularity."""

import re
import shutil
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from wassden.cli import app

# Constants for CLI exit codes
CLI_USAGE_ERROR_CODE = 2


class TestCLIBasicFunctionality:
    """Detailed CLI basic functionality tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.temp_dir)

    def test_app_help_output_structure(self):
        """Test CLI help output contains required structure."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "wassden - MCP-based Spec-Driven Development toolkit" in result.output
        assert "Usage:" in result.output
        # Typer uses rich formatting with box characters
        assert "Options:" in result.output or "╭─" in result.output
        # Typer uses rich formatting with box characters for commands section
        assert "Commands:" in result.output or "╭─" in result.output

    def test_app_help_contains_all_commands(self):
        """Test CLI help contains all expected commands."""
        result = self.runner.invoke(app, ["--help"])

        expected_commands = [
            "check-completeness",
            "prompt-requirements",
            "validate-requirements",
            "prompt-design",
            "validate-design",
            "prompt-tasks",
            "validate-tasks",
            "prompt-code",
            "analyze-changes",
            "get-traceability",
            "start-mcp-server",
        ]

        for command in expected_commands:
            assert command in result.output

    def test_app_version_format(self):
        """Test CLI version output format."""
        result = self.runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        # Version should be in format X.Y.Z
        version_pattern = r"\d+\.\d+\.\d+"
        assert re.search(version_pattern, result.output)

    def test_app_invalid_command(self):
        """Test CLI with invalid command."""
        result = self.runner.invoke(app, ["invalid-command"])

        assert result.exit_code != 0
        assert "No such command" in result.output

    def test_app_no_arguments(self):
        """Test CLI with no arguments shows help."""
        result = self.runner.invoke(app, [])

        # CLI with no arguments shows usage error
        assert result.exit_code == CLI_USAGE_ERROR_CODE
        assert "Usage:" in result.output


class TestCheckCompletenessCommand:
    """Detailed check-completeness command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_check_completeness_help(self):
        """Test check-completeness help output."""
        result = self.runner.invoke(app, ["check-completeness", "--help"])

        assert result.exit_code == 0
        assert "check-completeness" in result.output
        assert "--userInput" in result.output
        assert "Usage:" in result.output

    def test_check_completeness_missing_required_arg(self):
        """Test check-completeness without required userInput."""
        result = self.runner.invoke(app, ["check-completeness"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_check_completeness_with_simple_input(self):
        """Test check-completeness with simple input."""
        result = self.runner.invoke(app, ["check-completeness", "--userInput", "Simple test project"])

        assert result.exit_code == 0
        assert "Please review the following project information" in result.output

    def test_check_completeness_with_complex_input(self):
        """Test check-completeness with complex input."""
        complex_input = """
        Python FastAPI web application for task management.
        Technology: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL
        Users: Project managers and team members
        Constraints: Must be cloud-deployable, response time < 1s
        Scope: CRUD operations for tasks, user authentication, basic reporting
        """

        result = self.runner.invoke(app, ["check-completeness", "--userInput", complex_input])

        assert result.exit_code == 0
        assert "Please review the following project information" in result.output

    def test_check_completeness_with_empty_input(self):
        """Test check-completeness with empty input."""
        result = self.runner.invoke(app, ["check-completeness", "--userInput", ""])

        assert result.exit_code == 0
        # Should still provide some guidance even with empty input

    def test_check_completeness_with_special_characters(self):
        """Test check-completeness with special characters."""
        special_input = "Project with symbols: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"

        result = self.runner.invoke(app, ["check-completeness", "--userInput", special_input])

        assert result.exit_code == 0

    def test_check_completeness_with_japanese_input(self):
        """Test check-completeness with Japanese input."""
        japanese_input = "日本語のプロジェクト説明です。Python、FastAPI、Reactを使用します。"

        result = self.runner.invoke(app, ["check-completeness", "--userInput", japanese_input])

        assert result.exit_code == 0
        assert "プロジェクト情報を確認" in result.output

    def test_check_completeness_with_very_long_input(self):
        """Test check-completeness with very long input."""
        long_input = "A" * 10000  # 10KB of text

        result = self.runner.invoke(app, ["check-completeness", "--userInput", long_input])

        assert result.exit_code == 0


class TestPromptRequirementsCommand:
    """Detailed prompt-requirements command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_prompt_requirements_help(self):
        """Test prompt-requirements help output."""
        result = self.runner.invoke(app, ["prompt-requirements", "--help"])

        assert result.exit_code == 0
        assert "prompt-requirements" in result.output
        assert "--projectDescription" in result.output
        assert "--scope" in result.output
        assert "--constraints" in result.output

    def test_prompt_requirements_missing_required_arg(self):
        """Test prompt-requirements without required projectDescription."""
        result = self.runner.invoke(app, ["prompt-requirements"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_prompt_requirements_basic_usage(self):
        """Test prompt-requirements with basic usage."""
        result = self.runner.invoke(
            app, ["prompt-requirements", "--projectDescription", "Test project for CLI testing"]
        )

        assert result.exit_code == 0
        assert "requirements.md" in result.output
        assert "EARS format" in result.output
        assert "Test project for CLI testing" in result.output

    def test_prompt_requirements_with_scope(self):
        """Test prompt-requirements with scope parameter."""
        result = self.runner.invoke(
            app,
            ["prompt-requirements", "--projectDescription", "Test project", "--scope", "Web application development"],
        )

        assert result.exit_code == 0
        assert "Web application development" in result.output

    def test_prompt_requirements_with_constraints(self):
        """Test prompt-requirements with constraints parameter."""
        result = self.runner.invoke(
            app,
            [
                "prompt-requirements",
                "--projectDescription",
                "Test project",
                "--constraints",
                "Python 3.12+, FastAPI, PostgreSQL",
            ],
        )

        assert result.exit_code == 0
        assert "Python 3.12+, FastAPI, PostgreSQL" in result.output

    def test_prompt_requirements_with_all_parameters(self):
        """Test prompt-requirements with all parameters."""
        result = self.runner.invoke(
            app,
            [
                "prompt-requirements",
                "--projectDescription",
                "Comprehensive test project",
                "--scope",
                "Enterprise web application",
                "--constraints",
                "Python 3.12+, FastAPI, PostgreSQL, Docker",
            ],
        )

        assert result.exit_code == 0
        assert "Comprehensive test project" in result.output
        assert "Enterprise web application" in result.output
        assert "Python 3.12+, FastAPI, PostgreSQL, Docker" in result.output

    def test_prompt_requirements_empty_description(self):
        """Test prompt-requirements with empty description."""
        result = self.runner.invoke(app, ["prompt-requirements", "--projectDescription", ""])

        assert result.exit_code == 0
        assert "requirements.md" in result.output

    def test_prompt_requirements_special_characters(self):
        """Test prompt-requirements with special characters."""
        result = self.runner.invoke(
            app,
            [
                "prompt-requirements",
                "--projectDescription",
                "Project with symbols: !@#$%^&*()",
                "--scope",
                "Scope with symbols: <>?{}[]",
                "--constraints",
                "Constraints with symbols: |\\:;\"'",
            ],
        )

        assert result.exit_code == 0


class TestValidateRequirementsCommand:
    """Detailed validate-requirements command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.temp_dir)

    def test_validate_requirements_help(self):
        """Test validate-requirements help output."""
        result = self.runner.invoke(app, ["validate-requirements", "--help"])

        assert result.exit_code == 0
        assert "validate-requirements" in result.output
        assert "--requirementsPath" in result.output

    def test_validate_requirements_default_path(self):
        """Test validate-requirements with default path."""
        result = self.runner.invoke(app, ["validate-requirements"])

        assert result.exit_code == 0
        # Should show error message about missing file or attempt validation
        assert "エラー" in result.output or "検証" in result.output

    def test_validate_requirements_nonexistent_file(self):
        """Test validate-requirements with non-existent file."""
        result = self.runner.invoke(
            app, ["validate-requirements", "--requirementsPath", "/nonexistent/requirements.md"]
        )

        assert result.exit_code == 0  # Command succeeds but shows error message
        assert "エラー" in result.output
        assert "見つかりません" in result.output

    def test_validate_requirements_with_valid_file(self):
        """Test validate-requirements with valid file."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("""
# Requirements Document

## 0. サマリー
テストプロジェクトです。

## 1. 用語集
- **MCP**: Model Context Protocol

## 2. スコープ
### インスコープ
- 基本機能

## 3. 制約
- Python 3.12以上

## 4. 非機能要件（NFR）
- **NFR-01**: 性能要件

## 5. KPI / 受入基準
- **KPI-01**: 成功指標

## 6. 機能要件（EARS）
- **REQ-01**: システムは、入力を受け付けること
- **REQ-02**: システムは、出力を提供すること
""")

            result = self.runner.invoke(app, ["validate-requirements"])

            assert result.exit_code == 0
            assert "検証" in result.output

    def test_validate_requirements_with_invalid_file(self):
        """Test validate-requirements with invalid file."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("""
# Invalid Requirements

## Summary
Missing required sections and invalid IDs

## Functional Requirements
- **REQ-001**: Invalid ID format
- **REQ-1**: Also invalid format
""")

            result = self.runner.invoke(app, ["validate-requirements"])

            assert result.exit_code == 0
            # Should detect validation issues

    def test_validate_requirements_custom_path(self):
        """Test validate-requirements with custom path."""
        with self.runner.isolated_filesystem():
            Path("custom").mkdir(exist_ok=True)
            Path("custom/my_requirements.md").write_text("""
## 6. 機能要件（EARS）
- **REQ-01**: Test requirement
""")

            result = self.runner.invoke(
                app, ["validate-requirements", "--requirementsPath", "custom/my_requirements.md"]
            )

            assert result.exit_code == 0

    def test_validate_requirements_empty_file(self):
        """Test validate-requirements with empty file."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("")

            result = self.runner.invoke(app, ["validate-requirements"])

            assert result.exit_code == 0
            # Should handle empty file gracefully


class TestPromptDesignCommand:
    """Detailed prompt-design command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_prompt_design_help(self):
        """Test prompt-design help output."""
        result = self.runner.invoke(app, ["prompt-design", "--help"])

        assert result.exit_code == 0
        assert "prompt-design" in result.output
        assert "--requirementsPath" in result.output

    def test_prompt_design_default_path(self):
        """Test prompt-design with default path."""
        result = self.runner.invoke(app, ["prompt-design"])

        assert result.exit_code == 0
        # Should show error about missing requirements file or attempt to generate prompt
        assert "エラー" in result.output or "design.md" in result.output

    def test_prompt_design_with_valid_requirements(self):
        """Test prompt-design with valid requirements file."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("""
## 機能要件（EARS）
- **REQ-01**: Test requirement
""")

            result = self.runner.invoke(app, ["prompt-design"])

            assert result.exit_code == 0
            assert "design.md" in result.output
            assert "アーキテクチャ" in result.output

    def test_prompt_design_nonexistent_requirements(self):
        """Test prompt-design with non-existent requirements file."""
        result = self.runner.invoke(app, ["prompt-design", "--requirementsPath", "/nonexistent/requirements.md"])

        assert result.exit_code == 0
        assert "エラー" in result.output

    def test_prompt_design_custom_requirements_path(self):
        """Test prompt-design with custom requirements path."""
        with self.runner.isolated_filesystem():
            Path("custom").mkdir(exist_ok=True)
            Path("custom/my_requirements.md").write_text("""
## 機能要件（EARS）
- **REQ-01**: Custom requirement
- **REQ-02**: Another requirement
""")

            result = self.runner.invoke(app, ["prompt-design", "--requirementsPath", "custom/my_requirements.md"])

            assert result.exit_code == 0
            assert "design.md" in result.output


class TestValidateDesignCommand:
    """Detailed validate-design command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_validate_design_help(self):
        """Test validate-design help output."""
        result = self.runner.invoke(app, ["validate-design", "--help"])

        assert result.exit_code == 0
        assert "validate-design" in result.output
        assert "--designPath" in result.output
        assert "--requirementsPath" in result.output

    def test_validate_design_default_paths(self):
        """Test validate-design with default paths."""
        result = self.runner.invoke(app, ["validate-design"])

        assert result.exit_code == 0
        # Should show error about missing files or attempt validation
        assert "エラー" in result.output or "検証" in result.output

    def test_validate_design_with_valid_files(self):
        """Test validate-design with valid files."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("""
## 機能要件（EARS）
- **REQ-01**: Test requirement
""")
            Path("specs/design.md").write_text("""
## アーキテクチャ概要
Test architecture [REQ-01]

## コンポーネント設計
Test components

## データ設計
Test data

## API設計
Test API

## 非機能設計
Test NFR

## テスト戦略
Test strategy
""")

            result = self.runner.invoke(app, ["validate-design"])

            assert result.exit_code == 0
            assert "検証" in result.output

    def test_validate_design_custom_paths(self):
        """Test validate-design with custom paths."""
        with self.runner.isolated_filesystem():
            Path("custom").mkdir(exist_ok=True)
            Path("custom/my_requirements.md").write_text("## 機能要件\n- **REQ-01**: Test")
            Path("custom/my_design.md").write_text("## アーキテクチャ\nTest [REQ-01]")

            result = self.runner.invoke(
                app,
                [
                    "validate-design",
                    "--designPath",
                    "custom/my_design.md",
                    "--requirementsPath",
                    "custom/my_requirements.md",
                ],
            )

            assert result.exit_code == 0


class TestPromptTasksCommand:
    """Detailed prompt-tasks command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_prompt_tasks_help(self):
        """Test prompt-tasks help output."""
        result = self.runner.invoke(app, ["prompt-tasks", "--help"])

        assert result.exit_code == 0
        assert "prompt-tasks" in result.output
        assert "--designPath" in result.output
        assert "--requirementsPath" in result.output

    def test_prompt_tasks_default_paths(self):
        """Test prompt-tasks with default paths."""
        result = self.runner.invoke(app, ["prompt-tasks"])

        assert result.exit_code == 0
        # Should show error about missing files or attempt to generate prompt
        assert "エラー" in result.output or "tasks.md" in result.output

    def test_prompt_tasks_with_valid_files(self):
        """Test prompt-tasks with valid files."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("## 機能要件\n- **REQ-01**: Test")
            Path("specs/design.md").write_text("## コンポーネント設計\n- **component**: Test")

            result = self.runner.invoke(app, ["prompt-tasks"])

            assert result.exit_code == 0
            assert "tasks.md" in result.output
            assert "WBS" in result.output


class TestValidateTasksCommand:
    """Detailed validate-tasks command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_validate_tasks_help(self):
        """Test validate-tasks help output."""
        result = self.runner.invoke(app, ["validate-tasks", "--help"])

        assert result.exit_code == 0
        assert "validate-tasks" in result.output
        assert "--tasksPath" in result.output

    def test_validate_tasks_default_path(self):
        """Test validate-tasks with default path."""
        result = self.runner.invoke(app, ["validate-tasks"])

        assert result.exit_code == 0
        assert "エラー" in result.output or "検証" in result.output

    def test_validate_tasks_with_valid_file(self):
        """Test validate-tasks with valid file."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/tasks.md").write_text("""
## 概要
Test overview

## タスク一覧
- **TASK-01-01**: Test task

## 依存関係
Dependencies

## マイルストーン
Milestones
""")

            result = self.runner.invoke(app, ["validate-tasks"])

            assert result.exit_code == 0
            assert "検証" in result.output


class TestPromptCodeCommand:
    """Detailed prompt-code command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_prompt_code_help(self):
        """Test prompt-code help output."""
        result = self.runner.invoke(app, ["prompt-code", "--help"])

        assert result.exit_code == 0
        assert "prompt-code" in result.output
        assert "--tasksPath" in result.output
        assert "--requirementsPath" in result.output
        assert "--designPath" in result.output

    def test_prompt_code_default_paths(self):
        """Test prompt-code with default paths."""
        result = self.runner.invoke(app, ["prompt-code"])

        assert result.exit_code == 0
        assert "エラー" in result.output or "実装" in result.output

    def test_prompt_code_with_valid_files(self):
        """Test prompt-code with valid files."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("# Requirements\n- **REQ-01**: Test")
            Path("specs/design.md").write_text("# Design\n- Component: Test")
            Path("specs/tasks.md").write_text("# Tasks\n- **TASK-01-01**: Test")

            result = self.runner.invoke(app, ["prompt-code"])

            assert result.exit_code == 0
            assert "実装" in result.output
            assert "TASK-01-01" in result.output


class TestAnalyzeChangesCommand:
    """Detailed analyze-changes command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_analyze_changes_help(self):
        """Test analyze-changes help output."""
        result = self.runner.invoke(app, ["analyze-changes", "--help"])

        assert result.exit_code == 0
        assert "analyze-changes" in result.output
        assert "--changedFile" in result.output
        assert "--changeDescription" in result.output

    def test_analyze_changes_missing_args(self):
        """Test analyze-changes without required arguments."""
        result = self.runner.invoke(app, ["analyze-changes"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_analyze_changes_basic_usage(self):
        """Test analyze-changes with basic usage."""
        result = self.runner.invoke(
            app,
            [
                "analyze-changes",
                "--changedFile",
                "specs/requirements.md",
                "--changeDescription",
                "Added REQ-03 for new feature",
            ],
        )

        assert result.exit_code == 0
        assert "変更影響分析" in result.output
        assert "REQ-03" in result.output

    def test_analyze_changes_empty_description(self):
        """Test analyze-changes with empty description."""
        result = self.runner.invoke(
            app, ["analyze-changes", "--changedFile", "specs/requirements.md", "--changeDescription", ""]
        )

        assert result.exit_code == 0
        assert "変更影響分析" in result.output

    def test_analyze_changes_complex_description(self):
        """Test analyze-changes with complex description."""
        complex_description = """
        Added new requirements REQ-05, REQ-06, and REQ-07 for user management.
        Modified existing REQ-02 to include additional validation.
        Removed deprecated REQ-04 that was no longer needed.
        """

        result = self.runner.invoke(
            app,
            ["analyze-changes", "--changedFile", "specs/requirements.md", "--changeDescription", complex_description],
        )

        assert result.exit_code == 0
        assert "変更影響分析" in result.output


class TestGetTraceabilityCommand:
    """Detailed get-traceability command tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_get_traceability_help(self):
        """Test get-traceability help output."""
        result = self.runner.invoke(app, ["get-traceability", "--help"])

        assert result.exit_code == 0
        assert "get-traceability" in result.output
        assert "--requirementsPath" in result.output
        assert "--designPath" in result.output
        assert "--tasksPath" in result.output

    def test_get_traceability_default_paths(self):
        """Test get-traceability with default paths."""
        result = self.runner.invoke(app, ["get-traceability"])

        assert result.exit_code == 0
        assert "トレーサビリティレポート" in result.output

    def test_get_traceability_with_files(self):
        """Test get-traceability with existing files."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("## 機能要件\n- **REQ-01**: Test")
            Path("specs/design.md").write_text("## アーキテクチャ\n[REQ-01]")
            Path("specs/tasks.md").write_text("## タスク一覧\n- **TASK-01-01**: Test")

            result = self.runner.invoke(app, ["get-traceability"])

            assert result.exit_code == 0
            assert "トレーサビリティレポート" in result.output


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.runner = CliRunner()

    def test_app_with_invalid_options(self):
        """Test CLI commands with invalid options."""
        result = self.runner.invoke(app, ["check-completeness", "--invalid-option", "value"])

        assert result.exit_code != 0
        assert "no such option" in result.output.lower() or "unknown option" in result.output.lower()

    def test_app_with_conflicting_options(self):
        """Test CLI commands with conflicting options."""
        # Test with command that has multiple options
        result = self.runner.invoke(app, ["start-mcp-server", "--help"])

        # Should handle gracefully (help takes precedence)
        assert "start-mcp-server" in result.output

    def test_app_commands_handle_file_errors_gracefully(self):
        """Test that CLI commands handle file errors gracefully."""
        commands_with_file_args = [
            ["validate-requirements", "--requirementsPath", "/invalid/path.md"],
            ["prompt-design", "--requirementsPath", "/invalid/path.md"],
            ["validate-design", "--designPath", "/invalid/path.md"],
            ["validate-tasks", "--tasksPath", "/invalid/path.md"],
        ]

        for command_args in commands_with_file_args:
            result = self.runner.invoke(app, command_args)

            # Commands should handle file errors gracefully and not crash
            assert result.exit_code == 0  # Should complete but show error message
            assert "エラー" in result.output

    def test_app_with_very_long_arguments(self):
        """Test CLI with very long arguments."""
        very_long_input = "A" * 100000  # 100KB of text

        result = self.runner.invoke(app, ["check-completeness", "--userInput", very_long_input])

        # Should handle long input without crashing
        assert result.exit_code == 0

    def test_app_with_unicode_arguments(self):
        """Test CLI with Unicode arguments."""
        unicode_input = "Unicode test: 日本語, 한국어, العربية, русский, français"

        result = self.runner.invoke(app, ["check-completeness", "--userInput", unicode_input])

        assert result.exit_code == 0
