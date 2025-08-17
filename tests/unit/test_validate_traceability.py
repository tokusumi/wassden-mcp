"""Test traceability validation functionality."""

from wassden.lib import validate


class TestDesignTraceabilityValidation:
    """Test design validation with traceability checking."""

    def test_design_validation_with_complete_traceability(self):
        """Test design validation when all requirements are referenced."""
        requirements_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証機能を提供すること
- **REQ-02**: システムは、データ管理機能を提供すること
- **REQ-03**: システムは、レポート生成機能を提供すること
"""

        design_content = """
## アーキテクチャ概要
認証システムとデータ管理システムを実装する。

## コンポーネント設計
- **auth-service**: 認証サービス
- **data-service**: データ管理サービス
- **report-service**: レポート生成サービス

## データ設計
データ構造の定義

## API設計
API仕様

## 非機能設計
パフォーマンス設計

## テスト戦略
テスト計画

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **auth-service**
- REQ-02 ⇔ **data-service**
- REQ-03 ⇔ **report-service**
"""

        result = validate.validate_design(design_content, requirements_content)

        assert result["isValid"] is True
        assert result["stats"]["referencedRequirements"] == 3
        assert result["stats"]["missingReferences"] == []

    def test_design_validation_with_missing_references(self):
        """Test design validation when some requirements are not referenced."""
        requirements_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証機能を提供すること
- **REQ-02**: システムは、データ管理機能を提供すること
- **REQ-03**: システムは、レポート生成機能を提供すること
- **REQ-04**: システムは、監査機能を提供すること
"""

        design_content = """
## アーキテクチャ概要
認証システムとデータ管理システムを実装する。

## コンポーネント設計
- **auth-service**: 認証サービス
- **data-service**: データ管理サービス

## データ設計
データ構造の定義

## API設計
API仕様

## 非機能設計
パフォーマンス設計

## テスト戦略
テスト計画

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **auth-service**
- REQ-02 ⇔ **data-service**
"""

        result = validate.validate_design(design_content, requirements_content)

        assert result["isValid"] is False
        assert result["stats"]["referencedRequirements"] == 2
        assert set(result["stats"]["missingReferences"]) == {"REQ-03", "REQ-04"}
        assert any("Missing references to requirements:" in issue for issue in result["issues"])

    def test_design_validation_without_requirements(self):
        """Test design validation when no requirements content is provided."""
        design_content = """
## アーキテクチャ概要
システム設計

## コンポーネント設計
- **auth-service**: 認証サービス

## データ設計
データ構造の定義

## API設計
API仕様

## 非機能設計
パフォーマンス設計

## テスト戦略
テスト計画

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **auth-service**
- REQ-02 ⇔ **data-service**
"""

        result = validate.validate_design(design_content, None)

        assert result["isValid"] is True
        assert result["stats"]["referencedRequirements"] == 2
        assert result["stats"]["missingReferences"] == []


def test_design_validation_with_tr_references():
    """Test design validation with TR references in traceability section."""
    requirements_content = """
## 6. 機能要件（EARS）
- **REQ-01**: システムは、認証機能を提供すること

## 7. テスト要件（Testing Requirements）
- **TR-01**: 入力処理のテスト要件
- **TR-02**: 出力処理のテスト要件
"""

    design_content = """
## 1. アーキテクチャ概要
システム概要

## 2. コンポーネント設計
- **auth-service**: 認証サービス

## 3. データ設計
データ概要

## 4. API設計
API概要

## 5. 非機能設計
非機能概要

## 6. テスト戦略
- **test-input-processing**: 入力処理テスト
- **test-output-generation**: 出力処理テスト

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **auth-service**
- TR-01 ⇔ **test-input-processing**
- TR-02 ⇔ **test-output-generation**
"""

    result = validate.validate_design(design_content, requirements_content)
    assert result["isValid"] is True
    assert result["stats"]["referencedTRs"] == 2


def test_design_validation_missing_tr_references():
    """Test design validation when some TRs are not referenced."""
    requirements_content = """
## 6. 機能要件（EARS）
- **REQ-01**: システムは、認証機能を提供すること

## 7. テスト要件（Testing Requirements）
- **TR-01**: 入力処理のテスト要件
- **TR-02**: 出力処理のテスト要件
- **TR-03**: 統合テストのテスト要件
"""

    design_content = """
## 1. アーキテクチャ概要
システム概要

## 2. コンポーネント設計
- **auth-service**: 認証サービス

## 3. データ設計
データ概要

## 4. API設計
API概要

## 5. 非機能設計
非機能概要

## 6. テスト戦略
- **test-input-processing**: 入力処理テスト

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **auth-service**
- TR-01 ⇔ **test-input-processing**
"""

    result = validate.validate_design(design_content, requirements_content)
    assert result["isValid"] is False
    assert "TR-02" in str(result["stats"]["missingReferences"])
    assert "TR-03" in str(result["stats"]["missingReferences"])


class TestTasksTraceabilityValidation:
    """Test tasks validation with traceability checking."""

    def test_tasks_validation_with_requirement_references(self):
        """Test tasks validation with proper requirement references."""
        requirements_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証機能を提供すること
- **REQ-02**: システムは、データ管理機能を提供すること
"""

        design_content = """
## コンポーネント設計
- **auth-service**: 認証サービス
- **data-service**: データ管理サービス
"""

        tasks_content = """
## 概要
タスク概要

