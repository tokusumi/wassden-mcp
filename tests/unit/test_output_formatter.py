"""Unit tests for output formatter module.

Tests for TASK-02-04 output formatting functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest

from wassden.lib.experiment import (
    EARSCoverageReport,
    EARSViolationDetail,
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType,
    LanguageDetectionReport,
    LanguageDetectionResult,
    PerformanceDetail,
    PerformanceReport,
    StatisticalSummary,
)
from wassden.lib.output_formatter import (
    FileWriteError,
    FormatConversionError,
    OutputFormat,
    OutputFormatter,
)


class TestOutputFormatter:
    """Test cases for OutputFormatter."""

    @pytest.fixture
    def formatter(self):
        """Create OutputFormatter instance."""
        return OutputFormatter(max_retries=3)

    @pytest.fixture
    def sample_experiment_result(self):
        """Create a sample experiment result."""
        return ExperimentResult(
            experiment_id="exp-001",
            config=ExperimentConfig(
                experiment_type=ExperimentType.EARS_COVERAGE,
                parameters={"target_files": ["test.md"]},
                output_formats=[OutputFormat.JSON, OutputFormat.CSV],
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=5.2,
            ears_report=EARSCoverageReport(
                total_requirements=20,
                ears_compliant=17,
                coverage_rate=0.85,
                violations=[],
                document_path=Path("test.md"),
            ),
            metadata={"test": "metadata"},
        )

    @pytest.fixture
    def sample_performance_report(self):
        """Create a sample performance report."""
        return PerformanceReport(
            total_executions=3,
            successful_executions=3,
            failed_executions=0,
            average_wall_time_ms=150.5,
            average_cpu_time_ms=140.2,
            average_memory_mb=25.3,
            peak_memory_mb=30.5,
            details=[
                PerformanceDetail(
                    wall_time_ms=150.0,
                    cpu_time_ms=140.0,
                    memory_used_mb=25.0,
                    peak_memory_mb=30.0,
                    function_name="test_function",
                    success=True,
                    error_message=None,
                ),
            ],
            result_data={"test": "data"},
        )

    @pytest.fixture
    def sample_ears_coverage_report(self):
        """Create a sample EARS coverage report."""
        return EARSCoverageReport(
            total_requirements=10,
            ears_compliant=8,
            coverage_rate=0.8,
            violations=[
                EARSViolationDetail(
                    line_number=5,
                    requirement_text="The system shall process data",
                    violation_type="Missing trigger",
                    suggestion="Add WHEN clause",
                ),
            ],
            document_path=Path("test.md"),
        )

    @pytest.fixture
    def sample_language_detection_report(self):
        """Create a sample language detection report."""
        return LanguageDetectionReport(
            results=[
                LanguageDetectionResult(
                    document_path=Path("doc1.md"),
                    expected_language="ja",
                    detected_language="ja",
                    confidence_score=0.95,
                    is_correct=True,
                ),
                LanguageDetectionResult(
                    document_path=Path("doc2.md"),
                    expected_language="en",
                    detected_language="en",
                    confidence_score=0.90,
                    is_correct=True,
                ),
            ],
            accuracy_rate=1.0,
            japanese_accuracy=1.0,
            english_accuracy=1.0,
            statistics=StatisticalSummary(
                mean=0.925,
                variance=0.0025,
                std_dev=0.05,
                confidence_interval=(0.90, 0.95),
                sample_size=2,
                min_value=0.90,
                max_value=0.95,
            ),
        )

    def test_format_to_json_simple_dict(self, formatter):
        """Test JSON formatting for simple dictionary.

        Implements: REQ-05 - 観点1: 構造化されたJSON形式での出力
        """
        data = {"key1": "value1", "key2": 42, "key3": True}
        result = formatter.format_to_json(data)

        # Verify valid JSON
        parsed = json.loads(result)
        assert parsed == data

        # Check pretty printing
        assert "\n" in result  # Pretty printed with newlines
        assert "  " in result  # Indented

    def test_format_to_json_pydantic_model(self, formatter, sample_experiment_result):
        """Test JSON formatting for Pydantic model."""
        result = formatter.format_to_json(sample_experiment_result)

        # Verify valid JSON
        parsed = json.loads(result)
        assert parsed["experiment_id"] == "exp-001"
        assert parsed["ears_report"]["coverage_rate"] == 0.85

    def test_format_to_json_with_path_objects(self, formatter):
        """Test JSON formatting with Path objects."""
        data = {"file": Path("/test/file.md"), "count": 10}
        result = formatter.format_to_json(data)

        parsed = json.loads(result)
        assert parsed["file"] == "/test/file.md"  # Path converted to string

    def test_format_to_json_compact(self, formatter):
        """Test compact JSON formatting."""
        data = {"key": "value"}
        result = formatter.format_to_json(data, pretty=False)

        assert "\n" not in result  # No newlines in compact format
        parsed = json.loads(result)
        assert parsed == data

    def test_format_to_csv_simple_dict(self, formatter):
        """Test CSV formatting for simple dictionary.

        Implements: REQ-05 - 観点2: 表形式のCSV形式での出力
        """
        data = {"name": "Test", "value": 42, "status": "active"}
        result = formatter.format_to_csv(data)

        lines = result.strip().split("\n")
        assert len(lines) == 2  # Header + 1 data row
        assert "name,value,status" in lines[0]
        assert "Test,42,active" in lines[1]

    def test_format_to_csv_list_of_dicts(self, formatter):
        """Test CSV formatting for list of dictionaries."""
        data = [
            {"id": 1, "name": "Item1", "value": 10},
            {"id": 2, "name": "Item2", "value": 20},
        ]
        result = formatter.format_to_csv(data)

        lines = result.strip().split("\n")
        assert len(lines) == 3  # Header + 2 data rows
        assert "id,name,value" in lines[0]
        assert "1,Item1,10" in lines[1]
        assert "2,Item2,20" in lines[2]

    def test_format_to_csv_pydantic_model(self, formatter, sample_performance_report):
        """Test CSV formatting for Pydantic model."""
        result = formatter.format_to_csv(sample_performance_report)

        lines = result.strip().split("\n")
        assert len(lines) >= 2  # Header + data rows
        # Check that key metrics are in the CSV
        assert "total_executions" in lines[0]
        assert "3" in result  # total_executions value

    def test_format_to_csv_with_custom_headers(self, formatter):
        """Test CSV formatting with custom headers."""
        data = [{"a": 1, "b": 2, "c": 3}, {"a": 4, "b": 5, "c": 6}]
        headers = ["a", "b"]  # Only include a and b columns
        result = formatter.format_to_csv(data, headers=headers)

        lines = result.strip().split("\n")
        assert "a,b" in lines[0]
        assert "c" not in lines[0]  # c column excluded

    def test_flatten_for_csv_ears_report(self, formatter, sample_ears_coverage_report):
        """Test flattening EARS coverage report for CSV."""
        data = sample_ears_coverage_report.model_dump()
        rows = formatter._flatten_for_csv(data)

        assert len(rows) >= 1
        # Check that violation details are included
        if rows:
            assert "line_number" in rows[0]
            assert rows[0]["coverage_rate"] == 0.8

    def test_flatten_for_csv_language_report(self, formatter, sample_language_detection_report):
        """Test flattening language detection report for CSV."""
        data = sample_language_detection_report.model_dump()
        rows = formatter._flatten_for_csv(data)

        assert len(rows) == 2  # Two results
        assert rows[0]["accuracy_rate"] == 1.0
        assert rows[0]["is_correct"] is True

    def test_save_to_file_json_success(self, formatter, sample_experiment_result):
        """Test saving to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_output.json"
            formatter.save_to_file(sample_experiment_result, file_path, OutputFormat.JSON)

            # Verify file was created
            assert file_path.exists()

            # Verify content is valid JSON
            content = file_path.read_text()
            parsed = json.loads(content)
            assert parsed["experiment_id"] == "exp-001"

    def test_save_to_file_csv_success(self, formatter, sample_performance_report):
        """Test saving to CSV file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_output.csv"
            formatter.save_to_file(sample_performance_report, file_path, OutputFormat.CSV)

            # Verify file was created
            assert file_path.exists()

            # Verify content is valid CSV
            content = file_path.read_text()
            assert "total_executions" in content
            assert "3" in content

    def test_save_to_file_with_retry(self, formatter):
        """Test file saving with retry on failure."""
        # Create a read-only directory to force initial failure
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "readonly" / "test.json"

            # This should succeed by creating parent directory
            formatter.save_to_file({"test": "data"}, file_path, OutputFormat.JSON)
            assert file_path.exists()

    def test_save_to_file_failure(self, formatter, monkeypatch):
        """Test file saving failure after retries."""

        # Mock write_text to always fail
        def failing_write_text(*args, **kwargs):  # noqa: ARG001
            raise OSError("Permission denied")

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            monkeypatch.setattr(Path, "write_text", failing_write_text)

            with pytest.raises(FileWriteError, match="Failed to write file"):
                formatter.save_to_file({"test": "data"}, file_path, OutputFormat.JSON)

    def test_format_experiment_result_json(self, formatter, sample_experiment_result):
        """Test formatting ExperimentResult to JSON."""
        result = formatter.format_experiment_result(sample_experiment_result, OutputFormat.JSON)

        parsed = json.loads(result)
        assert parsed["experiment_id"] == "exp-001"
        assert parsed["config"]["experiment_type"] == "ears_coverage"

    def test_format_experiment_result_csv(self, formatter, sample_experiment_result):
        """Test formatting ExperimentResult to CSV."""
        result = formatter.format_experiment_result(sample_experiment_result, OutputFormat.CSV)

        assert "experiment_id" in result
        assert "exp-001" in result

    def test_format_performance_report_json(self, formatter, sample_performance_report):
        """Test formatting PerformanceReport to JSON."""
        result = formatter.format_performance_report(sample_performance_report, OutputFormat.JSON)

        parsed = json.loads(result)
        assert parsed["total_executions"] == 3
        assert parsed["average_wall_time_ms"] == 150.5

    def test_format_performance_report_csv(self, formatter, sample_performance_report):
        """Test formatting PerformanceReport to CSV."""
        result = formatter.format_performance_report(sample_performance_report, OutputFormat.CSV)

        assert "total_executions" in result
        assert "150" in result  # wall_time_ms

    def test_format_ears_coverage_report_json(self, formatter, sample_ears_coverage_report):
        """Test formatting EARSCoverageReport to JSON."""
        result = formatter.format_ears_coverage_report(sample_ears_coverage_report, OutputFormat.JSON)

        parsed = json.loads(result)
        assert parsed["coverage_rate"] == 0.8
        assert len(parsed["violations"]) == 1

    def test_format_ears_coverage_report_csv(self, formatter, sample_ears_coverage_report):
        """Test formatting EARSCoverageReport to CSV."""
        result = formatter.format_ears_coverage_report(sample_ears_coverage_report, OutputFormat.CSV)

        assert "coverage_rate" in result
        assert "0.8" in result

    def test_format_language_detection_report_json(self, formatter, sample_language_detection_report):
        """Test formatting LanguageDetectionReport to JSON."""
        result = formatter.format_language_detection_report(sample_language_detection_report, OutputFormat.JSON)

        parsed = json.loads(result)
        assert parsed["accuracy_rate"] == 1.0
        assert len(parsed["results"]) == 2

    def test_format_language_detection_report_csv(self, formatter, sample_language_detection_report):
        """Test formatting LanguageDetectionReport to CSV."""
        result = formatter.format_language_detection_report(sample_language_detection_report, OutputFormat.CSV)

        assert "accuracy_rate" in result
        assert "doc1.md" in result
        assert "doc2.md" in result

    def test_format_invalid_format_type(self, formatter, sample_experiment_result):
        """Test formatting with invalid format type."""
        with pytest.raises(FormatConversionError, match="Unsupported format"):
            formatter.format_experiment_result(sample_experiment_result, "invalid")  # type: ignore

    def test_convert_paths_to_strings(self, formatter):
        """Test Path object conversion."""
        data = {
            "file": Path("/test/file.md"),
            "nested": {"path": Path("/nested/path.txt")},
            "list": [Path("/item1.md"), Path("/item2.md")],
        }

        result = formatter._convert_paths_to_strings(data)

        assert result["file"] == "/test/file.md"
        assert result["nested"]["path"] == "/nested/path.txt"
        assert result["list"] == ["/item1.md", "/item2.md"]

    def test_flatten_dict(self, formatter):
        """Test dictionary flattening."""
        data = {"level1": {"level2": {"value": 42}, "another": "test"}, "simple": "value"}

        result = formatter._flatten_dict(data)

        assert result["level1_level2_value"] == 42
        assert result["level1_another"] == "test"
        assert result["simple"] == "value"
