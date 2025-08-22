"""Unit tests for EARS analyzer module.

Tests for TASK-02-01 EARS coverage measurement functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from wassden.lib.ears_analyzer import (
    DocumentParseError,
    EARSAnalyzer,
    EARSAnalyzerError,
    InvalidMarkdownError,
)
from wassden.lib.experiment import EARSCoverageReport, EARSViolationDetail
from wassden.lib.validate_ears import EARSValidationResult, EARSViolation
from wassden.types import Language

pytestmark = pytest.mark.dev


@pytest.mark.dev
class TestEARSAnalyzer:
    """Test cases for EARSAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create EARSAnalyzer instance."""
        return EARSAnalyzer()

    @pytest.fixture
    def sample_markdown_file(self):
        """Create a temporary markdown file for testing."""
        content = """# Requirements

- **REQ-01**: システムは、データを受信したとき、処理を実行すること
- **REQ-02**: システムは、結果を表示すること
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content)
            f.flush()
            yield Path(f.name)
        Path(f.name).unlink()

    @pytest.fixture
    def sample_validation_result(self):
        """Create sample EARS validation result."""
        return EARSValidationResult(
            pattern="ubiquitous",
            total=2,
            matched=1,
            rate=0.5,
            violations=[EARSViolation(line=5, text="システムは、結果を表示すること", reason="missing_trigger")],
        )

    @pytest.mark.asyncio
    async def test_analyze_document_success(self, analyzer, sample_markdown_file):
        """Test successful document analysis.

        Implements: REQ-01 - 観点1: 要件識別子を含む要件を正確に抽出する
        """
        # Mock the validator
        mock_result = EARSValidationResult(
            pattern="ubiquitous",
            total=2,
            matched=1,
            rate=0.5,
            violations=[EARSViolation(line=5, text="システムは、結果を表示すること", reason="missing_trigger")],
        )

        with (
            patch("wassden.lib.ears_analyzer.determine_language", return_value=Language.JAPANESE),
            patch("wassden.lib.ears_analyzer.validate_ears_in_content", return_value=mock_result),
        ):
            report = await analyzer.analyze_document(sample_markdown_file)

        # Verify report structure
        assert isinstance(report, EARSCoverageReport)
        assert report.total_requirements == 2
        assert report.ears_compliant == 1
        assert report.coverage_rate == 0.5
        assert len(report.violations) == 1
        assert report.document_path == sample_markdown_file

        # Verify violation details
        violation = report.violations[0]
        assert violation.line_number == 5
        assert violation.violation_type == "missing_trigger"
        assert violation.suggestion is None

    @pytest.mark.asyncio
    async def test_analyze_document_file_not_found(self, analyzer):
        """Test analysis with non-existent file."""
        non_existent_path = Path("/non/existent/file.md")

        with pytest.raises(FileNotFoundError, match="Document not found"):
            await analyzer.analyze_document(non_existent_path)

    @pytest.mark.asyncio
    async def test_analyze_document_invalid_extension(self, analyzer):
        """Test analysis with non-markdown file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Some content")
            f.flush()
            txt_path = Path(f.name)

        try:
            with pytest.raises(InvalidMarkdownError, match="Not a markdown file"):
                await analyzer.analyze_document(txt_path)
        finally:
            txt_path.unlink()

    @pytest.mark.asyncio
    async def test_analyze_document_unicode_error(self, analyzer):
        """Test analysis with unicode decode error."""
        # Create a file with invalid UTF-8
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False) as f:
            f.write(b"\xff\xfe# Invalid UTF-8")
            f.flush()
            invalid_path = Path(f.name)

        try:
            with pytest.raises(DocumentParseError, match="Failed to decode document"):
                await analyzer.analyze_document(invalid_path)
        finally:
            invalid_path.unlink()

    @pytest.mark.asyncio
    async def test_analyze_documents_success(self, analyzer, sample_markdown_file):
        """Test analyzing multiple documents."""
        # Create second file
        content2 = """# More Requirements

