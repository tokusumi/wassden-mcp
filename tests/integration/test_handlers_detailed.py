"""Detailed integration tests for handlers matching TypeScript version granularity."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

from wassden.handlers import (
    handle_analyze_changes,
    handle_check_completeness,
    handle_get_traceability,
    handle_prompt_code,
    handle_prompt_design,
    handle_prompt_requirements,
    handle_prompt_tasks,
    handle_validate_design,
    handle_validate_requirements,
    handle_validate_tasks,
)


class TestCheckCompletenessHandler:
    """Detailed check_completeness handler tests."""

    @pytest.mark.asyncio
    async def test_handle_check_completeness_basic_input(self):
        """Test check_completeness handler with basic input."""
        result = await handle_check_completeness({"userInput": "Simple test project"})

        assert isinstance(result, dict)
        assert "content" in result
        assert len(result["content"]) > 0
        assert "text" in result["content"][0]

        text = result["content"][0]["text"]
        assert "プロジェクト情報を確認" in text

    @pytest.mark.asyncio
    async def test_handle_check_completeness_comprehensive_input(self):
        """Test check_completeness handler with comprehensive input."""
        comprehensive_input = """
        Python FastAPI RESTful API for task management.
        Technology: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL
        Users: Project managers and team members
        Constraints: Must be cloud-deployable, response time < 1s
        Scope: CRUD operations for tasks, user authentication, basic reporting
        Budget: $50,000
        Timeline: 3 months
        Team: 3 developers, 1 designer
        """

        result = await handle_check_completeness({"userInput": comprehensive_input})

        text = result["content"][0]["text"]
        assert "requirements.md" in text or "プロジェクト情報を確認" in text

    @pytest.mark.asyncio
    async def test_handle_check_completeness_incomplete_input(self):
        """Test check_completeness handler with incomplete input."""
        result = await handle_check_completeness({"userInput": "Simple project"})

        text = result["content"][0]["text"]
        # Should ask for more information
        assert "不足" in text or "不明" in text or "技術" in text or "ユーザー" in text

    @pytest.mark.asyncio
    async def test_handle_check_completeness_empty_input(self):
        """Test check_completeness handler with empty input."""
        result = await handle_check_completeness({"userInput": ""})

        text = result["content"][0]["text"]
        assert len(text) > 0  # Should provide some guidance

    @pytest.mark.asyncio
    async def test_handle_check_completeness_japanese_input(self):
        """Test check_completeness handler with Japanese input."""
        japanese_input = """
        日本語のプロジェクト説明です。
        技術スタック: Python 3.12、FastAPI、PostgreSQL
        ユーザー: プロジェクトマネージャーとチームメンバー
        制約: クラウド展開可能、レスポンス時間1秒以内
        スコープ: タスクのCRUD操作、ユーザー認証、基本レポート
        """

        result = await handle_check_completeness({"userInput": japanese_input})

        text = result["content"][0]["text"]
        assert "プロジェクト情報を確認" in text

    @pytest.mark.asyncio
    async def test_handle_check_completeness_special_characters(self):
        """Test check_completeness handler with special characters."""
        special_input = "Project with symbols: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"

        result = await handle_check_completeness({"userInput": special_input})

        text = result["content"][0]["text"]
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_handle_check_completeness_very_long_input(self):
        """Test check_completeness handler with very long input."""
        long_input = "Detailed project description. " * 1000  # Very long input

        result = await handle_check_completeness({"userInput": long_input})

        text = result["content"][0]["text"]
        assert len(text) > 0


class TestPromptRequirementsHandler:
    """Detailed prompt_requirements handler tests."""

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_basic(self):
        """Test prompt_requirements handler with basic input."""
        result = await handle_prompt_requirements({"projectDescription": "Test project for requirements generation"})

        assert isinstance(result, dict)
        assert "content" in result
        text = result["content"][0]["text"]

        assert "requirements.md" in text
        assert "EARS形式" in text
        assert "Test project for requirements generation" in text

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_with_scope(self):
        """Test prompt_requirements handler with scope."""
        result = await handle_prompt_requirements(
            {
                "projectDescription": "Web application project",
                "scope": "Enterprise-level web application with microservices",
            }
        )

        text = result["content"][0]["text"]
        assert "Web application project" in text
        assert "Enterprise-level web application with microservices" in text

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_with_constraints(self):
        """Test prompt_requirements handler with constraints."""
        result = await handle_prompt_requirements(
            {"projectDescription": "Mobile application", "constraints": "React Native, iOS/Android, offline capability"}
        )

        text = result["content"][0]["text"]
        assert "Mobile application" in text
        assert "React Native, iOS/Android, offline capability" in text

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_all_parameters(self):
        """Test prompt_requirements handler with all parameters."""
        result = await handle_prompt_requirements(
            {
                "projectDescription": "E-commerce platform",
                "scope": "B2B marketplace with vendor management",
                "constraints": "Python Django, PostgreSQL, AWS deployment, PCI compliance",
            }
        )

        text = result["content"][0]["text"]
        assert "E-commerce platform" in text
        assert "B2B marketplace with vendor management" in text
        assert "Python Django, PostgreSQL, AWS deployment, PCI compliance" in text

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_empty_description(self):
        """Test prompt_requirements handler with empty description."""
        result = await handle_prompt_requirements({"projectDescription": ""})

        text = result["content"][0]["text"]
        assert "requirements.md" in text
        assert "EARS形式" in text

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_special_characters(self):
        """Test prompt_requirements handler with special characters."""
        result = await handle_prompt_requirements(
            {
                "projectDescription": "Project with symbols: !@#$%^&*()",
                "scope": "Scope with symbols: <>?{}[]",
                "constraints": "Constraints with symbols: |\\:;\"'",
            }
        )

        text = result["content"][0]["text"]
        assert "Project with symbols: !@#$%^&*()" in text


class TestValidateRequirementsHandler:
    """Detailed validate_requirements handler tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment after each test."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_handle_validate_requirements_valid_file(self):
        """Test validate_requirements handler with valid file."""
        # Create specs directory
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create valid requirements file
        req_file = specs_dir / "requirements.md"
        req_content = """
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
"""
        req_file.write_text(req_content)

        result = await handle_validate_requirements({"requirementsPath": str(req_file)})

        text = result["content"][0]["text"]
        assert "✅" in text
        assert "要件数: 2" in text

    @pytest.mark.asyncio
    async def test_handle_validate_requirements_invalid_file(self):
        """Test validate_requirements handler with invalid file."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create invalid requirements file
        req_file = specs_dir / "requirements.md"
        invalid_content = """