## タスク一覧
- **TASK-01-01**: 認証サービス実装 [REQ-01]
- **TASK-01-02**: データサービス実装 [REQ-02]
- **TASK-02-01**: auth-service テスト
- **TASK-02-02**: data-service テスト

## 依存関係
TASK-01-01 → TASK-02-01

## マイルストーン
- M1: Phase 1完了
"""

        result = validate.validate_tasks(tasks_content, requirements_content, design_content)

        assert result["isValid"] is True
        assert result["stats"]["totalTasks"] == 4
        assert result["stats"]["missingRequirementReferences"] == []
        assert result["stats"]["missingDesignReferences"] == []

    def test_tasks_validation_with_missing_requirement_references(self):
        """Test tasks validation when requirements are not referenced."""
        requirements_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証機能を提供すること
- **REQ-02**: システムは、データ管理機能を提供すること
- **REQ-03**: システムは、レポート機能を提供すること
- **REQ-04**: システムは、監査機能を提供すること
- **REQ-05**: システムは、バックアップ機能を提供すること
"""

        tasks_content = """
## 概要
タスク概要

## タスク一覧
- **TASK-01-01**: 認証サービス実装 [REQ-01]

## 依存関係
なし

## マイルストーン
- M1: Phase 1完了
"""

        result = validate.validate_tasks(tasks_content, requirements_content, None)

        assert result["isValid"] is False
        assert result["stats"]["totalTasks"] == 1
        assert len(result["stats"]["missingRequirementReferences"]) == 4  # REQ-02, REQ-03, REQ-04, REQ-05
        assert any("Requirements not referenced in tasks" in issue for issue in result["issues"])

    def test_tasks_validation_with_any_missing_requirements_should_warn(self):
        """Test tasks validation when any requirement is missing (100% coverage required)."""
        requirements_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証機能を提供すること
- **REQ-02**: システムは、データ管理機能を提供すること
- **REQ-03**: システムは、レポート機能を提供すること
- **REQ-04**: システムは、監査機能を提供すること
"""

        tasks_content = """
## 概要
タスク概要

## タスク一覧
- **TASK-01-01**: 認証サービス実装 [REQ-01]
- **TASK-01-02**: データサービス実装 [REQ-02]
- **TASK-01-03**: レポートサービス実装 [REQ-03]

## 依存関係
TASK-01-01 → TASK-01-02

## マイルストーン
- M1: Phase 1完了
"""

        result = validate.validate_tasks(tasks_content, requirements_content, None)

        # Should fail because 1 requirement is missing (100% coverage required)
        assert result["isValid"] is False
        assert result["stats"]["totalTasks"] == 3
        assert len(result["stats"]["missingRequirementReferences"]) == 1  # REQ-04
        assert any("Requirements not referenced in tasks" in issue for issue in result["issues"])

    def test_tasks_validation_with_missing_design_references(self):
        """Test tasks validation when design components are not referenced."""
        design_content = """
## コンポーネント設計
- **auth-service**: 認証サービス
- **data-service**: データ管理サービス
- **report-service**: レポートサービス
- **audit-service**: 監査サービス
"""

        tasks_content = """
## 概要
タスク概要

## タスク一覧
- **TASK-01-01**: auth-service実装

## 依存関係
なし

## マイルストーン
- M1: Phase 1完了
"""

        result = validate.validate_tasks(tasks_content, None, design_content)

        assert result["isValid"] is False
        assert result["stats"]["totalTasks"] == 1
        assert len(result["stats"]["missingDesignReferences"]) == 3  # data-service, report-service, audit-service
        assert any("Design components not referenced in tasks" in issue for issue in result["issues"])

    def test_tasks_validation_without_requirements_or_design(self):
        """Test tasks validation when no requirements or design content is provided."""
        tasks_content = """
## 概要
タスク概要

## タスク一覧
- **TASK-01-01**: 実装タスク
- **TASK-01-02**: テストタスク

## 依存関係
TASK-01-01 → TASK-01-02

## マイルストーン
- M1: Phase 1完了
"""

        result = validate.validate_tasks(tasks_content, None, None)

        assert result["isValid"] is True
        assert result["stats"]["totalTasks"] == 2
        assert result["stats"]["missingRequirementReferences"] == []
        assert result["stats"]["missingDesignReferences"] == []

    def test_tasks_validation_with_circular_dependency_and_traceability(self):
        """Test tasks validation with both circular dependency and traceability issues."""
        requirements_content = """
## 機能要件（EARS）
- **REQ-01**: システムは、認証機能を提供すること
- **REQ-02**: システムは、データ管理機能を提供すること
- **REQ-03**: システムは、レポート機能を提供すること
- **REQ-04**: システムは、監査機能を提供すること
- **REQ-05**: システムは、バックアップ機能を提供すること
"""

        tasks_content = """
## 概要
タスク概要

## タスク一覧
- **TASK-01-01**: 認証サービス実装
- **TASK-01-02**: データサービス実装

## 依存関係
TASK-01-01 依存: TASK-01-02
TASK-01-02 依存: TASK-01-01

## マイルストーン
- M1: Phase 1完了
"""

        result = validate.validate_tasks(tasks_content, requirements_content, None)

        assert result["isValid"] is False
        assert result["stats"]["totalTasks"] == 2

        # Should detect both circular dependency and missing requirement references
        issues = result["issues"]
        assert any("Circular dependency detected" in issue for issue in issues)
        assert any("Requirements not referenced in tasks" in issue for issue in issues)
