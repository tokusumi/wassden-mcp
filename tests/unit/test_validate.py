"""Unit tests for validation functions."""

from wassden.lib import validate

# Test constants
EXPECTED_REQUIREMENTS_COUNT = 2
EXPECTED_NFRS_COUNT = 1
EXPECTED_KPIS_COUNT = 1
EXPECTED_TRS_COUNT = 2
EXPECTED_SECTIONS_COUNT = 8  # Now includes section 7 (テスト要件)
EXPECTED_REFERENCED_REQUIREMENTS = 2
EXPECTED_TASKS_COUNT = 6


def test_validate_req_id():
    """Test requirement ID validation."""
    assert validate.validate_req_id("REQ-01") is True
    assert validate.validate_req_id("REQ-99") is True
    assert validate.validate_req_id("REQ-001") is False
    assert validate.validate_req_id("REQ-1") is False
    assert validate.validate_req_id("REQ01") is False
    assert validate.validate_req_id("REQ") is False


def test_validate_task_id():
    """Test task ID validation."""
    assert validate.validate_task_id("TASK-01-01") is True
    assert validate.validate_task_id("TASK-01-01-01") is True
    assert validate.validate_task_id("TASK-99-99") is True
    assert validate.validate_task_id("TASK-01") is False
    assert validate.validate_task_id("TASK-01-01-01-01") is False
    assert validate.validate_task_id("TASK01-01") is False


def test_validate_requirements_structure(sample_requirements):
    """Test requirements structure validation."""
    errors = validate.validate_requirements_structure(sample_requirements)
    assert len(errors) == 0

    # Test missing section
    incomplete = sample_requirements.replace("## 1. 用語集", "")
    errors = validate.validate_requirements_structure(incomplete)
    assert any("用語集" in error for error in errors)

    # Test invalid REQ-ID
    invalid_req = sample_requirements.replace("REQ-01", "REQ-001")
    errors = validate.validate_requirements_structure(invalid_req)
    assert any("REQ-001" in error for error in errors)


def test_validate_design_structure(sample_design):
    """Test design structure validation."""
    errors = validate.validate_design_structure(sample_design)
    assert len(errors) == 0

    # Test missing REQ references
    no_refs = sample_design.replace("REQ-01", "").replace("REQ-02", "")
    errors = validate.validate_design_structure(no_refs)
    assert any("REQ-ID" in error for error in errors)


def test_validate_tasks_structure(sample_tasks):
    """Test tasks structure validation."""
    errors = validate.validate_tasks_structure(sample_tasks)
    assert len(errors) == 0

    # Test duplicate task IDs
    duplicate = sample_tasks + "\n- **TASK-01-01**: Duplicate task"
    errors = validate.validate_tasks_structure(duplicate)
    assert any("Duplicate" in error for error in errors)


def test_validate_tasks_with_incomplete_references():
    """Test that incomplete TASK-ID references in descriptions are not flagged as errors."""
    # Test case from dogfooding-findings.md
    tasks_content = """# タスク管理

## 1. 概要
プロジェクトのタスク管理

## 2. タスク一覧
- **TASK-01-01**: 初期設定タスク
- **TASK-01-02**: 基本実装タスク
- **TASK-01-03**: テスト作成タスク

## 3. 依存関係
- TASK-01-02 → TASK-01-01
- TASK-01-03 → TASK-01-02

## 4. マイルストーン
- **M1**: Foundation Phase完了 (TASK-01 (TASK-01-01〜TASK-01-03) 完了時点)
"""
    errors = validate.validate_tasks_structure(tasks_content)

    # TASK-01 and TASK-01-03 in the milestone description should NOT be flagged as errors
    # because they are references in descriptive text, not task definitions
    assert not any("TASK-01" in error and "Invalid" in error for error in errors), (
        f"TASK-01 in description should not be invalid. Errors: {errors}"
    )
    assert not any("TASK-03" in error and "Invalid" in error for error in errors), (
        f"TASK-03 reference should not be invalid. Errors: {errors}"
    )

    # The actual task definitions (TASK-01-01, TASK-01-02, TASK-01-03) should be valid
    assert len(errors) == 0, f"Should have no errors for valid task structure, but got: {errors}"