# Invalid Requirements

## Summary
Missing required sections and invalid IDs

## Functional Requirements
- **REQ-001**: Invalid ID format
- **REQ-1**: Also invalid format
- **INVALID-01**: Wrong prefix
"""
        req_file.write_text(invalid_content)

        result = await handle_validate_requirements({"requirementsPath": str(req_file)})

        text = result["content"][0]["text"]
        assert "⚠️" in text or "修正が必要" in text

    @pytest.mark.asyncio
    async def test_handle_validate_requirements_nonexistent_file(self):
        """Test validate_requirements handler with non-existent file."""
        result = await handle_validate_requirements({"requirementsPath": "nonexistent/requirements.md"})

        text = result["content"][0]["text"]
        assert "エラー" in text
        assert "見つかりません" in text

    @pytest.mark.asyncio
    async def test_handle_validate_requirements_default_path(self):
        """Test validate_requirements handler with default path."""
        result = await handle_validate_requirements({})

        text = result["content"][0]["text"]
        # Should either show error or attempt validation
        assert "エラー" in text or "検証" in text

    @pytest.mark.asyncio
    async def test_handle_validate_requirements_empty_file(self):
        """Test validate_requirements handler with empty file."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create empty requirements file
        req_file = specs_dir / "requirements.md"
        req_file.write_text("")

        result = await handle_validate_requirements({"requirementsPath": str(req_file)})

        text = result["content"][0]["text"]
        # Should handle empty file gracefully
        assert len(text) > 0


class TestPromptDesignHandler:
    """Detailed prompt_design handler tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment after each test."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_handle_prompt_design_valid_requirements(self):
        """Test prompt_design handler with valid requirements."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create requirements file
        req_file = specs_dir / "requirements.md"
        req_content = """
# Requirements Document

## 6. 機能要件（EARS）
- **REQ-01**: システムは、ユーザー認証を行うこと
- **REQ-02**: システムは、データ管理を行うこと
- **REQ-03**: システムは、レポート生成を行うこと
"""
        req_file.write_text(req_content)

        result = await handle_prompt_design({"requirementsPath": str(req_file)})

        text = result["content"][0]["text"]
        assert "design.md" in text
        assert req_content in text

    @pytest.mark.asyncio
    async def test_handle_prompt_design_nonexistent_requirements(self):
        """Test prompt_design handler with non-existent requirements."""
        result = await handle_prompt_design({"requirementsPath": "nonexistent/requirements.md"})

        text = result["content"][0]["text"]
        assert "エラー" in text

    @pytest.mark.asyncio
    async def test_handle_prompt_design_default_path(self):
        """Test prompt_design handler with default path."""
        result = await handle_prompt_design({})

        text = result["content"][0]["text"]
        # Should either show error or attempt to generate prompt
        assert "エラー" in text or "design.md" in text

    @pytest.mark.asyncio
    async def test_handle_prompt_design_complex_requirements(self):
        """Test prompt_design handler with complex requirements."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create complex requirements file
        req_file = specs_dir / "requirements.md"
        complex_requirements = """
