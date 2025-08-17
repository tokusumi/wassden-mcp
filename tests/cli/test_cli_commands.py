"""CLI command tests."""

from pathlib import Path

from click.testing import CliRunner

from wassden.cli import cli


class TestCLICommands:
    """Test CLI command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "wassden - MCP-based Spec-Driven Development toolkit" in result.output
        assert "check-completeness" in result.output
        assert "validate-requirements" in result.output

    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_check_completeness_command(self):
        """Test check_completeness command."""
        result = self.runner.invoke(cli, ["check-completeness", "--userInput", "Simple test project"])

        assert result.exit_code == 0
        assert "プロジェクト情報を確認" in result.output

    def test_check_completeness_missing_input(self):
        """Test check_completeness command without required input."""
        result = self.runner.invoke(cli, ["check-completeness"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_prompt_requirements_command(self):
        """Test prompt_requirements command."""
        result = self.runner.invoke(
            cli, ["prompt-requirements", "--projectDescription", "Test project for CLI testing"]
        )

        assert result.exit_code == 0
        assert "requirements.md" in result.output
        assert "EARS形式" in result.output
        assert "Test project for CLI testing" in result.output

    def test_prompt_requirements_with_scope_and_constraints(self):
        """Test prompt_requirements with optional parameters."""
        result = self.runner.invoke(
            cli,
            [
                "prompt-requirements",
                "--projectDescription",
                "Test project",
                "--scope",
                "Web application",
                "--constraints",
                "Python 3.12+",
            ],
        )

        assert result.exit_code == 0
        assert "Web application" in result.output
        assert "Python 3.12+" in result.output

    def test_validate_requirements_file_not_found(self):
        """Test validate_requirements with non-existent file."""
        result = self.runner.invoke(
            cli, ["validate-requirements", "--requirementsPath", "/nonexistent/requirements.md"]
        )

        assert result.exit_code == 0  # Command succeeds but shows error message
        assert "エラー" in result.output
        assert "見つかりません" in result.output

    def test_validate_requirements_default_path(self):
        """Test validate_requirements with default path."""
        result = self.runner.invoke(cli, ["validate-requirements"])

        assert result.exit_code == 0
        # Should show validation success since specs/requirements.md exists
        assert "検証に成功しました" in result.output or "エラー" in result.output

    def test_prompt_design_command(self):
        """Test prompt_design command."""
        # Create temporary requirements file
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("""
## 機能要件
- **REQ-01**: Test requirement
""")

            result = self.runner.invoke(cli, ["prompt-design"])

            assert result.exit_code == 0
            assert "design.md" in result.output
            assert "アーキテクチャ" in result.output

    def test_validate_design_command(self):
        """Test validate_design command."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("""