def test_task_id_validation_context_aware():
    """Test that TASK-ID validation considers context (definitions vs references)."""
    # Incomplete TASK-IDs in various contexts
    tasks_content = """# タスク管理

## 1. 概要
このセクションではTASK-01について説明します。

## 2. タスク一覧
- **TASK-02-01**: 実装タスク
  - 詳細: TASK-02の最初のサブタスク
- **TASK-02-02**: テストタスク
  - 関連: TASK-01やTASK-03も参照

## 3. 依存関係
- TASK-02-02 → TASK-02-01

## 4. マイルストーン
- M1: TASK-01完了時点
- M2: TASK-02 (TASK-02-01, TASK-02-02)完了時点
- M3: TASK-03開始予定
"""
    errors = validate.validate_tasks_structure(tasks_content)

    # References to TASK-01, TASK-02, TASK-03 should not be errors
    invalid_errors = [e for e in errors if "Invalid TASK-ID format" in e]
    assert len(invalid_errors) == 0, f"Should not have invalid format errors for references: {invalid_errors}"


def test_validate_requirements(sample_requirements):
    """Test complete requirements validation."""
    result = validate.validate_requirements(sample_requirements)
    assert result["isValid"] is True
    assert result["stats"]["totalRequirements"] == EXPECTED_REQUIREMENTS_COUNT
    assert result["stats"]["totalNFRs"] == EXPECTED_NFRS_COUNT
    assert result["stats"]["totalKPIs"] == EXPECTED_KPIS_COUNT
    assert result["stats"]["totalTRs"] == EXPECTED_TRS_COUNT
    assert len(result["foundSections"]) == EXPECTED_SECTIONS_COUNT


def test_validate_design(sample_design, sample_requirements):
    """Test complete design validation."""
    result = validate.validate_design(sample_design, sample_requirements)
    assert result["isValid"] is True
    assert result["stats"]["referencedRequirements"] == EXPECTED_REFERENCED_REQUIREMENTS
    assert len(result["stats"]["missingReferences"]) == 0


def test_validate_tasks(sample_tasks, sample_requirements, sample_design):
    """Test complete tasks validation with requirements and design."""
    result = validate.validate_tasks(sample_tasks, sample_requirements, sample_design)
    assert result["isValid"] is True
    assert result["stats"]["totalTasks"] == EXPECTED_TASKS_COUNT
    assert result["stats"]["dependencies"] >= 0


def test_validate_tasks_missing_test_scenarios():
    """Test tasks validation when test scenarios are not referenced."""
    requirements_content = """
## 7. テスト要件（Testing Requirements）
- **TR-01**: 入力処理のテスト要件
- **TR-02**: 出力処理のテスト要件
"""

    design_content = """
## 6. テスト戦略
- **test-input-processing**: 入力処理テスト
- **test-output-generation**: 出力処理テスト

## 7. トレーサビリティ (必須)
- TR-01 ⇔ **test-input-processing**
- TR-02 ⇔ **test-output-generation**
"""

    # Tasks that don't reference all test scenarios
    tasks_content = """
## 2. タスク一覧
- [ ] **TASK-01-01**: Test task
  - **REQ**: [TR-01]
  - **DC**: **test-input-processing**
  - **依存**: なし
  - **受け入れ観点**:
    - 観点1: テストが実行される
"""

    result = validate.validate_tasks(tasks_content, requirements_content, design_content)
    assert result["isValid"] is False
    assert any("test-output-generation" in str(issue) for issue in result["issues"])


def test_validate_tasks_complete_test_scenario_coverage():
    """Test tasks validation when all test scenarios are properly referenced."""
    requirements_content = """
## 7. テスト要件（Testing Requirements）
- **TR-01**: 入力処理のテスト要件
- **TR-02**: 出力処理のテスト要件
"""

    design_content = """
## 1. アーキテクチャ概要
システム概要

## 2. コンポーネント設計
- **component-a**: コンポーネント

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
- REQ-01 ⇔ **component-a**
- TR-01 ⇔ **test-input-processing**
- TR-02 ⇔ **test-output-generation**
"""

    # Tasks that reference all test scenarios
    tasks_content = """
## 1. 概要
タスク概要

## 2. タスク一覧
- [ ] **TASK-01-01**: Input test task
  - **REQ**: [TR-01]
  - **DC**: **test-input-processing**
  - **依存**: なし
  - **受け入れ観点**:
    - 観点1: 入力テストが実行される

- [ ] **TASK-01-02**: Output test task
  - **REQ**: [TR-02]
  - **DC**: **test-output-generation**
  - **依存**: TASK-01-01
  - **受け入れ観点**:
    - 観点1: 出力テストが実行される

- [ ] **TASK-01-03**: Component task
  - **REQ**: [REQ-01]
  - **DC**: **component-a**
  - **依存**: なし
  - **受け入れ観点**:
    - 観点1: コンポーネントが実装される

## 3. 依存関係
TASK-01-01 → TASK-01-02

## 4. マイルストーン
- M1: 完了
"""

    result = validate.validate_tasks(tasks_content, requirements_content, design_content)
    assert result["isValid"] is True, f"Validation failed with issues: {result.get('issues', [])}"
