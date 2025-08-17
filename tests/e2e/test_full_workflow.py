"""End-to-end workflow tests."""

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
    handle_prompt_tasks,
    handle_validate_design,
    handle_validate_requirements,
    handle_validate_tasks,
)


class TestFullWorkflow:
    """Test complete end-to-end workflows."""

    @pytest.fixture(autouse=True)
    def setup_temp_workspace(self):
        """Set up temporary workspace for each test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.specs_dir = self.temp_dir / "specs"
        self.specs_dir.mkdir()

        # Change to temp directory for file operations
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

        yield

        # Cleanup
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_complete_sdd_workflow(self):
        """Test complete Spec-Driven Development workflow."""
        # Step 1-3: Completeness check, requirements creation and validation
        req_file = await self._test_requirements_phase()

        # Step 4-6: Design prompt, creation and validation
        design_file = await self._test_design_phase(req_file)

        # Step 7-9: Tasks prompt, creation and validation
        tasks_file = await self._test_tasks_phase(req_file, design_file)

        # Step 10-12: Implementation, traceability and change analysis
        await self._test_implementation_phase(req_file, design_file, tasks_file)

    async def _test_requirements_phase(self) -> Path:
        """Test requirements phase of workflow."""
        # Step 1: Check completeness with sufficient information
        completeness_result = await handle_check_completeness({"userInput": self._get_sample_user_input()})

        assert "content" in completeness_result
        completeness_text = completeness_result["content"][0]["text"]
        assert "requirements.md" in completeness_text
        assert "EARS" in completeness_text

        # Step 2: Create requirements manually
        requirements_content = self._get_sample_requirements()
        req_file = self.specs_dir / "requirements.md"
        req_file.write_text(requirements_content)

        # Step 3: Validate requirements
        validation_result = await handle_validate_requirements({"requirementsPath": str(req_file)})
        validation_text = validation_result["content"][0]["text"]
        assert "✅" in validation_text
        assert "要件数: 7" in validation_text

        return req_file

    async def _test_design_phase(self, req_file: Path) -> Path:
        """Test design phase of workflow."""
        # Step 4: Generate design prompt
        design_prompt_result = await handle_prompt_design({"requirementsPath": str(req_file)})
        design_prompt_text = design_prompt_result["content"][0]["text"]
        assert "design.md" in design_prompt_text
        assert "アーキテクチャ" in design_prompt_text

        # Step 5: Create design document
        design_content = self._get_sample_design()
        design_file = self.specs_dir / "design.md"
        design_file.write_text(design_content)

        # Step 6: Validate design
        design_validation_result = await handle_validate_design(
            {"designPath": str(design_file), "requirementsPath": str(req_file)}
        )
        design_validation_text = design_validation_result["content"][0]["text"]
        assert "✅" in design_validation_text
        assert "参照要件数: 7" in design_validation_text

        return design_file

    async def _test_tasks_phase(self, req_file: Path, design_file: Path) -> Path:
        """Test tasks phase of workflow."""
        # Step 7: Generate tasks prompt
        tasks_prompt_result = await handle_prompt_tasks(
            {"designPath": str(design_file), "requirementsPath": str(req_file)}
        )
        tasks_prompt_text = tasks_prompt_result["content"][0]["text"]
        assert "tasks.md" in tasks_prompt_text
        assert "WBS" in tasks_prompt_text

        # Step 8: Create tasks document
        tasks_content = self._get_sample_tasks()
        tasks_file = self.specs_dir / "tasks.md"
        tasks_file.write_text(tasks_content)

        # Step 9: Validate tasks
        tasks_validation_result = await handle_validate_tasks({"tasksPath": str(tasks_file)})
        tasks_validation_text = tasks_validation_result["content"][0]["text"]
        assert "✅" in tasks_validation_text
        assert "タスク数: 8" in tasks_validation_text

        return tasks_file

    async def _test_implementation_phase(self, req_file: Path, design_file: Path, tasks_file: Path) -> None:
        """Test implementation phase of workflow."""
        # Step 10: Generate implementation prompt
        code_prompt_result = await handle_prompt_code(
            {"tasksPath": str(tasks_file), "requirementsPath": str(req_file), "designPath": str(design_file)}
        )
        code_prompt_text = code_prompt_result["content"][0]["text"]
        assert "実装" in code_prompt_text
        assert "TASK-01-01" in code_prompt_text

        # Step 11: Get traceability report
        traceability_result = await handle_get_traceability(
            {"requirementsPath": str(req_file), "designPath": str(design_file), "tasksPath": str(tasks_file)}
        )
        traceability_text = traceability_result["content"][0]["text"]
        assert "トレーサビリティレポート" in traceability_text
        assert "要件数: 7" in traceability_text

        # Step 12: Analyze change impact
        change_analysis_result = await handle_analyze_changes(
            {"changedFile": str(req_file), "changeDescription": "Added REQ-08 for user profile management"}
        )
        change_analysis_text = change_analysis_result["content"][0]["text"]
        assert "変更影響分析" in change_analysis_text
        assert "REQ-08" in change_analysis_text

    def _get_sample_user_input(self) -> str:
        """Get sample user input for testing."""
        return """
        Python FastAPI RESTful API for task management.
        Technology: Python 3.12, FastAPI, SQLAlchemy, PostgreSQL
        Users: Project managers and team members
        Constraints: Must be cloud-deployable, response time < 1s
        Scope: CRUD operations for tasks, user authentication, basic reporting
        """

    def _get_sample_requirements(self) -> str:
        """Get sample requirements content for testing."""
        return """
