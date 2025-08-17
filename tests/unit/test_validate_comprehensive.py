"""Comprehensive unit tests for validation functions."""

from wassden.lib import validate


class TestValidateReqId:
    """Test requirement ID validation comprehensively."""

    def test_valid_req_ids(self):
        """Test valid REQ-ID formats."""
        valid_ids = ["REQ-01", "REQ-02", "REQ-10", "REQ-99"]
        for req_id in valid_ids:
            assert validate.validate_req_id(req_id), f"{req_id} should be valid"

    def test_invalid_req_ids(self):
        """Test invalid REQ-ID formats."""
        invalid_ids = [
            "REQ-1",  # Single digit
            "REQ-001",  # Three digits
            "REQ-100",  # Three digits
            "REQ01",  # No hyphen
            "REQ-",  # No digits
            "req-01",  # Lowercase
            "TASK-01",  # Wrong prefix
            "REQ-AB",  # Letters instead of numbers
            "REQ-1a",  # Mixed alphanumeric
            "",  # Empty string
            "REQ",  # No hyphen or digits
            "REQ-00",  # Zero padding issues
        ]
        for req_id in invalid_ids:
            assert not validate.validate_req_id(req_id), f"{req_id} should be invalid"


class TestValidateTaskId:
    """Test task ID validation comprehensively."""

    def test_valid_task_ids(self):
        """Test valid TASK-ID formats."""
        valid_ids = [
            "TASK-01-01",  # Standard format
            "TASK-01-02",  # Different numbers
            "TASK-10-20",  # Higher numbers
            "TASK-99-99",  # Max numbers
            "TASK-01-01-01",  # Three levels
            "TASK-01-01-02",  # Three levels different
            "TASK-05-10-15",  # Three levels higher
        ]
        for task_id in valid_ids:
            assert validate.validate_task_id(task_id), f"{task_id} should be valid"

    def test_invalid_task_ids(self):
        """Test invalid TASK-ID formats."""
        invalid_ids = [
            "TASK-01",  # Only one level
            "TASK-1-01",  # Single digit first
            "TASK-01-1",  # Single digit second
            "TASK-001-01",  # Three digits
            "TASK-01-001",  # Three digits
            "TASK01-01",  # No first hyphen
            "TASK-01.01",  # Dot instead of hyphen
            "task-01-01",  # Lowercase
            "TASK-01-01-01-01",  # Four levels
            "TASK-AB-01",  # Letters
            "TASK--01",  # Double hyphen
            "",  # Empty
            "TASK",  # Just prefix
        ]
        for task_id in invalid_ids:
            assert not validate.validate_task_id(task_id), f"{task_id} should be invalid"


class TestRequirementsValidation:
    """Test requirements document validation."""

    def test_valid_requirements_document(self):
        """Test validation of properly structured requirements."""
        content = """
# Requirements Document

## 0. サマリー
テストプロジェクトです。

## 1. 用語集
- **MCP**: Model Context Protocol

## 2. スコープ
### インスコープ
- 基本機能

### アウトオブスコープ
- 高度機能

## 3. 制約
- Python 3.12以上

## 4. 非機能要件（NFR）
- **NFR-01**: 性能要件

## 5. KPI / 受入基準
- **KPI-01**: 成功指標

## 6. 機能要件（EARS）
- **REQ-01**: システムは、入力を受け付けること
- **REQ-02**: システムは、出力を提供すること

## 7. テスト要件（Testing Requirements）
- **TR-01**: 入力テスト要件
- **TR-02**: 出力テスト要件
"""

        errors = validate.validate_requirements_structure(content)
        assert len(errors) == 0, f"Expected no errors but got: {errors}"

    def test_missing_sections(self):
        """Test detection of missing sections."""
        content = """
# Requirements Document

## 0. サマリー
テストプロジェクトです。

## 6. 機能要件（EARS）
- **REQ-01**: システムは、入力を受け付けること
"""

        errors = validate.validate_requirements_structure(content)

        # Should detect missing sections
        expected_missing = ["用語集", "スコープ", "制約", "非機能要件", "KPI"]
        for section in expected_missing:
            assert any(section in error for error in errors), f"Should detect missing {section}"

    def test_duplicate_req_ids(self):
        """Test detection of duplicate REQ-IDs."""
        content = """
## 6. 機能要件（EARS）
- **REQ-01**: システムは、入力を受け付けること
- **REQ-02**: システムは、処理すること
- **REQ-01**: システムは、重複IDテスト
"""

        errors = validate.validate_requirements_structure(content)
        assert any("Duplicate REQ-IDs" in error for error in errors)

    def test_invalid_req_id_format(self):
        """Test detection of invalid REQ-ID format."""
        content = """
## 6. 機能要件（EARS）
- **REQ-001**: システムは、無効なIDフォーマット
- **REQ-1**: システムは、短いID
- **INVALID-01**: システムは、間違ったプレフィックス
"""

        errors = validate.validate_requirements_structure(content)

        invalid_ids = ["REQ-001", "REQ-1", "INVALID-01"]
        for invalid_id in invalid_ids:
            assert any(invalid_id in error for error in errors), f"Should detect invalid {invalid_id}"


