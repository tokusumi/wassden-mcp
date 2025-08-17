"""Pytest configuration and fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_requirements():
    """Sample requirements.md content."""
    return """# Requirements

## 0. サマリー
テストプロジェクトの要件定義書です。

## 1. 用語集
- **MCP**: Model Context Protocol

## 2. スコープ
### インスコープ
- 基本機能の実装

### アウトオブスコープ
- 高度な機能

## 3. 制約
- 技術的制約: Python 3.12以上

## 4. 非機能要件（NFR）
- **NFR-01**: レスポンス時間は1秒以内

## 5. KPI
- **KPI-01**: 全テストがパスすること

## 6. 機能要件（EARS）
- **REQ-01**: システムは、入力を受け付けること
- **REQ-02**: システムは、結果を出力すること
"""


@pytest.fixture
def sample_design():
    """Sample design.md content."""
    return """# Design

## 1. アーキテクチャ概要
モジュラーアーキテクチャを採用 [REQ-01, REQ-02]

## 2. コンポーネント設計
- **input-handler**: 入力処理 [REQ-01]
- **output-handler**: 出力処理 [REQ-02]

## 3. データモデル
```python
class Data:
    value: str
```

## 4. API（MCPツール）
- **process_input** → 入力を処理
- **generate_output** → 出力を生成

## 5. 非機能・品質
- **パフォーマンス**: 1秒以内のレスポンス [NFR-01]

## 6. テスト戦略
### 6.1 単体テスト
各コンポーネントの個別テスト

## 7. トレーサビリティ
REQ-01 ⇔ input-handler ⇔ TASK-01-01

## 8. リスクと対応
- **リスク1**: 性能要件未達 → 最適化実施
"""


@pytest.fixture
def sample_tasks():
    """Sample tasks.md content."""
    return """# Tasks

## 1. 概要
プロジェクトのタスク分解構造

## 2. タスク一覧
### Phase 1: 基盤構築
- **TASK-01-01**: 環境セットアップ (工数: 2h)
  - 詳細: 開発環境の構築
  - 関連: [REQ-01], [input-handler]
  - 依存: なし

- **TASK-01-02**: 基本構造作成 (工数: 4h)
  - 詳細: プロジェクト構造の作成
  - 関連: [REQ-02], [output-handler]
  - 依存: TASK-01-01

### Phase 2: 機能実装
- **TASK-02-01**: 入力処理実装 (工数: 8h)
  - 詳細: 入力ハンドラーの実装
  - 関連: [REQ-01]
  - 依存: TASK-01-02

## 3. 依存関係
TASK-01-01 → TASK-01-02 → TASK-02-01

## 4. マイルストーン
- **M1**: Phase 1完了
"""


@pytest.fixture
def incorrect_tasks():
    """Incomplete tasks.md content that will fail traceability validation."""
    return """# Tasks

## 1. 概要
プロジェクトのタスク分解構造

## 2. タスク一覧
### Phase 1: 基盤構築
- **TASK-01-01**: 環境セットアップ (工数: 2h)
  - 詳細: 開発環境の構築
  - 関連: [REQ-01], [input-handler]
  - 依存: なし

- **TASK-01-02**: 基本構造作成 (工数: 4h)
  - 詳細: プロジェクト構造の作成
  - 関連: [REQ-02], [output-handler]
  - 依存: TASK-01-01

### Phase 2: 機能実装
- **TASK-02-01**: 入力処理実装 (工数: 8h)
  - 詳細: 入力ハンドラーの実装
  - 関連: [REQ-01]
  - 依存: TASK-01-02

## 3. 依存関係
TASK-01-01 → TASK-01-02 → TASK-02-01

## 4. マイルストーン
- **M1**: Phase 1完了
"""


@pytest.fixture
def correct_tasks():
    """Complete tasks.md content that will pass 100% traceability validation."""
    return """# Tasks

## 1. 概要
プロジェクトのタスク分解構造

## 2. タスク一覧
### Phase 1: 基盤構築
- **TASK-01-01**: 環境セットアップ (工数: 2h)
  - 詳細: 開発環境の構築
  - 関連: [REQ-01], [input-handler]
  - 依存: なし

- **TASK-01-02**: 基本構造作成 (工数: 4h)
  - 詳細: プロジェクト構造の作成
  - 関連: [REQ-02], [output-handler]
  - 依存: TASK-01-01

### Phase 2: 機能実装
- **TASK-02-01**: 入力処理実装 (工数: 8h)
  - 詳細: 入力ハンドラーの実装
  - 関連: [REQ-01], [input-handler]
  - 依存: TASK-01-02

- **TASK-02-02**: 出力処理実装 (工数: 6h)
  - 詳細: 出力ハンドラーの実装
  - 関連: [REQ-02], [output-handler]
  - 依存: TASK-01-02

## 3. 依存関係
TASK-01-01 → TASK-01-02 → TASK-02-01
TASK-01-01 → TASK-01-02 → TASK-02-02

## 4. マイルストーン
- **M1**: Phase 1完了
- **M2**: Phase 2完了
"""


@pytest.fixture
def incorrect_requirements():
    """Invalid requirements.md content that will fail validation."""
    return """# Invalid Requirements

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


@pytest.fixture
def correct_requirements():
    """Complete requirements.md content that will pass validation."""
    return """# Requirements

## 0. サマリー
テストプロジェクトの要件定義書です。

## 1. 用語集
- **MCP**: Model Context Protocol

## 2. スコープ
### インスコープ
- 基本機能の実装

### アウトオブスコープ
- 高度な機能

## 3. 制約
- 技術的制約: Python 3.12以上

## 4. 非機能要件（NFR）
- **NFR-01**: レスポンス時間は1秒以内

## 5. KPI / 受入基準
- **KPI-01**: 全テストがパスすること

## 6. 機能要件（EARS）
- **REQ-01**: システムは、入力を受け付けること
- **REQ-02**: システムは、結果を出力すること
"""


@pytest.fixture
def incorrect_design():
    """Incomplete design.md content that will fail traceability validation."""
    return """# Design

## 1. アーキテクチャ概要
System design [REQ-01]

## 2. コンポーネント設計
- **component-a**: Function A [REQ-01]

## 3. データ設計
Data model

## 4. API設計
API endpoints

## 5. 非機能設計
NFR implementation

## 6. テスト戦略
Test plan
"""


@pytest.fixture
def correct_design():
    """Complete design.md content that will pass 100% traceability validation."""
    return """# Design

## 1. アーキテクチャ概要
モジュラーアーキテクチャを採用 [REQ-01, REQ-02]

## 2. コンポーネント設計
- **input-handler**: 入力処理 [REQ-01]
- **output-handler**: 出力処理 [REQ-02]

## 3. データモデル
```python
class Data:
    value: str
```

## 4. API（MCPツール）
- **process_input** → 入力を処理
- **generate_output** → 出力を生成

## 5. 非機能・品質
- **パフォーマンス**: 1秒以内のレスポンス [NFR-01]

## 6. テスト戦略
### 6.1 単体テスト
各コンポーネントの個別テスト

## 7. トレーサビリティ
REQ-01 ⇔ input-handler ⇔ TASK-01-01

## 8. リスクと対応
- **リスク1**: 性能要件未達 → 最適化実施
"""
