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
from wassden.types import HandlerResponse, Language, SpecDocuments


class TestCheckCompletenessHandler:
    """Detailed check_completeness handler tests."""

    @pytest.mark.asyncio
    async def test_handle_check_completeness_basic_input(self):
        """Test check_completeness handler with basic input."""
        result = await handle_check_completeness("Simple test project", Language.JAPANESE)

        assert isinstance(result, HandlerResponse)
        assert len(result.content) > 0
        assert hasattr(result.content[0], "text")

        text = result.content[0].text
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

        result = await handle_check_completeness(comprehensive_input, Language.JAPANESE)

        text = result.content[0].text
        assert "requirements.md" in text or "プロジェクト情報を確認" in text

    @pytest.mark.asyncio
    async def test_handle_check_completeness_incomplete_input(self):
        """Test check_completeness handler with incomplete input."""
        result = await handle_check_completeness("Simple project", Language.JAPANESE)

        text = result.content[0].text
        assert "プロジェクト情報を確認" in text
        # Should provide guidance about missing information
        assert "情報" in text

    @pytest.mark.asyncio
    async def test_handle_check_completeness_empty_input(self):
        """Test check_completeness handler with empty input."""
        result = await handle_check_completeness("", Language.JAPANESE)

        text = result.content[0].text
        assert "プロジェクト情報を確認" in text
        # Should provide guidance about project information
        assert "情報" in text

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

        result = await handle_check_completeness(japanese_input, Language.JAPANESE)

        text = result.content[0].text
        assert "プロジェクト情報を確認" in text

    @pytest.mark.asyncio
    async def test_handle_check_completeness_special_characters(self):
        """Test check_completeness handler with special characters."""
        special_input = "Project with symbols: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./"

        result = await handle_check_completeness(special_input, Language.JAPANESE)

        text = result.content[0].text
        assert "プロジェクト情報を確認" in text
        assert isinstance(text, str)

    @pytest.mark.asyncio
    async def test_handle_check_completeness_very_long_input(self):
        """Test check_completeness handler with very long input."""
        long_input = "Detailed project description. " * 1000  # Very long input

        result = await handle_check_completeness(long_input, Language.JAPANESE)

        text = result.content[0].text
        assert len(text) > 0