# Requirements Document

## 0. サマリー
複雑なシステムの要件定義

## 1. 用語集
- **API**: Application Programming Interface
- **SDD**: Spec-Driven Development
- **MCP**: Model Context Protocol

## 2. スコープ
### インスコープ
- ユーザー管理
- データ管理
- レポート機能
- API提供

### アウトオブスコープ
- モバイルアプリ
- リアルタイム通知

## 3. 制約
- Python 3.12以上
- FastAPI使用
- PostgreSQL使用
- クラウド展開

## 4. 非機能要件（NFR）
- **NFR-01**: APIレスポンス時間は1秒以内であること
- **NFR-02**: 同時接続100ユーザーまで対応すること
- **NFR-03**: データは暗号化して保存すること

## 5. KPI / 受入基準
- **KPI-01**: API応答時間平均500ms以下
- **KPI-02**: システム稼働率99%以上
- **KPI-03**: ユーザー満足度4.0/5.0以上

## 6. 機能要件（EARS）
- **REQ-01**: システムは、ユーザーがログインするとき、認証を行うこと
- **REQ-02**: システムは、データを保存するとき、暗号化すること
- **REQ-03**: システムは、レポートを生成するとき、PDF形式で出力すること
- **REQ-04**: システムは、APIを提供するとき、RESTful形式で提供すること
- **REQ-05**: システムは、エラーが発生したとき、ログに記録すること
"""
        req_file.write_text(complex_requirements)

        result = await handle_prompt_design({"requirementsPath": str(req_file)})

        text = result["content"][0]["text"]
        assert "design.md" in text
        assert "REQ-01" in text
        assert "REQ-05" in text
        assert complex_requirements in text


class TestValidateDesignHandler:
    """Detailed validate_design handler tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment after each test."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_handle_validate_design_valid_files(self):
        """Test validate_design handler with valid files."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create requirements file
        req_file = specs_dir / "requirements.md"
        req_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証を行うこと
- **REQ-02**: システムは、データ管理を行うこと
"""
        req_file.write_text(req_content)

        # Create design file
        design_file = specs_dir / "design.md"
        design_content = """
# Design Document

## 1. アーキテクチャ概要
システム設計の概要 [REQ-01, REQ-02]

## 2. コンポーネント設計
- **auth-service**: 認証サービス [REQ-01]
- **data-service**: データサービス [REQ-02]

## 3. データモデル
データ構造の定義

## 4. API設計
API仕様の詳細

## 5. 非機能設計
パフォーマンスとセキュリティ

## 6. テスト戦略
テスト計画とアプローチ
"""
        design_file.write_text(design_content)

        result = await handle_validate_design({"designPath": str(design_file), "requirementsPath": str(req_file)})

        text = result["content"][0]["text"]
        assert "✅" in text
        assert "参照要件数: 2" in text

    @pytest.mark.asyncio
    async def test_handle_validate_design_missing_requirements(self):
        """Test validate_design handler with missing requirement references."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create requirements file with 3 requirements
        req_file = specs_dir / "requirements.md"
        req_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証を行うこと
- **REQ-02**: システムは、データ管理を行うこと
- **REQ-03**: システムは、レポート生成を行うこと
"""
        req_file.write_text(req_content)

        # Create design file that only references REQ-01 and REQ-02
        design_file = specs_dir / "design.md"
        design_content = """
# Design Document

## 1. アーキテクチャ概要
システム設計 [REQ-01, REQ-02]

## 2. コンポーネント設計
- **auth-service**: 認証 [REQ-01]
- **data-service**: データ [REQ-02]

## 3. データモデル
データ構造

## 4. API設計
API仕様

## 5. 非機能設計
非機能設計

## 6. テスト戦略
テスト戦略
"""
        design_file.write_text(design_content)

        result = await handle_validate_design({"designPath": str(design_file), "requirementsPath": str(req_file)})

        text = result["content"][0]["text"]
        # Should detect missing REQ-03
        assert "⚠️" in text or "修正が必要" in text

    @pytest.mark.asyncio
    async def test_handle_validate_design_nonexistent_files(self):
        """Test validate_design handler with non-existent files."""
        result = await handle_validate_design(
            {"designPath": "nonexistent/design.md", "requirementsPath": "nonexistent/requirements.md"}
        )

        text = result["content"][0]["text"]
        assert "エラー" in text