# Requirements Document

## 0. サマリー
タスク管理用のPython FastAPI RESTful APIシステム。
プロジェクトマネージャーとチームメンバーが使用。
クラウド展開可能で1秒以内のレスポンス時間を実現。

## 1. 用語集
- **API**: Application Programming Interface
- **CRUD**: Create, Read, Update, Delete operations
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Python ORM

## 2. スコープ
### インスコープ
- タスクのCRUD操作
- ユーザー認証機能
- 基本的なレポート機能

### アウトオブスコープ
- 高度な分析機能
- リアルタイム通知
- モバイルアプリ

## 3. 制約
- Python 3.12以上使用
- FastAPI フレームワーク使用
- PostgreSQLデータベース使用
- クラウド展開可能であること
- レスポンス時間1秒以内

## 4. 非機能要件（NFR）
- **NFR-01**: APIレスポンス時間は1秒以内であること
- **NFR-02**: 同時接続100ユーザーまで対応すること
- **NFR-03**: データは暗号化して保存すること
- **NFR-04**: APIドキュメントが自動生成されること
- **NFR-05**: 99%以上の稼働率を維持すること

## 5. KPI / 受入基準
- **KPI-01**: API応答時間平均500ms以下
- **KPI-02**: システム稼働率99%以上
- **KPI-03**: ユーザー満足度4.0/5.0以上

## 6. 機能要件（EARS）
- **REQ-01**: システムは、認証されたユーザーがタスクを作成すること
- **REQ-02**: システムは、認証されたユーザーがタスク一覧を取得すること
- **REQ-03**: システムは、認証されたユーザーがタスクを更新すること
- **REQ-04**: システムは、認証されたユーザーがタスクを削除すること
- **REQ-05**: システムは、ユーザーがログインできること
- **REQ-06**: システムは、ユーザーがログアウトできること
- **REQ-07**: システムは、基本的なタスク統計を提供すること
"""

    def _get_sample_design(self) -> str:
        """Get sample design content for testing."""
        return """
# Design Document

## 1. アーキテクチャ概要
RESTful API アーキテクチャを採用したタスク管理システム
[Requirements: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07]

## 2. コンポーネント設計
- **auth-service**: ユーザー認証処理 [REQ-05, REQ-06]
- **task-service**: タスクCRUD操作 [REQ-01, REQ-02, REQ-03, REQ-04]
- **stats-service**: 統計情報提供 [REQ-07]
- **database-layer**: データ永続化層
- **api-gateway**: APIエンドポイント管理

## 3. データ設計
```python
class User:
    id: int
    username: str
    email: str
    hashed_password: str

class Task:
    id: int
    title: str
    description: str
    status: str
    user_id: int
    created_at: datetime
    updated_at: datetime
```