class TestPromptRequirementsHandler:
    """Detailed prompt_requirements handler tests."""

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_basic(self):
        """Test prompt_requirements handler with basic input."""
        description = "Simple web application for task management"
        result = await handle_prompt_requirements(description, "", "", Language.JAPANESE)

        assert isinstance(result, HandlerResponse)
        assert len(result.content) > 0

        text = result.content[0].text
        assert len(text) > 100
        assert "要件" in text or "requirements" in text.lower()

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_with_scope(self):
        """Test prompt_requirements handler with scope."""
        result = await handle_prompt_requirements(
            "Web application project", "Enterprise-level web application with microservices", "", Language.JAPANESE
        )

        text = result.content[0].text
        assert "microservices" in text or "マイクロサービス" in text
        assert len(text) > 100

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_with_constraints(self):
        """Test prompt_requirements handler with constraints."""
        result = await handle_prompt_requirements(
            "Mobile application", "", "React Native, iOS/Android, offline capability", Language.JAPANESE
        )

        text = result.content[0].text
        assert "React Native" in text or "制約" in text
        assert len(text) > 100

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_all_parameters(self):
        """Test prompt_requirements handler with all parameters."""
        result = await handle_prompt_requirements(
            "E-commerce platform",
            "B2B marketplace with vendor management",
            "AWS cloud, microservices, GDPR compliance",
            Language.JAPANESE,
        )

        text = result.content[0].text
        assert "E-commerce" in text or "marketplace" in text or "B2B" in text
        assert len(text) > 100

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_empty_description(self):
        """Test prompt_requirements handler with empty description."""
        result = await handle_prompt_requirements("", "", "", Language.JAPANESE)

        text = result.content[0].text
        assert "requirements.md" in text

    @pytest.mark.asyncio
    async def test_handle_prompt_requirements_special_characters(self):
        """Test prompt_requirements handler with special characters."""
        result = await handle_prompt_requirements(
            "Project with symbols: !@#$%^&*()",
            "Scope with symbols: <>?{}[]",
            "Constraints with symbols: |\\\"';",
            Language.JAPANESE,
        )

        text = result.content[0].text
        assert len(text) > 100
        assert isinstance(text, str)


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
        """Test validate_requirements handler with valid requirements file."""
        valid_requirements = """# 要件仕様書

## 1. システム概要
- 種別: Webアプリケーション
- 目的: タスク管理システム

## 2. 機能要件
### 2.1 ユーザー管理
- ユーザー登録機能
- ログイン・ログアウト機能

### 2.2 タスク管理
- タスク作成機能
- タスク編集機能
- タスク削除機能

## 3. 非機能要件
### 3.1 性能要件
- 応答時間: 3秒以内
- 同時接続数: 1000ユーザー

### 3.2 セキュリティ要件
- 認証機能実装
- HTTPS通信対応

## 4. 制約事項
- 開発期間: 3ヶ月
- 予算: 500万円

## 5. その他
- 運用開始予定: 2024年4月"""

        requirements_file = self.temp_dir / "requirements.md"
        requirements_file.write_text(valid_requirements, encoding="utf-8")

        specs = await SpecDocuments.from_paths(requirements_path=requirements_file, language=Language.JAPANESE)
        result = await handle_validate_requirements(specs)

        text = result.content[0].text
        # Should contain validation output with either success or fixes needed
        assert "修正" in text or "検証" in text or "validation" in text.lower()
        assert "requirements.md" in text

    @pytest.mark.asyncio
    async def test_handle_validate_requirements_invalid_file(self):
        """Test validate_requirements handler with invalid file."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create invalid requirements file
        req_file = specs_dir / "requirements.md"
        req_file.write_text("Invalid content without proper structure", encoding="utf-8")

        specs = await SpecDocuments.from_paths(requirements_path=req_file, language=Language.JAPANESE)
        result = await handle_validate_requirements(specs)

        text = result.content[0].text
        # Should contain validation output with fixes needed
        assert "修正" in text or "検証" in text or "validation" in text.lower()
        assert len(text) > 50

    @pytest.mark.asyncio
    async def test_handle_validate_requirements_nonexistent_file(self):
        """Test validate_requirements handler with non-existent file."""
        specs = await SpecDocuments.from_paths(
            requirements_path=Path("nonexistent/requirements.md"), language=Language.JAPANESE
        )
        result = await handle_validate_requirements(specs)

        text = result.content[0].text
        assert "エラー" in text
        assert "見つかりません" in text

    @pytest.mark.asyncio
    async def test_handle_validate_requirements_default_path(self):
        """Test validate_requirements handler with default path."""
        specs = await SpecDocuments.from_paths(
            requirements_path=Path("specs/requirements.md"), language=Language.JAPANESE
        )
        result = await handle_validate_requirements(specs)

        text = result.content[0].text
        assert isinstance(text, str)
        assert len(text) > 10

    @pytest.mark.asyncio
    async def test_handle_validate_requirements_empty_file(self):
        """Test validate_requirements handler with empty file."""
        specs_dir = self.temp_dir / "specs"
        specs_dir.mkdir()

        # Create empty requirements file
        req_file = specs_dir / "requirements.md"
        req_file.write_text("", encoding="utf-8")

        specs = await SpecDocuments.from_paths(requirements_path=req_file, language=Language.JAPANESE)
        result = await handle_validate_requirements(specs)

        text = result.content[0].text
        # Should contain validation output
        assert "修正" in text or "検証" in text or "validation" in text.lower()
        assert len(text) > 10


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

        specs = await SpecDocuments.from_paths(requirements_path=req_file, language=Language.JAPANESE)
        result = await handle_prompt_design(specs)

        text = result.content[0].text
        assert "design.md" in text
        assert req_content in text

    @pytest.mark.asyncio
    async def test_handle_prompt_design_nonexistent_requirements(self):
        """Test prompt_design handler with non-existent requirements."""
        specs = await SpecDocuments.from_paths(requirements_path=Path("nonexistent/requirements.md"))
        result = await handle_prompt_design(specs)

        text = result.content[0].text
        assert "エラー" in text

    @pytest.mark.asyncio
    async def test_handle_prompt_design_default_path(self):
        """Test prompt_design handler with default path."""
        specs = await SpecDocuments.from_paths(requirements_path=Path("specs/requirements.md"))
        result = await handle_prompt_design(specs)

        text = result.content[0].text
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

        specs = await SpecDocuments.from_paths(requirements_path=req_file, language=Language.JAPANESE)
        result = await handle_prompt_design(specs)

        text = result.content[0].text
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
システム設計の概要

## 2. コンポーネント設計
- **auth-service**: 認証サービス
- **data-service**: データサービス

## 3. データモデル
データ構造の定義

## 4. API設計
API仕様の詳細

## 5. 非機能設計
パフォーマンスとセキュリティ

## 6. テスト戦略
テスト計画とアプローチ

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **auth-service**
- REQ-02 ⇔ **data-service**
"""
        design_file.write_text(design_content)

        specs = await SpecDocuments.from_paths(
            requirements_path=req_file, design_path=design_file, language=Language.JAPANESE
        )
        result = await handle_validate_design(specs)

        text = result.content[0].text
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

        specs = await SpecDocuments.from_paths(
            requirements_path=req_file, design_path=design_file, language=Language.JAPANESE
        )
        result = await handle_validate_design(specs)

        text = result.content[0].text
        # Should detect missing REQ-03
        assert "⚠️" in text or "修正が必要" in text

    @pytest.mark.asyncio
    async def test_handle_validate_design_nonexistent_files(self):
        """Test validate_design handler with non-existent files."""
        specs = await SpecDocuments.from_paths(
            requirements_path=Path("nonexistent/requirements.md"),
            design_path=Path("nonexistent/design.md"),
        )
        result = await handle_validate_design(specs)

        text = result.content[0].text
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

        specs = await SpecDocuments.from_paths(
            requirements_path=req_file, design_path=design_file, language=Language.JAPANESE
        )
        result = await handle_prompt_tasks(specs)

        text = result.content[0].text
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

        specs = await SpecDocuments.from_paths(tasks_path=tasks_file, language=Language.JAPANESE)
        result = await handle_validate_tasks(specs)

        text = result.content[0].text
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

        specs = await SpecDocuments.from_paths(tasks_path=tasks_file, language=Language.JAPANESE)
        result = await handle_validate_tasks(specs)

        text = result.content[0].text
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

        specs = await SpecDocuments.from_paths(
            requirements_path=req_file, design_path=design_file, tasks_path=tasks_file, language=Language.JAPANESE
        )
        result = await handle_prompt_code(specs)

        text = result.content[0].text
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
            Path("specs/requirements.md"), "Added REQ-05 for user authentication", Language.JAPANESE
        )

        text = result.content[0].text
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

        result = await handle_analyze_changes(Path("specs/requirements.md"), complex_description, Language.JAPANESE)

        text = result.content[0].text
        assert "変更影響分析" in text
        assert "REQ-06" in text
        assert "REQ-07" in text
        assert "REQ-08" in text

    @pytest.mark.asyncio
    async def test_handle_analyze_changes_empty_description(self):
        """Test analyze_changes handler with empty description."""
        result = await handle_analyze_changes(Path("specs/design.md"), "", Language.JAPANESE)

        text = result.content[0].text
        assert "変更影響分析" in text
        assert "design.md" in text

    @pytest.mark.asyncio
    async def test_handle_analyze_changes_different_file_types(self):
        """Test analyze_changes handler with different file types."""
        file_types = ["specs/requirements.md", "specs/design.md", "specs/tasks.md", "src/main.py", "docs/api.md"]

        for file_type in file_types:
            result = await handle_analyze_changes(
                Path(file_type), f"Modified {file_type} with updates", Language.JAPANESE
            )

            text = result.content[0].text
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
        specs = await SpecDocuments.from_paths(
            requirements_path=Path("nonexistent_req.md"),
            design_path=Path("nonexistent_design.md"),
            tasks_path=Path("nonexistent_tasks.md"),
        )
        result = await handle_get_traceability(specs)

        text = result.content[0].text
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

        specs = await SpecDocuments.from_paths(
            requirements_path=req_file, design_path=design_file, tasks_path=tasks_file, language=Language.JAPANESE
        )
        result = await handle_get_traceability(specs)

        text = result.content[0].text
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

        specs = await SpecDocuments.from_paths(
            requirements_path=req_file,
            design_path=Path("nonexistent_design.md"),
            tasks_path=Path("nonexistent_tasks.md"),
        )
        result = await handle_get_traceability(specs)

        text = result.content[0].text
        assert "トレーサビリティレポート" in text
        assert "要件数: 2" in text