class TestPromptTasksHandler:
    """Detailed prompt_tasks handler tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment after each test."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_handle_prompt_tasks_valid_files(self):
        """Test prompt_tasks handler with valid files."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create requirements file
        req_file = specs_dir / "requirements.md"
        req_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証を行うこと
- **REQ-02**: システムは、データ管理を行うこと
"""
        req_file.write_text(req_content)

        # Create design file
        design_file = specs_dir / "design.md"
        design_content = """
## アーキテクチャ概要
システム設計 [REQ-01, REQ-02]

## コンポーネント設計
- **auth-service**: 認証 [REQ-01]
- **data-service**: データ [REQ-02]
"""
        design_file.write_text(design_content)

        result = await handle_prompt_tasks({"designPath": str(design_file), "requirementsPath": str(req_file)})

        text = result["content"][0]["text"]
        assert "tasks.md" in text
        assert "WBS" in text
        assert design_content in text
        assert req_content in text


class TestValidateTasksHandler:
    """Detailed validate_tasks handler tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment after each test."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_handle_validate_tasks_valid_file(self):
        """Test validate_tasks handler with valid file."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create tasks file
        tasks_file = specs_dir / "tasks.md"
        tasks_content = """
# Tasks Document

## 1. 概要
タスクの概要説明

## 2. タスク一覧
- **TASK-01-01**: 環境構築
- **TASK-01-02**: 認証機能実装
- **TASK-02-01**: データ管理機能実装

## 3. 依存関係
TASK-01-01 → TASK-01-02 → TASK-02-01

## 4. マイルストーン
- M1: 基盤完成
- M2: 機能完成
"""
        tasks_file.write_text(tasks_content)

        result = await handle_validate_tasks({"tasksPath": str(tasks_file)})

        text = result["content"][0]["text"]
        assert "✅" in text
        assert "タスク数: 3" in text

    @pytest.mark.asyncio
    async def test_handle_validate_tasks_invalid_file(self):
        """Test validate_tasks handler with invalid file."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create invalid tasks file
        tasks_file = specs_dir / "tasks.md"
        invalid_content = """
## タスク一覧
- **TASK-1-01**: 無効フォーマット1
- **TASK-01-1**: 無効フォーマット2
- **INVALID-01-01**: 間違ったプレフィックス
"""
        tasks_file.write_text(invalid_content)

        result = await handle_validate_tasks({"tasksPath": str(tasks_file)})

        text = result["content"][0]["text"]
        # Should detect validation issues
        assert "⚠️" in text or "修正が必要" in text


class TestPromptCodeHandler:
    """Detailed prompt_code handler tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment after each test."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_handle_prompt_code_valid_files(self):
        """Test prompt_code handler with valid files."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create all required files
        req_file = specs_dir / "requirements.md"
        req_content = "# Requirements\n- **REQ-01**: Test requirement"
        req_file.write_text(req_content)

        design_file = specs_dir / "design.md"
        design_content = "# Design\n- Component: Test component"
        design_file.write_text(design_content)

        tasks_file = specs_dir / "tasks.md"
        tasks_content = "# Tasks\n- **TASK-01-01**: Test task"
        tasks_file.write_text(tasks_content)

        result = await handle_prompt_code(
            {"tasksPath": str(tasks_file), "requirementsPath": str(req_file), "designPath": str(design_file)}
        )

        text = result["content"][0]["text"]
        assert "実装" in text
        assert "TASK-01-01" in text
        assert req_content in text
        assert design_content in text
        assert tasks_content in text


