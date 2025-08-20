"""Unit tests for generate_review_prompt functionality."""

from unittest.mock import Mock

from wassden.handlers.code_analysis import (
    _extract_file_structure_from_design,
    _extract_interfaces_from_design,
    _extract_related_requirements,
    _extract_related_test_requirements,
    _extract_task_info,
    _find_requirement_detail,
    _format_requirements_list,
)


class TestTaskInfoExtraction:
    """Test task information extraction functions."""

    def test_extract_task_info_success(self):
        """Test successful task info extraction."""
        tasks_content = """
## Phase 1: Setup
Initial setup phase

## タスク一覧
- **TASK-01-01**: 環境構築とプロジェクト初期化
- **TASK-01-02**: データベース設計と実装

## Phase 2: Development
Development phase

## タスク一覧
- **TASK-02-01**: API実装
"""

        result = _extract_task_info(tasks_content, "TASK-01-01")

        assert result is not None
        assert result["phase"] == "## Phase 1: Setup"
        assert "環境構築とプロジェクト初期化" in result["summary"]

    def test_extract_task_info_not_found(self):
        """Test task info extraction when task not found."""
        tasks_content = """
## タスク一覧
- **TASK-01-01**: Test task
"""

        result = _extract_task_info(tasks_content, "TASK-99-99")

        assert result is None

    def test_extract_task_info_no_phase(self):
        """Test task info extraction without phase information."""
        tasks_content = """
## タスク一覧
- **TASK-01-01**: Test task without phase
"""

        result = _extract_task_info(tasks_content, "TASK-01-01")

        assert result is not None
        assert result["phase"] == ""
        assert "Test task without phase" in result["summary"]


class TestRequirementExtraction:
    """Test requirement extraction functions."""

    def test_extract_related_requirements(self):
        """Test extraction of related requirements."""
        task_info = {"summary": "Environment setup [REQ-01] and database [REQ-02]", "phase": "Phase 1 with REQ-03"}
        requirements_content = """
## 機能要件
- **REQ-01**: システムは、環境を構築すること
- **REQ-02**: システムは、データベースを作成すること
- **REQ-03**: システムは、設定を保存すること
"""

        result = _extract_related_requirements(task_info, requirements_content)

        assert len(result) == 3
        assert any("REQ-01" in req for req in result)
        assert any("REQ-02" in req for req in result)
        assert any("REQ-03" in req for req in result)

    def test_extract_related_test_requirements(self):
        """Test extraction of related test requirements."""
        task_info = {"summary": "Testing task [TR-01] with validation [TR-02]", "phase": "Test phase"}
        requirements_content = """
## テスト要件
- **TR-01**: テストは、環境構築を検証すること
- **TR-02**: テストは、データベース接続を確認すること
"""

        result = _extract_related_test_requirements(task_info, requirements_content)

        assert len(result) == 2
        assert any("TR-01" in req for req in result)
        assert any("TR-02" in req for req in result)

    def test_find_requirement_detail(self):
        """Test finding requirement detail by ID."""
        requirements_content = """
## 機能要件
- **REQ-01**: システムは、ユーザーログインすること
- **REQ-02**: システムは、データを保存すること
"""

        result = _find_requirement_detail(requirements_content, "REQ-01")

        assert result is not None
        assert "REQ-01" in result
        assert "ユーザーログイン" in result

    def test_find_requirement_detail_not_found(self):
        """Test finding requirement detail when not found."""
        requirements_content = """
## 機能要件
- **REQ-01**: システムは、テストすること
"""

        result = _find_requirement_detail(requirements_content, "REQ-99")

        assert result is None

    def test_format_requirements_list(self):
        """Test formatting requirements list."""
        requirements = ["**REQ-01**: First requirement", "**REQ-02**: Second requirement"]

        mock_i18n = Mock()
        result = _format_requirements_list(requirements, mock_i18n)

        assert "- **REQ-01**: First requirement" in result
        assert "- **REQ-02**: Second requirement" in result

    def test_format_requirements_list_empty(self):
        """Test formatting empty requirements list."""
        requirements = []

        mock_i18n = Mock()
        mock_i18n.t.return_value = "なし"
        result = _format_requirements_list(requirements, mock_i18n)

        assert result == "なし"


