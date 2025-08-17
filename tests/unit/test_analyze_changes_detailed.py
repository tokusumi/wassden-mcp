"""Detailed unit tests for analyze_changes functionality."""

from unittest.mock import patch

import pytest

from wassden.handlers.traceability import handle_analyze_changes


@pytest.fixture
def sample_requirements():
    """Sample requirements document following standard format."""
    return """
# requirements.md

## 6. 機能要件（EARS）

- **REQ-01**: システムは、ユーザー認証要求を受信したとき、認証機能を提供すること
- **REQ-02**: システムは、データ処理要求があったとき、効率的にユーザーデータを処理すること
- **REQ-03**: システムは、レポート生成要求を受けたとき、詳細レポートを生成すること
"""


@pytest.fixture
def sample_design():
    """Sample design document following standard format."""
    return """
# design.md

## 1. アーキテクチャ概要
[Requirements: REQ-01, REQ-02, REQ-03]

## 2. コンポーネント設計
- **auth-service**: ユーザー認証サービス [REQ-01]
- **data-processor**: データ処理エンジン [REQ-02]
- **report-engine**: レポート生成システム [REQ-03]

REQ-01の認証機能は**auth-service**コンポーネントが処理。
REQ-02のデータ処理は**data-processor**が実装。
REQ-03のレポート生成は**report-engine**が担当。
"""


@pytest.fixture
def sample_tasks():
    """Sample tasks document following standard format."""
    return """
# tasks.md

## 1. 基盤構築

- [x] 1.0 認証基盤構築 [REQ-01]
  - [x] 1.1 **auth-service**実装
  - [x] 1.2 認証API開発

## 2. 機能実装

- [x] 2.0 データ処理実装 [REQ-02]
  - [x] 2.1 **data-processor**パイプライン構築

- [ ] 3.0 レポート機能 [REQ-03]
  - [ ] 3.1 **report-engine**テンプレート作成
"""


