"""Pytest configuration and fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest


def pytest_collection_modifyitems(config, items):
    """Skip dev-only tests when running in core mode."""
    # Check if we're running with "-m 'not dev'" filter
    markexpr = config.getoption("-m", default="")
    if "not dev" in markexpr:
        # Remove items that have dev marker
        items[:] = [item for item in items if "dev" not in [mark.name for mark in item.iter_markers()]]


def pytest_ignore_collect(collection_path, config):
    """Completely ignore dev-only test files when running in core mode."""
    # Check if we're running with "-m 'not dev'" filter
    markexpr = config.getoption("-m", default="")
    if "not dev" in markexpr:
        # List of files that require dev dependencies
        dev_only_files = [
            "test_experiment_api.py",
            "test_experiment_cli.py",
            "test_experiment_cli_async.py",
            "test_experiment_cli_concurrent.py",
            "test_experiment_manager.py",
            "test_experiment_integration.py",
            "test_experiment_e2e.py",
            "test_comparative_analyzer.py",
            "test_ears_analyzer.py",
            "test_language_detector_analyzer.py",
            "test_output_formatter.py",
            "test_performance_profiler.py",
            "test_statistics_engine.py",
            "test_cli_detailed.py",
            "test_dev_gate.py",
        ]

        if collection_path.name in dev_only_files:
            return True
    return False


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
- **背景/目的**: テストプロジェクトの要件定義書です。
- **対象ユーザー/主要シナリオ**: 開発者がシステムをテストする場合

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
  - 受け入れ観点1: 入力が正常に処理される
  - 受け入れ観点2: エラー時は適切なメッセージを表示する
- **REQ-02**: システムは、結果を出力すること
  - 受け入れ観点1: 正しい形式で出力される
  - 受け入れ観点2: 出力が完全である

## 7. テスト要件（Testing Requirements）
- **TR-01**: 入力処理のテスト要件
- **TR-02**: 出力処理のテスト要件
"""


@pytest.fixture
def sample_design():
    """Sample design.md content."""
    return """# Design

## 1. アーキテクチャ概要
- **コンテキスト/依存関係/制約**: モジュラーアーキテクチャを採用
- **全体図**: 入力処理→データ変換→出力処理のフロー
[Requirements: REQ-01, REQ-02]

## 2. コンポーネント設計
- **input-handler**:
  - **役割**: 入力データの受信と前処理
  - **要件**: [REQ-01]
  - **入出力**: String input → Parsed data
  - **例外・リトライ**: 不正入力時はエラーレスポンス
  - **可観測性**: 入力処理ログとメトリクス

- **output-handler**:
  - **役割**: 処理結果の生成と出力
  - **要件**: [REQ-02]
  - **入出力**: Processed data → String output
  - **例外・リトライ**: 出力失敗時は再試行
  - **可観測性**: 出力処理ログとメトリクス

## 3. データモデル
```python
class Data:
    value: str
```

## 4. API/インターフェース
- **process_input**:
  - **概要**: 入力データを処理するAPI
  - **エンドポイント**: /api/process
  - **リクエスト/レスポンス**: JSON形式
  - **エラー**: 400/500エラーコード
  - **モジュール境界**: input-handler担当

- **generate_output**:
  - **概要**: 出力データを生成するAPI
  - **エンドポイント**: /api/output
  - **リクエスト/レスポンス**: JSON形式
  - **エラー**: 400/500エラーコード
  - **モジュール境界**: output-handler担当

## 5. 非機能・品質
- **パフォーマンス**: 1秒以内のレスポンス [NFR-01]
- **セキュリティ**: 入力値検証とサニタイズ
- **可用性**: 99%以上の稼働率

## 6. テスト戦略
- **単体/結合/E2E の役割分担**: 各レベルでの検証内容
- **test-input-processing**: 入力処理の重要なテストケース
  - **テストデータ方針**: 正常系・異常系のテストデータ準備
  - **観測可能な合否基準**: 入力が正しく処理され出力される
- **test-output-generation**: 出力処理の重要なテストケース
  - **テストデータ方針**: 様々な出力形式のテスト
  - **観測可能な合否基準**: 出力が正しい形式で生成される

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **input-handler**
- REQ-02 ⇔ **output-handler**
- TR-01 ⇔ **test-input-processing**
- TR-02 ⇔ **test-output-generation**

## 8. フロー設計
- **主要シーケンス**: 入力受信→検証→処理→出力生成
- **状態遷移**: IDLE→PROCESSING→COMPLETE
- **バックプレッシャー/キュー処理**: リクエスト待ち行列制御

## 9. 障害・エッジケース
- **フェイルパターン**: 入力不正、処理タイムアウト
- **フォールバック**: デフォルト値での処理継続
- **タイムアウト/リトライ方針**: 3秒タイムアウト、3回リトライ

## 10. セキュリティ & コンプライアンス
- **認証/認可**: APIキーベース認証
- **データ保護**: 入力データの暗号化
- **監査ログ**: 全処理のログ記録
- **秘密管理**: 環境変数での管理

## 11. リスクと対応 (Optional)
- **リスク1**: 性能要件未達 → 最適化実施
"""