class TestDesignExtraction:
    """Test design extraction functions."""

    def test_extract_file_structure_from_design(self):
        """Test extracting file structure from design."""
        design_content = """
## ファイル構成
- src/main.py
- src/models/user.py

## コンポーネント設計
- User module for authentication
- Database module for data persistence
"""

        mock_i18n = Mock()
        mock_i18n.t.return_value = ["ファイル", "file", "モジュール", "module", "構成"]
        result = _extract_file_structure_from_design(design_content, mock_i18n)

        assert "ファイル構成" in result
        # The function extracts lines containing file-related keywords
        # Check that at least the section header is found
        assert len(result.split("\n")) > 0

    def test_extract_file_structure_empty(self):
        """Test extracting file structure when no matches found."""
        design_content = """
## アーキテクチャ
Simple architecture
"""

        mock_i18n = Mock()
        mock_i18n.t.side_effect = lambda key: {
            "code_prompts.helpers.search_keywords.file_structure": ["ファイル", "file", "モジュール", "module", "構成"],
            "code_prompts.helpers.file_structure_not_found": "設計書から構成情報を確認してください",
        }[key]
        result = _extract_file_structure_from_design(design_content, mock_i18n)

        assert result == "設計書から構成情報を確認してください"

    def test_extract_interfaces_from_design(self):
        """Test extracting interfaces from design."""
        design_content = """
## API設計
REST API endpoints

## インターフェース仕様
- getUserById(id: string): User
- createUser(data: UserData): User

## 関数一覧
- validateUser(): boolean
"""

        mock_i18n = Mock()
        mock_i18n.t.return_value = ["api", "インターフェース", "interface", "関数", "function", "メソッド", "method"]
        result = _extract_interfaces_from_design(design_content, mock_i18n)

        assert "API設計" in result
        assert "インターフェース仕様" in result
        assert "関数一覧" in result

    def test_extract_interfaces_empty(self):
        """Test extracting interfaces when no matches found."""
        design_content = """
## データベース設計
Table schemas
"""

        mock_i18n = Mock()
        mock_i18n.t.side_effect = lambda key: {
            "code_prompts.helpers.search_keywords.interfaces": [
                "api",
                "インターフェース",
                "interface",
                "関数",
                "function",
                "メソッド",
                "method",
            ],
            "code_prompts.helpers.interfaces_not_found": "設計書からインターフェース情報を確認してください",
        }[key]
        result = _extract_interfaces_from_design(design_content, mock_i18n)

        assert result == "設計書からインターフェース情報を確認してください"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_extract_task_info_multiple_colons(self):
        """Test task info extraction with multiple colons in summary."""
        tasks_content = """
## タスク一覧
- **TASK-01-01**: Database: Setup and configuration: PostgreSQL
"""

        result = _extract_task_info(tasks_content, "TASK-01-01")

        assert result is not None
        assert "Database: Setup and configuration: PostgreSQL" in result["summary"]

    def test_extract_requirements_special_characters(self):
        """Test requirement extraction with special characters."""
        task_info = {"summary": "Task with special chars [REQ-01] & symbols", "phase": "Phase with $pecial chars"}
        requirements_content = """
- **REQ-01**: システムは、特殊文字 & シンボルを処理すること
"""

        result = _extract_related_requirements(task_info, requirements_content)

        assert len(result) == 1
        assert "特殊文字 & シンボル" in result[0]

    def test_extract_task_info_unicode(self):
        """Test task info extraction with unicode characters."""
        tasks_content = """
## Phase 1: 🚀 Setup
## タスク一覧
- **TASK-01-01**: 🔧 環境構築 ⚙️ with emojis
"""

        result = _extract_task_info(tasks_content, "TASK-01-01")

        assert result is not None
        assert "🔧 環境構築 ⚙️" in result["summary"]
        assert "🚀" in result["phase"]