class TestAnalyzeChangesDetailed:
    """Detailed tests for analyze_changes impact analysis."""

    @pytest.mark.asyncio
    async def test_requirements_change_new_req_impact_analysis(self, sample_requirements, sample_design, sample_tasks):
        """Test impact analysis for new requirements changes."""

        # Mock file reading to return our test data
        with patch("wassden.handlers.traceability._read_all_specs") as mock_read:
            mock_read.return_value = {
                "requirements": sample_requirements,
                "design": sample_design,
                "tasks": sample_tasks,
            }

            result = await handle_analyze_changes(
                {
                    "changedFile": "specs/requirements.md",
                    "changeDescription": "Added REQ-04 for new notification feature",
                }
            )

        # Verify basic response structure
        assert isinstance(result, dict)
        assert "content" in result
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"

        result_text = result["content"][0]["text"]

        # Verify change detection in header
        assert "specs/requirements.md" in result_text
        assert "Added REQ-04 for new notification feature" in result_text

        # Verify impact analysis section
        assert "影響を受ける設計要素" in result_text

        # For new REQ-04 (not in existing matrix), should show no existing impact
        assert "なし" in result_text
        assert "まだ設計に反映されていません" in result_text

        # Verify next steps guidance
        assert "次のステップ" in result_text
        assert "validate_" in result_text
        assert "get_traceability" in result_text

    @pytest.mark.asyncio
    async def test_requirements_change_existing_req_impact_analysis(
        self, sample_requirements, sample_design, sample_tasks
    ):
        """Test impact analysis for existing requirements changes."""

        # Mock file reading to return our test data
        with patch("wassden.handlers.traceability._read_all_specs") as mock_read:
            mock_read.return_value = {
                "requirements": sample_requirements,
                "design": sample_design,
                "tasks": sample_tasks,
            }

            result = await handle_analyze_changes(
                {
                    "changedFile": "specs/requirements.md",
                    "changeDescription": "Modified REQ-01 to include OAuth support",
                }
            )

        result_text = result["content"][0]["text"]

        # Verify change detection
        assert "specs/requirements.md" in result_text
        assert "Modified REQ-01 to include OAuth support" in result_text

        # Verify impact analysis shows affected design components
        assert "影響を受ける設計要素" in result_text
        assert "auth-service" in result_text  # Should identify connected design component

        # Verify recommended actions for existing requirement changes
        assert "推奨アクション" in result_text
        assert "設計要素を確認" in result_text
        assert "validate_design" in result_text
        assert "タスクの見直し" in result_text

    @pytest.mark.asyncio
    async def test_design_change_impact_analysis(self, sample_requirements, sample_design, sample_tasks):
        """Test impact analysis for design changes with component-based analysis."""

        with patch("wassden.handlers.traceability._read_all_specs") as mock_read:
            mock_read.return_value = {
                "requirements": sample_requirements,
                "design": sample_design,
                "tasks": sample_tasks,
            }

            result = await handle_analyze_changes(
                {
                    "changedFile": "specs/design.md",
                    "changeDescription": "Modified data-processor component to use microservices architecture",
                }
            )

        result_text = result["content"][0]["text"]

        # Verify design change detection
        assert "specs/design.md" in result_text
        assert "Modified data-processor component to use microservices architecture" in result_text

        # Verify impact analysis section
        assert "影響を受けるタスク" in result_text

        # For design component changes, should show affected tasks
        assert "data-processor" in result_text  # Component name should be mentioned

        # Verify next steps guidance
        assert "次のステップ" in result_text

    @pytest.mark.asyncio
    async def test_tasks_change_impact_analysis(self, sample_requirements, sample_design, sample_tasks):
        """Test impact analysis for task changes."""

        with patch("wassden.handlers.traceability._read_all_specs") as mock_read:
            mock_read.return_value = {
                "requirements": sample_requirements,
                "design": sample_design,
                "tasks": sample_tasks,
            }

            result = await handle_analyze_changes(
                {"changedFile": "specs/tasks.md", "changeDescription": "Modified TASK-02 implementation approach"}
            )

        result_text = result["content"][0]["text"]

        # Verify task change detection
        assert "specs/tasks.md" in result_text
        assert "Modified TASK-02 implementation approach" in result_text

        # Verify task impact analysis section
        assert "影響を受ける" in result_text

        # Verify next steps guidance
        assert "次のステップ" in result_text

    @pytest.mark.asyncio
    async def test_multiple_req_changes_impact(self, sample_requirements, sample_design, sample_tasks):
        """Test impact analysis when multiple requirements are changed."""

        with patch("wassden.handlers.traceability._read_all_specs") as mock_read:
            mock_read.return_value = {
                "requirements": sample_requirements,
                "design": sample_design,
                "tasks": sample_tasks,
            }

            result = await handle_analyze_changes(
                {
                    "changedFile": "specs/requirements.md",
                    "changeDescription": (
                        "Added REQ-04 for notifications, REQ-05 for analytics, and modified REQ-01 authentication scope"
                    ),
                }
            )

        result_text = result["content"][0]["text"]

        # Verify multiple change detection in description
        assert "REQ-04" in result_text
        assert "REQ-05" in result_text
        assert "REQ-01" in result_text
        assert "notifications" in result_text
        assert "analytics" in result_text

        # Verify impact analysis shows mixed results (existing vs new)
        assert "影響を受ける設計要素" in result_text
        # Should show auth-service for existing REQ-01 and potentially show no impact for new REQs
        assert "auth-service" in result_text or "なし" in result_text

    @pytest.mark.asyncio
    async def test_non_spec_file_change_handling(self):
        """Test handling of changes to non-specification files."""

        result = await handle_analyze_changes(
            {"changedFile": "src/main.py", "changeDescription": "Refactored authentication logic"}
        )

        result_text = result["content"][0]["text"]

        # Verify non-spec file handling
        assert "src/main.py" in result_text
        assert "Refactored authentication logic" in result_text

        # Should provide different handling for non-spec files
        assert "実装ファイルの変更" in result_text

    @pytest.mark.asyncio
    async def test_empty_change_description_handling(self, sample_requirements, sample_design, sample_tasks):
        """Test handling of empty change descriptions."""

        with patch("wassden.handlers.traceability._read_all_specs") as mock_read:
            mock_read.return_value = {
                "requirements": sample_requirements,
                "design": sample_design,
                "tasks": sample_tasks,
            }

            result = await handle_analyze_changes({"changedFile": "specs/requirements.md", "changeDescription": ""})

        result_text = result["content"][0]["text"]

        # Should still provide basic analysis even with empty description
        assert "specs/requirements.md" in result_text
        assert "影響を受ける設計要素" in result_text

        # For empty description, should show no detected changes
        assert "なし" in result_text

    @pytest.mark.asyncio
    async def test_change_impact_output_structure(self, sample_requirements, sample_design, sample_tasks):
        """Test the structure and completeness of change impact output."""

        with patch("wassden.handlers.traceability._read_all_specs") as mock_read:
            mock_read.return_value = {
                "requirements": sample_requirements,
                "design": sample_design,
                "tasks": sample_tasks,
            }

            result = await handle_analyze_changes(
                {
                    "changedFile": "specs/requirements.md",
                    "changeDescription": "Added REQ-04 for user preferences management",
                }
            )

        result_text = result["content"][0]["text"]

        # Verify required sections exist
        required_sections = [
            "変更影響分析レポート",  # Change Impact Analysis header
            "変更内容",  # Changed Content section
            "影響を受ける",  # Affected section
            "次のステップ",  # Next Steps section
        ]

        for section in required_sections:
            assert section in result_text, f"Missing required section: {section}"

        # Verify validation steps are mentioned
        assert "validate_" in result_text
        assert "get_traceability" in result_text

    @pytest.mark.asyncio
    async def test_traceability_matrix_usage_in_analysis(self, sample_requirements, sample_design, sample_tasks):
        """Test that the analysis properly uses traceability matrix for impact detection."""

        with patch("wassden.handlers.traceability._read_all_specs") as mock_read:
            mock_read.return_value = {
                "requirements": sample_requirements,
                "design": sample_design,
                "tasks": sample_tasks,
            }

            # Mock the traceability matrix building with simplified structure
            with patch("wassden.lib.traceability.build_traceability_matrix") as mock_matrix:
                mock_matrix.return_value = {
                    "requirements": {"REQ-01", "REQ-02", "REQ-03"},
                    "design_components": {"auth-service", "data-processor", "report-engine"},
                    "tasks": {"TASK-01", "TASK-02", "TASK-03"},
                    "req_to_design": {
                        "REQ-01": ["auth-service"],
                        "REQ-02": ["data-processor"],
                        "REQ-03": ["report-engine"],
                    },
                    "design_to_tasks": {
                        "auth-service": ["TASK-01"],
                        "data-processor": ["TASK-02"],
                        "report-engine": ["TASK-03"],
                    },
                    "task_dependencies": {},
                }

                result = await handle_analyze_changes(
                    {
                        "changedFile": "specs/requirements.md",
                        "changeDescription": "Modified REQ-02 to include additional validation requirements",
                    }
                )

                # Verify traceability matrix was used
                mock_matrix.assert_called_once()

        result_text = result["content"][0]["text"]

        # Verify analysis identified correct dependencies based on matrix
        assert "REQ-02" in result_text
        assert "data-processor" in result_text  # Should identify connected design component

        # Verify impact analysis structure
        assert "影響を受ける設計要素" in result_text
        assert "推奨アクション" in result_text