## 4. API設計
- **POST /auth/login** → ユーザーログイン [REQ-05]
- **POST /auth/logout** → ユーザーログアウト [REQ-06]
- **POST /tasks** → タスク作成 [REQ-01]
- **GET /tasks** → タスク一覧取得 [REQ-02]
- **PUT /tasks/{id}** → タスク更新 [REQ-03]
- **DELETE /tasks/{id}** → タスク削除 [REQ-04]
- **GET /stats** → 統計情報取得 [REQ-07]

## 5. 非機能設計
- **パフォーマンス**: FastAPIとasync/awaitでレスポンス時間最適化
- **セキュリティ**: JWT認証、パスワードハッシュ化
- **可用性**: ヘルスチェックエンドポイント実装
- **ドキュメント**: FastAPIの自動ドキュメント生成

## 6. テスト戦略
### 6.1 単体テスト
各サービスクラスの個別テスト

### 6.2 統合テスト
API エンドポイントのテスト

### 6.3 E2Eテスト
完全なワークフローテスト
"""

    def _get_sample_tasks(self) -> str:
        """Get sample tasks content for testing."""
        return """
# Tasks Document

## 1. 概要
FastAPI タスク管理システムのWBS（Work Breakdown Structure）

## 2. タスク一覧
### Phase 1: 基盤構築
- **TASK-01-01**: 環境セットアップ (工数: 4h)
  - 詳細: Python、FastAPI、PostgreSQL環境構築
  - 関連: [NFR-04], [database-layer]
  - 依存: なし

- **TASK-01-02**: データベース設計実装 (工数: 6h)
  - 詳細: SQLAlchemyモデル定義、マイグレーション
  - 関連: [REQ-01, REQ-02, REQ-03, REQ-04], [database-layer]
  - 依存: TASK-01-01

### Phase 2: 認証機能実装
- **TASK-02-01**: ユーザー認証システム (工数: 8h)
  - 詳細: JWT認証、パスワードハッシュ化実装
  - 関連: [REQ-05, REQ-06], [auth-service]
  - 依存: TASK-01-02

### Phase 3: コア機能実装
- **TASK-03-01**: タスクCRUD API (工数: 12h)
  - 詳細: タスク作成、取得、更新、削除エンドポイント
  - 関連: [REQ-01, REQ-02, REQ-03, REQ-04], [task-service]
  - 依存: TASK-02-01

- **TASK-03-02**: 統計情報API (工数: 4h)
  - 詳細: タスク統計情報提供エンドポイント
  - 関連: [REQ-07], [stats-service]
  - 依存: TASK-03-01

- **TASK-03-03**: API Gateway 設定 (工数: 3h)
  - 詳細: APIエンドポイント管理・ルーティング設定
  - 関連: [api-gateway]
  - 依存: TASK-03-01

### Phase 4: テスト・品質保証
- **TASK-04-01**: 単体テスト作成 (工数: 8h)
  - 詳細: 各サービスの単体テスト
  - 関連: [全REQ]
  - 依存: TASK-03-03

- **TASK-04-02**: 統合テスト作成 (工数: 6h)
  - 詳細: APIエンドポイントの統合テスト
  - 関連: [NFR-01, NFR-05]
  - 依存: TASK-04-01

## 3. 依存関係
```
TASK-01-01 → TASK-01-02 → TASK-02-01 → TASK-03-01 → TASK-03-02 → TASK-04-01 → TASK-04-02
```

## 4. マイルストーン
- **M1**: Phase 1完了 (環境・基盤整備完了)
- **M2**: Phase 2完了 (認証機能完了)
- **M3**: Phase 3完了 (コア機能完了)
- **M4**: リリース準備完了 (テスト・品質保証完了)
"""

    @pytest.mark.asyncio
    async def test_incomplete_input_workflow(self):
        """Test workflow with incomplete user input."""
        # Step 1: Check completeness with insufficient information
        completeness_result = await handle_check_completeness({"userInput": "Simple project"})

        completeness_text = completeness_result["content"][0]["text"]

        # Should ask for more information
        assert "不足している" in completeness_text or "不明" in completeness_text
        assert "技術" in completeness_text or "ユーザー" in completeness_text

        # Should provide questions to clarify requirements
        question_indicators = ["？", "ですか", "何で", "誰で", "どの"]
        assert any(indicator in completeness_text for indicator in question_indicators)

    @pytest.mark.asyncio
    async def test_validation_failure_workflow(self):
        """Test workflow with validation failures."""
        # Create invalid requirements file
        invalid_requirements = """
