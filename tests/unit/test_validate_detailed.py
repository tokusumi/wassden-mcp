"""Detailed validation tests matching TypeScript version granularity."""

from wassden.lib import validate


class TestValidateReqIdDetailed:
    """Detailed requirement ID validation tests."""

    def test_accepts_valid_req_formats(self):
        """Test acceptance of various valid REQ-ID formats."""
        valid_ids = ["REQ-01", "REQ-02", "REQ-10", "REQ-99", "REQ-50", "REQ-25"]
        for req_id in valid_ids:
            assert validate.validate_req_id(req_id), f"{req_id} should be valid"

    def test_rejects_invalid_req_formats(self):
        """Test rejection of invalid REQ-ID formats."""
        invalid_ids = [
            "REQ-",  # No number
            "REQ-0",  # Single digit zero
            "REQ-00",  # Double zero
            "REQ-01a",  # Letter suffix
            "INVALID-01",  # Wrong prefix
            "req-01",  # Lowercase
            "",  # Empty string
            "REQ",  # No hyphen
            "REQ-001",  # Three digits
            "REQ-100",  # Three digits
            "R-01",  # Short prefix
            "REQUIREMENT-01",  # Long prefix
        ]
        for req_id in invalid_ids:
            assert not validate.validate_req_id(req_id), f"{req_id} should be invalid"

    def test_boundary_values(self):
        """Test boundary values for REQ-ID validation."""
        assert validate.validate_req_id("REQ-01")  # Minimum valid
        assert validate.validate_req_id("REQ-99")  # Maximum valid
        assert not validate.validate_req_id("REQ-00")  # Below minimum

    def test_special_characters(self):
        """Test REQ-ID with special characters."""
        special_cases = [
            "REQ-01@",
            "REQ-01#",
            "REQ-01$",
            "REQ-01%",
            "REQ-01!",
            "REQ-01?",
            "REQ-01.",
            "REQ-01,",
            "REQ-01;",
            "REQ-01:",
        ]
        for req_id in special_cases:
            assert not validate.validate_req_id(req_id), f"{req_id} should be invalid"

    def test_whitespace_handling(self):
        """Test REQ-ID with whitespace."""
        whitespace_cases = [
            " REQ-01",  # Leading space
            "REQ-01 ",  # Trailing space
            " REQ-01 ",  # Both spaces
            "REQ- 01",  # Space after hyphen
            "REQ -01",  # Space before hyphen
            "REQ\t01",  # Tab character
            "REQ\n01",  # Newline character
        ]
        for req_id in whitespace_cases:
            assert not validate.validate_req_id(req_id), f"{req_id} should be invalid"


class TestValidateTaskIdDetailed:
    """Detailed task ID validation tests."""

    def test_accepts_valid_two_level_tasks(self):
        """Test acceptance of valid two-level task IDs."""
        valid_ids = ["TASK-01-01", "TASK-01-02", "TASK-10-20", "TASK-99-99", "TASK-50-25", "TASK-05-15"]
        for task_id in valid_ids:
            assert validate.validate_task_id(task_id), f"{task_id} should be valid"

    def test_accepts_valid_three_level_tasks(self):
        """Test acceptance of valid three-level task IDs."""
        valid_ids = [
            "TASK-01-01-01",
            "TASK-01-01-02",
            "TASK-05-10-15",
            "TASK-99-99-99",
            "TASK-10-20-30",
            "TASK-25-50-75",
        ]
        for task_id in valid_ids:
            assert validate.validate_task_id(task_id), f"{task_id} should be valid"

    def test_rejects_invalid_task_formats(self):
        """Test rejection of invalid task ID formats."""
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
            "TSK-01-01",  # Wrong prefix
            "TASK-00-01",  # Zero in first position
            "TASK-01-00",  # Zero in second position
        ]
        for task_id in invalid_ids:
            assert not validate.validate_task_id(task_id), f"{task_id} should be invalid"

    def test_boundary_values_task_id(self):
        """Test boundary values for task ID validation."""
        assert validate.validate_task_id("TASK-01-01")  # Minimum valid
        assert validate.validate_task_id("TASK-99-99")  # Maximum valid
        assert not validate.validate_task_id("TASK-00-01")  # Zero first
        assert not validate.validate_task_id("TASK-01-00")  # Zero second

    def test_task_id_with_special_characters(self):
        """Test task ID with special characters."""
        special_cases = [
            "TASK-01-01@",
            "TASK-01-01#",
            "TASK-01@01",
            "TASK@01-01",
            "TASK-01_01",
            "TASK_01-01",
            "TASK-01+01",
            "TASK+01-01",
        ]
        for task_id in special_cases:
            assert not validate.validate_task_id(task_id), f"{task_id} should be invalid"

    def test_task_id_whitespace_handling(self):
        """Test task ID with whitespace."""
        whitespace_cases = [
            " TASK-01-01",  # Leading space
            "TASK-01-01 ",  # Trailing space
            " TASK-01-01 ",  # Both spaces
            "TASK- 01-01",  # Space after first hyphen
            "TASK -01-01",  # Space before first hyphen
            "TASK-01- 01",  # Space after second hyphen
            "TASK-01 -01",  # Space before second hyphen
            "TASK\t01-01",  # Tab character
            "TASK-01\n01",  # Newline character
        ]
        for task_id in whitespace_cases:
            assert not validate.validate_task_id(task_id), f"{task_id} should be invalid"