class TestDesignValidation:
    """Test design document validation."""

    def test_valid_design_document(self):
        """Test validation of properly structured design."""
        content = """
# Design Document

## 1. アーキテクチャ概要
システム設計 [REQ-01, REQ-02]

## 2. コンポーネント設計
- **input-handler**: 入力処理 [REQ-01]

## 3. データモデル
データ構造定義

## 4. API設計
API仕様

## 5. 非機能設計
性能設計

## 6. テスト戦略
テスト計画
"""

        errors = validate.validate_design_structure(content)
        assert len(errors) == 0, f"Expected no errors but got: {errors}"

    def test_design_missing_req_references(self):
        """Test detection of missing REQ-ID references."""
        content = """
# Design Document

## 1. アーキテクチャ概要
システム設計（REQ-IDなし）

## 2. コンポーネント設計
- **component**: 説明のみ
"""

        errors = validate.validate_design_structure(content)
        assert any("REQ-ID" in error for error in errors)

    def test_design_missing_sections(self):
        """Test detection of missing design sections."""
        content = """
# Design Document

## 1. アーキテクチャ概要
REQ-01の説明
"""

        errors = validate.validate_design_structure(content)

        expected_sections = ["コンポーネント設計", "データ", "API", "非機能", "テスト"]
        sum(1 for section in expected_sections if not any(section in content for section in [content]))
        assert len(errors) > 0


class TestTasksValidation:
    """Test tasks document validation."""

    def test_valid_tasks_document(self):
        """Test validation of properly structured tasks."""
        content = """
# Tasks Document

## 1. 概要
タスク概要

## 2. タスク一覧
- **TASK-01-01**: 環境構築
- **TASK-01-02**: 基本実装
- **TASK-02-01**: 機能実装

## 3. 依存関係
TASK-01-01 → TASK-01-02

## 4. マイルストーン
- M1: Phase 1完了
"""

        errors = validate.validate_tasks_structure(content)
        assert len(errors) == 0, f"Expected no errors but got: {errors}"

    def test_tasks_duplicate_ids(self):
        """Test detection of duplicate task IDs."""
        content = """
## 2. タスク一覧
- **TASK-01-01**: 最初のタスク
- **TASK-01-02**: 2番目のタスク
- **TASK-01-01**: 重複タスク
"""

        errors = validate.validate_tasks_structure(content)
        assert any("Duplicate TASK-IDs" in error for error in errors)

    def test_tasks_invalid_format(self):
        """Test detection of invalid task ID format."""
        content = """
## 2. タスク一覧
- **TASK-1-01**: 無効フォーマット1
- **TASK-01-1**: 無効フォーマット2
- **INVALID-01-01**: 間違ったプレフィックス
"""

        errors = validate.validate_tasks_structure(content)

        invalid_ids = ["TASK-1-01", "TASK-01-1", "INVALID-01-01"]
        for invalid_id in invalid_ids:
            assert any(invalid_id in error for error in errors), f"Should detect invalid {invalid_id}"


class TestCompleteValidation:
    """Test complete validation functions."""

    def test_validate_requirements_complete(self):
        """Test complete requirements validation with stats."""
        content = """
## 0. サマリー
テスト

## 1. 用語集
- **MCP**: Protocol

## 2. スコープ
### インスコープ
- 機能A

## 3. 制約
- 制約A

## 4. 非機能要件（NFR）
- **NFR-01**: 性能
- **NFR-02**: セキュリティ

## 5. KPI
- **KPI-01**: 指標1
- **KPI-02**: 指標2
- **KPI-03**: 指標3

## 6. 機能要件（EARS）
- **REQ-01**: システムは機能Aを提供すること
- **REQ-02**: システムは機能Bを提供すること
- **REQ-03**: システムは機能Cを提供すること
- **REQ-04**: システムは機能Dを提供すること

## 7. テスト要件（Testing Requirements）
- **TR-01**: テスト要件A
- **TR-02**: テスト要件B
"""

        result = validate.validate_requirements(content)

        assert result["isValid"] is True
        assert result["stats"]["totalRequirements"] == 4
        assert result["stats"]["totalNFRs"] == 2
        assert result["stats"]["totalKPIs"] == 3
        assert len(result["foundSections"]) == 8

    def test_validate_design_with_traceability(self):
        """Test design validation with traceability checking."""
        design_content = """
## アーキテクチャ概要
Design overview

## コンポーネント設計
Components

## データ設計
Data model

## API設計
API spec

## 非機能設計
NFR implementation

## テスト戦略
Test plan

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **component-a**
- REQ-02 ⇔ **component-b**
- REQ-03 ⇔ **component-c**
"""

        requirements_content = """
## 機能要件
- **REQ-01**: First requirement
- **REQ-02**: Second requirement
- **REQ-03**: Third requirement
- **REQ-04**: Fourth requirement (not referenced)
"""

        result = validate.validate_design(design_content, requirements_content)

        assert result["isValid"] is False  # Should fail due to missing REQ-04 reference
        assert result["stats"]["referencedRequirements"] == 3
        assert "REQ-04" in result["stats"]["missingReferences"]

    def test_validate_tasks_with_dependencies(self):
        """Test tasks validation with dependency checking."""
        content = """
## 概要
Tasks overview

## タスク一覧
- **TASK-01-01**: First task
- **TASK-01-02**: Second task
- **TASK-02-01**: Third task

## 依存関係
Dependencies listed

## マイルストーン
Milestones defined
"""

        result = validate.validate_tasks(content)

        assert result["isValid"] is True
        assert result["stats"]["totalTasks"] == 3
        assert result["stats"]["dependencies"] >= 0