@pytest.fixture
def sample_tasks():
    """Sample tasks.md content."""
    return """# Tasks

## 1. 概要
プロジェクトのタスク分解構造

## 2. タスク一覧
### Phase 1: Foundation
- [ ] **TASK-01-01**: 環境セットアップ
  - **REQ**: [REQ-01]
  - **DC**: **input-handler**
  - **依存**: なし
  - **受け入れ観点**:
    - 観点1: 開発環境が正常に構築される
    - 観点2: 必要なライブラリが全てインストールされる

- [ ] **TASK-01-02**: 基本構造作成
  - **REQ**: [REQ-02]
  - **DC**: **output-handler**
  - **依存**: TASK-01-01
  - **受け入れ観点**:
    - 観点1: プロジェクト構造が正しく作成される
    - 観点2: 設定ファイルが適切に配置される

### Phase 2: Implementation
- [ ] **TASK-02-01**: 入力処理実装
  - **REQ**: [REQ-01]
  - **DC**: **input-handler**, **process_input**
  - **依存**: TASK-01-02
  - **受け入れ観点**:
    - 観点1: 入力データが正しく処理される
    - 観点2: エラーハンドリングが適切に動作する

- [ ] **TASK-02-02**: 出力処理実装
  - **REQ**: [REQ-02]
  - **DC**: **output-handler**, **generate_output**
  - **依存**: TASK-01-02
  - **受け入れ観点**:
    - 観点1: 出力データが正しく生成される
    - 観点2: フォーマットが仕様に適合する

### Phase 3: Testing
- [ ] **TASK-03-01**: テストケース実装
  - **REQ**: [TR-01]
  - **DC**: **test-input-processing**
  - **依存**: TASK-02-01
  - **受け入れ観点**:
    - 観点1: 全テストケースが実装される
    - 観点2: テストが正常に実行される

- [ ] **TASK-03-02**: 出力テスト実装
  - **REQ**: [TR-02]
  - **DC**: **test-output-generation**
  - **依存**: TASK-02-02
  - **受け入れ観点**:
    - 観点1: 出力テストが完全に実装される
    - 観点2: 全ての出力パターンがテストされる

## 3. 依存関係
```
TASK-01-01 → TASK-01-02 → TASK-02-01 → TASK-03-01
TASK-01-01 → TASK-01-02 → TASK-02-02 → TASK-03-02
```

## 4. マイルストーン
- **M1**: Phase 1 completion (Phase 1完了)
- **M2**: Phase 2 completion (Phase 2完了)

## 5. リスクと対策
- **リスク**: 環境構築の遅延
  - 影響タスク: TASK-01-01
  - 対策: 事前準備とドキュメント整備
"""