class TestAnalyzeChangesHandler:
    """Detailed analyze_changes handler tests."""

    @pytest.mark.asyncio
    async def test_handle_analyze_changes_basic(self):
        """Test analyze_changes handler with basic input."""
        result = await handle_analyze_changes(
            {"changedFile": "specs/requirements.md", "changeDescription": "Added REQ-05 for user authentication"}
        )

        text = result["content"][0]["text"]
        assert "変更影響分析" in text
        assert "REQ-05" in text
        assert "requirements.md" in text

    @pytest.mark.asyncio
    async def test_handle_analyze_changes_complex_description(self):
        """Test analyze_changes handler with complex description."""
        complex_description = """
        Major changes to the requirements:
        1. Added REQ-06, REQ-07, REQ-08 for new user management features
        2. Modified REQ-02 to include additional validation logic
        3. Removed deprecated REQ-04 that was replaced by REQ-06
        4. Updated section 3 (constraints) to include new security requirements
        """

        result = await handle_analyze_changes(
            {"changedFile": "specs/requirements.md", "changeDescription": complex_description}
        )

        text = result["content"][0]["text"]
        assert "変更影響分析" in text
        assert "REQ-06" in text
        assert "REQ-07" in text
        assert "REQ-08" in text

    @pytest.mark.asyncio
    async def test_handle_analyze_changes_empty_description(self):
        """Test analyze_changes handler with empty description."""
        result = await handle_analyze_changes({"changedFile": "specs/design.md", "changeDescription": ""})

        text = result["content"][0]["text"]
        assert "変更影響分析" in text
        assert "design.md" in text

    @pytest.mark.asyncio
    async def test_handle_analyze_changes_different_file_types(self):
        """Test analyze_changes handler with different file types."""
        file_types = ["specs/requirements.md", "specs/design.md", "specs/tasks.md", "src/main.py", "docs/api.md"]

        for file_type in file_types:
            result = await handle_analyze_changes(
                {"changedFile": file_type, "changeDescription": f"Modified {file_type} with updates"}
            )

            text = result["content"][0]["text"]
            assert "変更影響分析" in text
            assert file_type in text


class TestGetTraceabilityHandler:
    """Detailed get_traceability handler tests."""

    def setup_method(self):
        """Set up test environment for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment after each test."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_handle_get_traceability_no_files(self):
        """Test get_traceability handler with no files."""
        result = await handle_get_traceability(
            {
                "requirementsPath": "nonexistent_req.md",
                "designPath": "nonexistent_design.md",
                "tasksPath": "nonexistent_tasks.md",
            }
        )

        text = result["content"][0]["text"]
        assert "トレーサビリティレポート" in text
        assert "要件数: 0" in text

    @pytest.mark.asyncio
    async def test_handle_get_traceability_with_files(self):
        """Test get_traceability handler with valid files."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create requirements file
        req_file = specs_dir / "requirements.md"
        req_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証を行うこと
- **REQ-02**: システムは、データ管理を行うこと
- **REQ-03**: システムは、レポート生成を行うこと
"""
        req_file.write_text(req_content)

        # Create design file
        design_file = specs_dir / "design.md"
        design_content = """
## アーキテクチャ概要
システム設計 [REQ-01, REQ-02, REQ-03]

## コンポーネント設計
- **auth-service**: 認証 [REQ-01]
- **data-service**: データ [REQ-02]
- **report-service**: レポート [REQ-03]
"""
        design_file.write_text(design_content)

        # Create tasks file
        tasks_file = specs_dir / "tasks.md"
        tasks_content = """
## タスク一覧
- **TASK-01-01**: 認証実装
- **TASK-01-02**: データ管理実装
- **TASK-02-01**: レポート実装
"""
        tasks_file.write_text(tasks_content)

        result = await handle_get_traceability(
            {"requirementsPath": str(req_file), "designPath": str(design_file), "tasksPath": str(tasks_file)}
        )

        text = result["content"][0]["text"]
        assert "トレーサビリティレポート" in text
        assert "要件数: 3" in text
        assert "REQ-01" in text
        assert "REQ-02" in text
        assert "REQ-03" in text

    @pytest.mark.asyncio
    async def test_handle_get_traceability_partial_files(self):
        """Test get_traceability handler with some missing files."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create only requirements file
        req_file = specs_dir / "requirements.md"
        req_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証を行うこと
- **REQ-02**: システムは、データ管理を行うこと
"""
        req_file.write_text(req_content)

        result = await handle_get_traceability(
            {
                "requirementsPath": str(req_file),
                "designPath": "nonexistent_design.md",
                "tasksPath": "nonexistent_tasks.md",
            }
        )

        text = result["content"][0]["text"]
        assert "トレーサビリティレポート" in text
        assert "要件数: 2" in text