## 機能要件
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

            result = self.runner.invoke(cli, ["validate-design"])

            assert result.exit_code == 0
            assert "検証" in result.output

    def test_prompt_tasks_command(self):
        """Test prompt_tasks command."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("## 機能要件\n- **REQ-01**: Test")
            Path("specs/design.md").write_text("## コンポーネント設計\n- **component**: Test")

            result = self.runner.invoke(cli, ["prompt-tasks"])

            assert result.exit_code == 0
            assert "tasks.md" in result.output
            assert "WBS" in result.output

    def test_validate_tasks_command(self):
        """Test validate_tasks command."""
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

            result = self.runner.invoke(cli, ["validate-tasks"])

            assert result.exit_code == 0
            assert "検証" in result.output

    def test_prompt_code_command(self):
        """Test prompt_code command."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("# Requirements\n- **REQ-01**: Test")
            Path("specs/design.md").write_text("# Design\n- Component: Test")
            Path("specs/tasks.md").write_text("# Tasks\n- **TASK-01-01**: Test")

            result = self.runner.invoke(cli, ["prompt-code"])

            assert result.exit_code == 0
            assert "実装" in result.output
            assert "TASK-01-01" in result.output

    def test_analyze_changes_command(self):
        """Test analyze_changes command."""
        result = self.runner.invoke(
            cli,
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

    def test_get_traceability_command(self):
        """Test get_traceability command."""
        with self.runner.isolated_filesystem():
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("## 機能要件\n- **REQ-01**: Test")
            Path("specs/design.md").write_text("## アーキテクチャ\n[REQ-01]")
            Path("specs/tasks.md").write_text("## タスク一覧\n- **TASK-01-01**: Test")

            result = self.runner.invoke(cli, ["get-traceability"])

            assert result.exit_code == 0
            assert "トレーサビリティレポート" in result.output

    def test_serve_command_without_server_flag(self):
        """Test serve command without --server flag."""
        result = self.runner.invoke(cli, ["serve"])

        assert result.exit_code == 1
        assert "Use --server flag" in result.output

    def test_all_commands_have_help(self):
        """Test that all commands have help text."""
        commands = [
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
            "serve",
        ]

        for cmd in commands:
            result = self.runner.invoke(cli, [cmd, "--help"])
            assert result.exit_code == 0
            assert "Usage:" in result.output
            assert "Options:" in result.output

    def test_command_error_handling(self):
        """Test command error handling."""
        # Test with invalid file path that will cause an error
        result = self.runner.invoke(
            cli, ["validate-requirements", "--requirementsPath", "/invalid/path/that/definitely/does/not/exist.md"]
        )

        # Command should handle the error gracefully
        assert result.exit_code == 0
        assert "エラー" in result.output


class TestCLIEdgeCases:
    """Test CLI edge cases and error conditions."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_empty_user_input(self):
        """Test check_completeness with empty input."""
        result = self.runner.invoke(cli, ["check-completeness", "--userInput", ""])

        assert result.exit_code == 0
        # Should still provide guidance even with empty input

    def test_very_long_user_input(self):
        """Test check_completeness with very long input."""
        long_input = "A" * 10000  # Very long input

        result = self.runner.invoke(cli, ["check-completeness", "--userInput", long_input])

        assert result.exit_code == 0

    def test_japanese_input(self):
        """Test CLI with Japanese input."""
        result = self.runner.invoke(
            cli,
            ["check-completeness", "--userInput", "日本語のプロジェクト説明です。Python、FastAPI、Reactを使用します。"],
        )

        assert result.exit_code == 0
        assert "プロジェクト情報を確認" in result.output

    def test_special_characters_input(self):
        """Test CLI with special characters."""
        result = self.runner.invoke(
            cli, ["check-completeness", "--userInput", "Project with symbols: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"]
        )

        assert result.exit_code == 0

    def test_multiple_flags_same_command(self):
        """Test command with multiple flags."""
        result = self.runner.invoke(
            cli,
            [
                "prompt-requirements",
                "--projectDescription",
                "Test project",
                "--scope",
                "Limited scope",
                "--constraints",
                "Python only",
            ],
        )

        assert result.exit_code == 0
        assert "Test project" in result.output
        assert "Limited scope" in result.output
        assert "Python only" in result.output


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_full_workflow_simulation(self):
        """Test a full SDD workflow through CLI."""
        with self.runner.isolated_filesystem():
            # Step 1: Check completeness
            result1 = self.runner.invoke(
                cli, ["check-completeness", "--userInput", "Python FastAPI web application for task management"]
            )
            assert result1.exit_code == 0

            # Step 2: Generate requirements (simulated by creating file)
            Path("specs").mkdir(exist_ok=True)
            Path("specs/requirements.md").write_text("""
## 0. サマリー
タスク管理用Webアプリケーション

## 1. 用語集
- **API**: Application Programming Interface

## 2. スコープ
### インスコープ
- タスク管理機能

## 3. 制約
- Python FastAPI使用

## 4. 非機能要件（NFR）
- **NFR-01**: レスポンス時間1秒以内

## 5. KPI
- **KPI-01**: ユーザー満足度90%以上

## 6. 機能要件（EARS）
- **REQ-01**: システムは、タスクを作成すること
- **REQ-02**: システムは、タスクを一覧表示すること
""")

            # Step 3: Validate requirements
            result3 = self.runner.invoke(cli, ["validate-requirements"])
            assert result3.exit_code == 0
            assert "検証に成功" in result3.output or "検証" in result3.output

            # Step 4: Generate design prompt
            result4 = self.runner.invoke(cli, ["prompt-design"])
            assert result4.exit_code == 0
            assert "design.md" in result4.output

            # Create design file for next steps
            Path("specs/design.md").write_text("""
## アーキテクチャ概要
FastAPI RESTful API [REQ-01, REQ-02]

## コンポーネント設計
- **task-service**: タスク管理 [REQ-01, REQ-02]

## データ設計
Task model definition

## API設計
REST endpoints

## 非機能設計
Performance optimization

## テスト戦略
Unit and integration tests
""")

            # Step 5: Validate design
            result5 = self.runner.invoke(cli, ["validate-design"])
            assert result5.exit_code == 0

            # Step 6: Generate tasks prompt
            result6 = self.runner.invoke(cli, ["prompt-tasks"])
            assert result6.exit_code == 0
            assert "tasks.md" in result6.output

            # Create tasks file
            Path("specs/tasks.md").write_text("""
## 概要
開発タスクの分解

## タスク一覧
- **TASK-01-01**: 環境構築
- **TASK-01-02**: データモデル作成
- **TASK-02-01**: API実装

## 依存関係
TASK-01-01 → TASK-01-02 → TASK-02-01

## マイルストーン
- M1: 基盤完成
""")

            # Step 7: Validate tasks
            result7 = self.runner.invoke(cli, ["validate-tasks"])
            assert result7.exit_code == 0

            # Step 8: Get traceability report
            result8 = self.runner.invoke(cli, ["get-traceability"])
            assert result8.exit_code == 0
            assert "トレーサビリティレポート" in result8.output

            # Step 9: Generate implementation prompt
            result9 = self.runner.invoke(cli, ["prompt-code"])
            assert result9.exit_code == 0
            assert "実装" in result9.output