- **REQ-03**: システムは、入力を検証したとき、エラーを表示すること
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(content2)
            f.flush()
            second_file = Path(f.name)

        try:
            # Mock validator for both files
            mock_result1 = EARSValidationResult(pattern="ubiquitous", total=1, matched=1, rate=1.0, violations=[])
            mock_result2 = EARSValidationResult(pattern="ubiquitous", total=1, matched=1, rate=1.0, violations=[])

            with (
                patch("wassden.lib.ears_analyzer.determine_language", return_value=Language.JAPANESE),
                patch("wassden.lib.ears_analyzer.validate_ears_in_content", side_effect=[mock_result1, mock_result2]),
            ):
                reports = await analyzer.analyze_documents([sample_markdown_file, second_file])

            assert len(reports) == 2
            assert all(isinstance(report, EARSCoverageReport) for report in reports)

        finally:
            second_file.unlink()

    @pytest.mark.asyncio
    async def test_analyze_documents_empty_list(self, analyzer):
        """Test analyzing empty document list."""
        with pytest.raises(EARSAnalyzerError, match="No documents provided"):
            await analyzer.analyze_documents([])

    @pytest.mark.asyncio
    async def test_analyze_documents_all_fail(self, analyzer):
        """Test analyzing documents when all fail."""
        non_existent = Path("/non/existent.md")

        with pytest.raises(EARSAnalyzerError, match="All documents failed to analyze"):
            await analyzer.analyze_documents([non_existent])

    def test_aggregate_coverage_reports(self, analyzer):
        """Test aggregating coverage reports."""
        # Create sample reports
        report1 = EARSCoverageReport(
            total_requirements=2, ears_compliant=2, coverage_rate=1.0, violations=[], document_path=Path("doc1.md")
        )

        report2 = EARSCoverageReport(
            total_requirements=3,
            ears_compliant=1,
            coverage_rate=0.333,
            violations=[
                EARSViolationDetail(
                    line_number=1, requirement_text="test", violation_type="missing_trigger", suggestion=None
                ),
                EARSViolationDetail(
                    line_number=2, requirement_text="test2", violation_type="missing_outcome", suggestion=None
                ),
            ],
            document_path=Path("doc2.md"),
        )

        result = analyzer.aggregate_coverage_reports([report1, report2])

        # Verify summary
        summary = result["summary"]
        assert summary["total_documents"] == 2
        assert summary["total_requirements"] == 5
        assert summary["total_compliant"] == 3
        assert summary["overall_coverage_rate"] == 0.6
        assert summary["total_violations"] == 2

        # Verify document statistics
        doc_stats = result["document_statistics"]
        assert len(doc_stats) == 2
        assert doc_stats[0]["document_path"] == "doc1.md"
        assert doc_stats[0]["coverage_rate"] == 1.0

        # Verify violation analysis
        violation_analysis = result["violation_analysis"]
        assert violation_analysis["total_violations"] == 2
        assert violation_analysis["by_type"]["missing_trigger"] == 1
        assert violation_analysis["by_type"]["missing_outcome"] == 1

        # Verify quality metrics
        quality = result["quality_metrics"]
        assert quality["documents_with_100_percent_coverage"] == 1
        assert quality["documents_with_90_percent_coverage"] == 1
        assert abs(quality["average_coverage_rate"] - 0.6665) < 0.001

    def test_aggregate_coverage_reports_empty(self, analyzer):
        """Test aggregating empty reports list."""
        with pytest.raises(EARSAnalyzerError, match="No reports provided"):
            analyzer.aggregate_coverage_reports([])

    @pytest.mark.asyncio
    async def test_measure_ears_coverage_summary(self, analyzer, sample_markdown_file):
        """Test EARS coverage measurement with summary output.

        Implements: REQ-01 - 観点2: EARSパターン適合度を百分率で算出する
        """
        # Mock the analysis methods
        mock_report = EARSCoverageReport(
            total_requirements=2, ears_compliant=1, coverage_rate=0.5, violations=[], document_path=sample_markdown_file
        )

        analyzer.analyze_documents = AsyncMock(return_value=[mock_report])

        result = await analyzer.measure_ears_coverage([sample_markdown_file], "summary")

        # Verify summary format
        assert "coverage_summary" in result
        assert "quality_metrics" in result
        assert "document_statistics" not in result  # Should not be in summary

        # Verify coverage calculation
        assert result["coverage_summary"]["overall_coverage_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_measure_ears_coverage_detailed(self, analyzer, sample_markdown_file):
        """Test EARS coverage measurement with detailed output."""
        mock_report = EARSCoverageReport(
            total_requirements=2, ears_compliant=1, coverage_rate=0.5, violations=[], document_path=sample_markdown_file
        )

        analyzer.analyze_documents = AsyncMock(return_value=[mock_report])

        result = await analyzer.measure_ears_coverage([sample_markdown_file], "detailed")

        # Verify detailed format includes additional sections
        assert "coverage_summary" in result
        assert "document_statistics" in result
        assert "violation_analysis" in result
        assert "quality_metrics" in result

    @pytest.mark.asyncio
    async def test_measure_ears_coverage_full(self, analyzer, sample_markdown_file):
        """Test EARS coverage measurement with full output."""
        mock_violation = EARSViolationDetail(
            line_number=5,
            requirement_text="test requirement",
            violation_type="missing_trigger",
            suggestion="Add trigger condition",
        )

        mock_report = EARSCoverageReport(
            total_requirements=2,
            ears_compliant=1,
            coverage_rate=0.5,
            violations=[mock_violation],
            document_path=sample_markdown_file,
        )

        analyzer.analyze_documents = AsyncMock(return_value=[mock_report])

        result = await analyzer.measure_ears_coverage([sample_markdown_file], "full")

        # Verify full format includes document reports
        assert "coverage_summary" in result
        assert "document_reports" in result
        assert "violation_analysis" in result
        assert "quality_metrics" in result

        # Verify document report details
        doc_report = result["document_reports"][0]
        assert doc_report["coverage_rate"] == 0.5
        assert len(doc_report["violations"]) == 1

        violation = doc_report["violations"][0]
        assert violation["line_number"] == 5
        assert violation["violation_type"] == "missing_trigger"

    @pytest.mark.asyncio
    async def test_measure_ears_coverage_invalid_detail_level(self, analyzer, sample_markdown_file):
        """Test EARS coverage measurement with invalid detail level."""
        mock_report = EARSCoverageReport(
            total_requirements=1, ears_compliant=1, coverage_rate=1.0, violations=[], document_path=sample_markdown_file
        )
        analyzer.analyze_documents = AsyncMock(return_value=[mock_report])

        with pytest.raises(EARSAnalyzerError, match="Invalid output detail level"):
            await analyzer.measure_ears_coverage([sample_markdown_file], "invalid")