# Invalid Requirements

## 0. サマリー
Missing required sections and invalid IDs

## 1. 用語集
- **Term**: Definition

## 2. スコープ
Project scope

## 3. 制約
Constraints

## 4. 非機能要件（NFR）
- **NFR-01**: Performance requirement

## 5. KPI / 受入基準
- **KPI-01**: Success metric

## 6. 機能要件（EARS）
- **REQ-001**: Invalid ID format (should be REQ-XX)
- **REQ-1**: Also invalid format
- **INVALID-01**: Wrong prefix
"""

        req_file = self.specs_dir / "requirements.md"
        req_file.write_text(invalid_requirements)

        # Validate requirements - should fail
        validation_result = await handle_validate_requirements({"requirementsPath": str(req_file)})

        validation_text = validation_result["content"][0]["text"]
        assert "⚠️" in validation_text or "修正が必要" in validation_text
        assert "REQ-001" in validation_text  # Should detect invalid format
        assert "REQ-1" in validation_text
        assert "INVALID-01" in validation_text

    @pytest.mark.asyncio
    async def test_traceability_gaps_workflow(self):
        """Test workflow with traceability gaps."""
        # Create requirements with REQ-01, REQ-02, REQ-03
        requirements_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、機能Aを提供すること
- **REQ-02**: システムは、機能Bを提供すること
- **REQ-03**: システムは、機能Cを提供すること
"""

        # Create design that only references REQ-01 and REQ-02
        design_content = """
## アーキテクチャ概要
System design [REQ-01, REQ-02]

## コンポーネント設計
- **component-a**: Function A [REQ-01]
- **component-b**: Function B [REQ-02]

## データ設計
Data model

## API設計
API endpoints

## 非機能設計
NFR implementation

## テスト戦略
Test plan
"""

        req_file = self.specs_dir / "requirements.md"
        design_file = self.specs_dir / "design.md"

        req_file.write_text(requirements_content)
        design_file.write_text(design_content)

        # Validate design - should detect missing REQ-03
        design_validation_result = await handle_validate_design(
            {"designPath": str(design_file), "requirementsPath": str(req_file)}
        )

        validation_text = design_validation_result["content"][0]["text"]
        assert "⚠️" in validation_text or "修正が必要" in validation_text
        assert "REQ-03" in validation_text  # Should detect missing reference

        # Get traceability report to show gaps
        traceability_result = await handle_get_traceability(
            {
                "requirementsPath": str(req_file),
                "designPath": str(design_file),
                "tasksPath": "nonexistent.md",  # Optional file
            }
        )

        traceability_text = traceability_result["content"][0]["text"]
        assert "設計されていない要件" in traceability_text or "設計参照なし" in traceability_text


class TestWorkflowErrorHandling:
    """Test error handling in workflows."""

    @pytest.fixture(autouse=True)
    def setup_temp_workspace(self):
        """Set up temporary workspace."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.original_cwd = Path.cwd()
        os.chdir(self.temp_dir)

        yield

        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_missing_files_workflow(self):
        """Test workflow with missing prerequisite files."""
        # Try to validate requirements when file doesn't exist
        validation_result = await handle_validate_requirements({"requirementsPath": "nonexistent/requirements.md"})

        validation_text = validation_result["content"][0]["text"]
        assert "エラー" in validation_text
        assert "見つかりません" in validation_text

        # Try to generate design prompt when requirements don't exist
        design_prompt_result = await handle_prompt_design({"requirementsPath": "nonexistent/requirements.md"})

        design_text = design_prompt_result["content"][0]["text"]
        assert "エラー" in design_text

    @pytest.mark.asyncio
    async def test_corrupted_files_workflow(self):
        """Test workflow with corrupted/malformed files."""
        # Create corrupted requirements file
        specs_dir = Path("specs")
        specs_dir.mkdir(exist_ok=True)

        corrupted_file = specs_dir / "requirements.md"
        corrupted_file.write_text("Completely invalid content with no structure")

        # Validation should handle corrupted files gracefully
        validation_result = await handle_validate_requirements({"requirementsPath": str(corrupted_file)})

        validation_text = validation_result["content"][0]["text"]
        # Should either show validation errors or handle gracefully
        assert "修正" in validation_text or "エラー" in validation_text