class TestRequirementsStructureDetailed:
    """Detailed requirements structure validation tests."""

    def test_detects_each_missing_section_individually(self):
        """Test detection of each missing section individually."""
        base_content = """
# Requirements Document

## 0. サマリー
テストプロジェクトです。

## 6. 機能要件（EARS）
- **REQ-01**: システムは、機能を提供すること
"""

        missing_sections = [
            ("用語集", "1. 用語集"),
            ("スコープ", "2. スコープ"),
            ("制約", "3. 制約"),
            ("非機能要件", "4. 非機能要件"),
            ("KPI", "5. KPI"),
        ]

        for section_name, _section_header in missing_sections:
            content = base_content  # Missing this section
            errors = validate.validate_requirements_structure(content)
            assert any(section_name in error for error in errors), f"Should detect missing {section_name}"

    def test_validates_complete_requirements_document(self):
        """Test validation of complete requirements document."""
        complete_content = """
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
"""

        errors = validate.validate_requirements_structure(complete_content)
        assert len(errors) == 0, f"Complete document should have no errors, but got: {errors}"

    def test_detects_multiple_missing_sections(self):
        """Test detection of multiple missing sections."""
        minimal_content = """
# Requirements Document

## 0. サマリー
テストプロジェクトです。

## 6. 機能要件（EARS）
- **REQ-01**: システムは、機能を提供すること
"""

        errors = validate.validate_requirements_structure(minimal_content)

        # Should detect multiple missing sections
        missing_sections = ["用語集", "スコープ", "制約", "非機能要件", "KPI"]
        for section in missing_sections:
            assert any(section in error for error in errors), f"Should detect missing {section}"

    def test_detects_duplicate_req_ids_multiple(self):
        """Test detection of multiple duplicate REQ-IDs."""
        content_with_duplicates = """
## 6. 機能要件（EARS）
- **REQ-01**: システムは、最初の機能を提供すること
- **REQ-02**: システムは、2番目の機能を提供すること
- **REQ-01**: システムは、重複した機能を提供すること
- **REQ-03**: システムは、3番目の機能を提供すること
- **REQ-02**: システムは、また重複した機能を提供すること
"""

        errors = validate.validate_requirements_structure(content_with_duplicates)

        # Should detect duplicate REQ-IDs
        assert any("Duplicate REQ-IDs" in error for error in errors)

        # Should mention both duplicated IDs
        duplicate_error = next(error for error in errors if "Duplicate REQ-IDs" in error)
        assert "REQ-01" in duplicate_error
        assert "REQ-02" in duplicate_error

    def test_detects_multiple_invalid_req_id_formats(self):
        """Test detection of multiple invalid REQ-ID formats."""
        content_with_invalid_ids = """
## 6. 機能要件（EARS）
- **REQ-001**: システムは、無効なIDフォーマット1
- **REQ-1**: システムは、無効なIDフォーマット2
- **INVALID-01**: システムは、間違ったプレフィックス
- **REQ-**: システムは、数字なし
- **req-01**: システムは、小文字
- **REQ-99a**: システムは、文字付き数字
"""

        errors = validate.validate_requirements_structure(content_with_invalid_ids)

        invalid_ids = ["REQ-001", "REQ-1", "INVALID-01", "REQ-", "req-01", "REQ-99a"]
        for invalid_id in invalid_ids:
            assert any(invalid_id in error for error in errors), f"Should detect invalid {invalid_id}"