@pytest.fixture
def incorrect_tasks():
    """Incomplete tasks.md content that will fail traceability validation."""
    return """# Tasks

## 1. 概要
プロジェクトのタスク分解構造

## 2. タスク一覧
### Phase 1: Foundation
- [ ] **TASK-01-01**: 環境セットアップ
  - **REQ**: [REQ-01]
  - **DC**: **input-handler**
  - **依存**: なし
  - **受け入れ観点**:
    - 観点1: 開発環境が正常に構築される

- [ ] **TASK-01-02**: 基本構造作成
  - **REQ**: [REQ-02]
  - **DC**: **output-handler**
  - **依存**: TASK-01-01
  - **受け入れ観点**:
    - 観点1: プロジェクト構造が正しく作成される

### Phase 2: Implementation
- [ ] **TASK-02-01**: 入力処理実装
  - **REQ**: [REQ-01]
  - **DC**: **input-handler**
  - **依存**: TASK-01-02
  - **受け入れ観点**:
    - 観点1: 入力データが正しく処理される

## 3. 依存関係
```
TASK-01-01 → TASK-01-02 → TASK-02-01
```

## 4. マイルストーン
- **M1**: Phase 1 completion (Phase 1完了)
"""


@pytest.fixture
def correct_tasks():
    """Complete tasks.md content that will pass 100% traceability validation."""
    return """# Tasks

## 1. 概要
プロジェクトのタスク分解構造

## 2. タスク一覧
### Phase 1: Foundation
- [ ] **TASK-01-01**: 環境セットアップ
  - **REQ**: [REQ-01]
  - **DC**: **input-handler**
  - **依存**: なし
  - **受け入れ観点**:
    - 観点1: 開発環境が正常に構築される
    - 観点2: 必要なライブラリが全てインストールされる

- [ ] **TASK-01-02**: 基本構造作成
  - **REQ**: [REQ-02]
  - **DC**: **output-handler**
  - **依存**: TASK-01-01
  - **受け入れ観点**:
    - 観点1: プロジェクト構造が正しく作成される
    - 観点2: 設定ファイルが適切に配置される

### Phase 2: Implementation
- [ ] **TASK-02-01**: 入力処理実装
  - **REQ**: [REQ-01]
  - **DC**: **input-handler**, **process_input**
  - **依存**: TASK-01-02
  - **受け入れ観点**:
    - 観点1: 入力データが正しく処理される
    - 観点2: エラーハンドリングが適切に動作する

- [ ] **TASK-02-02**: 出力処理実装
  - **REQ**: [REQ-02]
  - **DC**: **output-handler**, **generate_output**
  - **依存**: TASK-01-02
  - **受け入れ観点**:
    - 観点1: 出力データが正しく生成される
    - 観点2: フォーマットが仕様に適合する

### Phase 3: Testing
- [ ] **TASK-03-01**: テストケース実装
  - **REQ**: [TR-01]
  - **DC**: **test-input-processing**
  - **依存**: TASK-02-01
  - **受け入れ観点**:
    - 観点1: 全テストケースが実装される
    - 観点2: テストが正常に実行される

- [ ] **TASK-03-02**: 出力テスト実装
  - **REQ**: [TR-02]
  - **DC**: **test-output-generation**
  - **依存**: TASK-02-02
  - **受け入れ観点**:
    - 観点1: 出力テストが完全に実装される
    - 観点2: 全ての出力パターンがテストされる

## 3. 依存関係
```
TASK-01-01 → TASK-01-02 → TASK-02-01 → TASK-03-01
TASK-01-01 → TASK-01-02 → TASK-02-02 → TASK-03-02
```

## 4. マイルストーン
- **M1**: Phase 1 completion (Phase 1完了)
- **M2**: Phase 2 completion (Phase 2完了)
- **M3**: Phase 3 completion (Phase 3完了)

## 5. リスクと対策
- **リスク**: 環境構築の遅延
  - 影響タスク: TASK-01-01
  - 対策: 事前準備とドキュメント整備
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
- **背景/目的**: テストプロジェクトの要件定義書です。
- **対象ユーザー/主要シナリオ**: 開発者がシステムをテストする場合

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
  - 受け入れ観点1: 入力が正常に処理される
  - 受け入れ観点2: エラー時は適切なメッセージを表示する
- **REQ-02**: システムは、結果を出力すること
  - 受け入れ観点1: 正しい形式で出力される
  - 受け入れ観点2: 出力が完全である

## 7. テスト要件（Testing Requirements）
- **TR-01**: 入力処理のテスト要件
- **TR-02**: 出力処理のテスト要件
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
- **コンテキスト/依存関係/制約**: モジュラーアーキテクチャを採用
- **全体図**: 入力処理→データ変換→出力処理のフロー
[Requirements: REQ-01, REQ-02]

## 2. コンポーネント設計
- **input-handler**:
  - **役割**: 入力データの受信と前処理
  - **要件**: [REQ-01]
  - **入出力**: String input → Parsed data
  - **例外・リトライ**: 不正入力時はエラーレスポンス
  - **可観測性**: 入力処理ログとメトリクス

- **output-handler**:
  - **役割**: 処理結果の生成と出力
  - **要件**: [REQ-02]
  - **入出力**: Processed data → String output
  - **例外・リトライ**: 出力失敗時は再試行
  - **可観測性**: 出力処理ログとメトリクス

## 3. データモデル
```python
class Data:
    value: str
```

## 4. API/インターフェース
- **process_input**:
  - **概要**: 入力データを処理するAPI
  - **エンドポイント**: /api/process
  - **リクエスト/レスポンス**: JSON形式
  - **エラー**: 400/500エラーコード
  - **モジュール境界**: input-handler担当

- **generate_output**:
  - **概要**: 出力データを生成するAPI
  - **エンドポイント**: /api/output
  - **リクエスト/レスポンス**: JSON形式
  - **エラー**: 400/500エラーコード
  - **モジュール境界**: output-handler担当

## 5. 非機能・品質
- **パフォーマンス**: 1秒以内のレスポンス [NFR-01]
- **セキュリティ**: 入力値検証とサニタイズ
- **可用性**: 99%以上の稼働率

## 6. テスト戦略
- **単体/結合/E2E の役割分担**: 各レベルでの検証内容
- **test-input-processing**: 入力処理の重要なテストケース
  - **テストデータ方針**: 正常系・異常系のテストデータ準備
  - **観測可能な合否基準**: 入力が正しく処理され出力される
- **test-output-generation**: 出力処理の重要なテストケース
  - **テストデータ方針**: 様々なデータパターンでのテスト
  - **観測可能な合否基準**: 正しい形式で出力される

## 7. トレーサビリティ (必須)
- REQ-01 ⇔ **input-handler**
- REQ-02 ⇔ **output-handler**
- TR-01 ⇔ **test-input-processing**
- TR-02 ⇔ **test-output-generation**

## 8. フロー設計
- **主要シーケンス**: 入力受信→検証→処理→出力生成
- **状態遷移**: IDLE→PROCESSING→COMPLETE
- **バックプレッシャー/キュー処理**: リクエスト待ち行列制御

## 9. 障害・エッジケース
- **フェイルパターン**: 入力不正、処理タイムアウト
- **フォールバック**: デフォルト値での処理継続
- **タイムアウト/リトライ方針**: 3秒タイムアウト、3回リトライ

## 10. セキュリティ & コンプライアンス
- **認証/認可**: APIキーベース認証
- **データ保護**: 入力データの暗号化
- **監査ログ**: 全処理のログ記録
- **秘密管理**: 環境変数での管理

## 11. リスクと対応 (Optional)
- **リスク1**: 性能要件未達 → 最適化実施
"""