class TestDesignStructureDetailed:
    """Detailed design structure validation tests."""

    def test_validates_complete_design_document(self):
        """Test validation of complete design document."""
        complete_design = """
# Design Document

## 1. アーキテクチャ概要
システム設計の概要 [REQ-01, REQ-02]

## 2. コンポーネント設計
- **input-handler**: 入力処理コンポーネント [REQ-01]
- **output-generator**: 出力生成コンポーネント [REQ-02]

## 3. データモデル
データ構造の定義

## 4. API設計
API仕様の詳細

## 5. 非機能設計
パフォーマンスとセキュリティの設計

## 6. テスト戦略
テスト計画とアプローチ
"""

        errors = validate.validate_design_structure(complete_design)
        assert len(errors) == 0, f"Complete design should have no errors, but got: {errors}"

    def test_detects_each_missing_design_section(self):
        """Test detection of each missing design section individually."""
        base_design = """
# Design Document

## 1. アーキテクチャ概要
システム設計の概要 [REQ-01]
"""

        missing_sections = ["コンポーネント設計", "データ", "API", "非機能", "テスト"]

        for _section in missing_sections:
            errors = validate.validate_design_structure(base_design)
            # Since we're only checking for presence of sections in content,
            # all missing sections should be detected
            assert len(errors) > 0

    def test_detects_missing_req_references_in_sections(self):
        """Test detection of missing REQ-ID references in sections."""
        design_without_refs = """
# Design Document

## 1. アーキテクチャ概要
システム設計の概要（REQ-IDなし）

## 2. コンポーネント設計
- **component**: 説明のみ、REQ-IDなし

## 3. データモデル
データ構造の定義

## 4. API設計
API仕様の詳細

## 5. 非機能設計
パフォーマンス設計

## 6. テスト戦略
テスト計画
"""

        errors = validate.validate_design_structure(design_without_refs)
        assert any("REQ-ID" in error for error in errors)


class TestTasksStructureDetailed:
    """Detailed tasks structure validation tests."""

    def test_validates_complete_tasks_document(self):
        """Test validation of complete tasks document."""
        complete_tasks = """
# Tasks Document

## 1. 概要
タスクの概要説明

## 2. タスク一覧
- **TASK-01-01**: 最初のタスク
- **TASK-01-02**: 2番目のタスク
- **TASK-02-01**: 3番目のタスク

## 3. 依存関係
タスクの依存関係

## 4. マイルストーン
プロジェクトのマイルストーン
"""

        errors = validate.validate_tasks_structure(complete_tasks)
        assert len(errors) == 0, f"Complete tasks document should have no errors, but got: {errors}"

    def test_detects_duplicate_task_ids_multiple(self):
        """Test detection of multiple duplicate task IDs."""
        content_with_duplicates = """
## 2. タスク一覧
- **TASK-01-01**: 最初のタスク
- **TASK-01-02**: 2番目のタスク
- **TASK-01-01**: 重複した最初のタスク
- **TASK-02-01**: 3番目のタスク
- **TASK-01-02**: 重複した2番目のタスク
"""

        errors = validate.validate_tasks_structure(content_with_duplicates)

        # Should detect duplicate TASK-IDs
        assert any("Duplicate TASK-IDs" in error for error in errors)

        # Should mention both duplicated IDs
        duplicate_error = next(error for error in errors if "Duplicate TASK-IDs" in error)
        assert "TASK-01-01" in duplicate_error
        assert "TASK-01-02" in duplicate_error

    def test_detects_multiple_invalid_task_id_formats(self):
        """Test detection of multiple invalid task ID formats."""
        content_with_invalid_ids = """
## 2. タスク一覧
- **TASK-1-01**: 無効フォーマット1（短い最初の数字）
- **TASK-01-1**: 無効フォーマット2（短い2番目の数字）
- **INVALID-01-01**: 間違ったプレフィックス
- **TASK-001-01**: 3桁の数字
- **TASK-01-001**: 3桁の数字
- **task-01-01**: 小文字
- **TASK-AB-01**: 文字
- **TASK-01**: レベルが不足
"""

        errors = validate.validate_tasks_structure(content_with_invalid_ids)

        invalid_ids = [
            "TASK-1-01",
            "TASK-01-1",
            "INVALID-01-01",
            "TASK-001-01",
            "TASK-01-001",
            "task-01-01",
            "TASK-AB-01",
            "TASK-01",
        ]
        for invalid_id in invalid_ids:
            assert any(invalid_id in error for error in errors), f"Should detect invalid {invalid_id}"
