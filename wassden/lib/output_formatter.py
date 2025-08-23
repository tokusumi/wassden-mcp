"""Output formatter component for experiment results.

This module provides functionality to format and output experiment results
in JSON and CSV formats for analysis and reporting.

Implements: REQ-05, TASK-02-04
"""

import csv
import json
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any

from wassden.lib.experiment import (
    ComparativeExperimentReport,
    EARSCoverageReport,
    ExperimentResult,
    LanguageDetectionReport,
    PerformanceReport,
)


class OutputFormat(str, Enum):
    """Supported output formats."""

    JSON = "json"
    CSV = "csv"


class OutputFormatterError(Exception):
    """Base exception for output formatter errors."""


class FormatConversionError(OutputFormatterError):
    """Raised when format conversion fails."""


class FileWriteError(OutputFormatterError):
    """Raised when file writing fails."""


class OutputFormatter:
    """Formatter for experiment results output."""

    def __init__(self, max_retries: int = 3) -> None:
        """Initialize output formatter.

        Args:
            max_retries: Maximum number of retries for file operations

        Implements: REQ-05 - システムは、実験結果を出力するとき、JSON形式とCSV形式を提供すること
        """
        self.max_retries = max_retries

    def format_to_json(self, data: Any, pretty: bool = True) -> str:
        """Format data to JSON string.

        Args:
            data: Data to format (can be dict, list, or Pydantic model)
            pretty: Whether to use pretty printing with indentation

        Returns:
            JSON formatted string

        Raises:
            FormatConversionError: If JSON conversion fails

        Implements: REQ-05 - 観点1: 構造化されたJSON形式での出力
        """
        try:
            # Handle Pydantic models
            if hasattr(data, "model_dump"):
                data = data.model_dump()
            elif hasattr(data, "dict"):  # Older Pydantic compatibility
                data = data.dict()

            # Convert Path objects to strings
            data = self._convert_paths_to_strings(data)

            # Format to JSON
            if pretty:
                return json.dumps(data, indent=2, ensure_ascii=False, default=str)
            return json.dumps(data, ensure_ascii=False, default=str)

        except Exception as e:
            raise FormatConversionError(f"Failed to convert to JSON: {e}") from e

    def format_to_csv(self, data: Any, headers: list[str] | None = None) -> str:
        """Format data to CSV string.

        Args:
            data: Data to format (dict, list of dicts, or Pydantic model)
            headers: Optional custom headers for CSV

        Returns:
            CSV formatted string

        Raises:
            FormatConversionError: If CSV conversion fails

        Implements: REQ-05 - 観点2: 表形式のCSV形式での出力
        """
        try:
            # Handle Pydantic models
            if hasattr(data, "model_dump"):
                data = data.model_dump()
            elif hasattr(data, "dict"):
                data = data.dict()

            # Convert to list of dictionaries for CSV
            if isinstance(data, dict):
                # If it's a single dict, wrap in list; otherwise flatten nested structure
                rows = [data] if not any(isinstance(v, list) for v in data.values()) else self._flatten_for_csv(data)
            elif isinstance(data, list):
                rows = data
            else:
                rows = [{"value": str(data)}]

            if not rows:
                return ""

            # Convert Path objects to strings
            rows = self._convert_paths_to_strings(rows)

            # Generate CSV
            output = StringIO()
            if headers is None:
                headers = list(rows[0].keys()) if rows else []

            writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

            return output.getvalue()

        except Exception as e:
            raise FormatConversionError(f"Failed to convert to CSV: {e}") from e

    def _flatten_for_csv(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Flatten nested dictionary structure for CSV output.

        Args:
            data: Nested dictionary to flatten

        Returns:
            List of flattened dictionaries suitable for CSV
        """
        if "results" in data and isinstance(data["results"], list):
            return self._flatten_results_report(data)
        if "details" in data and isinstance(data["details"], list):
            return self._flatten_details_report(data)
        if "violations" in data and isinstance(data["violations"], list):
            return self._flatten_violations_report(data)
        # Generic flattening
        return [self._flatten_dict(data)]

    def _flatten_results_report(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Flatten reports with results list (e.g., LanguageDetectionReport)."""
        rows = []
        accuracy_keys = ["accuracy_rate", "japanese_accuracy", "english_accuracy"]

        for result in data["results"]:
            row = {}
            # Add top-level metrics
            for key in accuracy_keys:
                if key in data:
                    row[key] = data[key]
            # Add result details
            if isinstance(result, dict):
                row.update(result)
            rows.append(row)
        return rows

    def _flatten_details_report(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Flatten reports with details list (e.g., PerformanceReport)."""
        rows = []
        summary_keys = [
            "total_executions",
            "successful_executions",
            "failed_executions",
            "average_wall_time_ms",
            "average_cpu_time_ms",
            "average_memory_mb",
            "peak_memory_mb",
        ]

        for detail in data["details"]:
            row = {}
            # Add summary metrics
            for key in summary_keys:
                if key in data:
                    row[key] = data[key]
            # Add detail information
            if isinstance(detail, dict):
                row.update(detail)
            rows.append(row)
        return rows

    def _flatten_violations_report(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Flatten EARS coverage reports with violations."""
        rows = []
        base_row = {k: v for k, v in data.items() if k != "violations"}

        for violation in data["violations"]:
            row = base_row.copy()
            if isinstance(violation, dict):
                row.update(violation)
            rows.append(row)

        # If no violations, still output the summary
        if not data["violations"]:
            rows.append(base_row)

        return rows

    def _flatten_dict(self, d: dict[str, Any], parent_key: str = "", sep: str = "_") -> dict[str, Any]:
        """Recursively flatten a nested dictionary.

        Args:
            d: Dictionary to flatten
            parent_key: Parent key for nested items
            sep: Separator for concatenated keys

        Returns:
            Flattened dictionary
        """
        items: list[tuple[str, Any]] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert list to string representation for CSV
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)

    def _convert_paths_to_strings(self, obj: Any) -> Any:
        """Recursively convert Path objects to strings.

        Args:
            obj: Object to process

        Returns:
            Object with Path objects converted to strings
        """
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, dict):
            return {k: self._convert_paths_to_strings(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._convert_paths_to_strings(item) for item in obj]
        if isinstance(obj, tuple):
            return tuple(self._convert_paths_to_strings(item) for item in obj)
        return obj

    def save_to_file(self, data: Any, file_path: Path, format_type: OutputFormat) -> None:
        """Save formatted data to file with retry logic.

        Args:
            data: Data to save
            file_path: Path to output file
            format_type: Output format type

        Raises:
            FileWriteError: If file writing fails after retries

        Implements: Design - ファイル書き込み失敗時のリトライ(最大3回)
        """
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Format data based on type
        if format_type == OutputFormat.JSON:
            content = self.format_to_json(data)
            file_path = file_path.with_suffix(".json")
        elif format_type == OutputFormat.CSV:
            content = self.format_to_csv(data)
            file_path = file_path.with_suffix(".csv")
        else:
            raise FormatConversionError(f"Unsupported format: {format_type}")

        # Write with retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                file_path.write_text(content, encoding="utf-8")
                return
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Try with temporary file as fallback
                    temp_path = file_path.with_suffix(f".tmp{attempt}")
                    try:
                        temp_path.write_text(content, encoding="utf-8")
                        temp_path.replace(file_path)
                        return
                    except Exception:
                        continue

        raise FileWriteError(f"Failed to write file after {self.max_retries} attempts: {last_error}") from last_error

    def format_experiment_result(self, result: ExperimentResult, format_type: OutputFormat) -> str:
        """Format ExperimentResult to specified format.

        Args:
            result: Experiment result to format
            format_type: Output format type

        Returns:
            Formatted string

        Raises:
            FormatConversionError: If formatting fails
        """
        if format_type == OutputFormat.JSON:
            return self.format_to_json(result)
        if format_type == OutputFormat.CSV:
            # Create a flattened view for CSV
            data = result.model_dump()
            return self.format_to_csv(data)
        raise FormatConversionError(f"Unsupported format: {format_type}")

    def format_performance_report(self, report: PerformanceReport, format_type: OutputFormat) -> str:
        """Format PerformanceReport to specified format.

        Args:
            report: Performance report to format
            format_type: Output format type

        Returns:
            Formatted string
        """
        if format_type == OutputFormat.JSON:
            return self.format_to_json(report)
        if format_type == OutputFormat.CSV:
            data = report.model_dump()
            return self.format_to_csv(data)
        raise FormatConversionError(f"Unsupported format: {format_type}")

    def format_ears_coverage_report(self, report: EARSCoverageReport, format_type: OutputFormat) -> str:
        """Format EARSCoverageReport to specified format.

        Args:
            report: EARS coverage report to format
            format_type: Output format type

        Returns:
            Formatted string
        """
        if format_type == OutputFormat.JSON:
            return self.format_to_json(report)
        if format_type == OutputFormat.CSV:
            data = report.model_dump()
            return self.format_to_csv(data)
        raise FormatConversionError(f"Unsupported format: {format_type}")

    def format_language_detection_report(self, report: LanguageDetectionReport, format_type: OutputFormat) -> str:
        """Format LanguageDetectionReport to specified format.

        Args:
            report: Language detection report to format
            format_type: Output format type

        Returns:
            Formatted string
        """
        if format_type == OutputFormat.JSON:
            return self.format_to_json(report)
        if format_type == OutputFormat.CSV:
            data = report.model_dump()
            return self.format_to_csv(data)
        raise FormatConversionError(f"Unsupported format: {format_type}")

    def format_comparative_experiment_report(
        self, report: ComparativeExperimentReport, format_type: OutputFormat
    ) -> str:
        """Format ComparativeExperimentReport to specified format.

        Args:
            report: Comparative experiment report to format
            format_type: Output format type

        Returns:
            Formatted string
        """
        if format_type == OutputFormat.JSON:
            return self.format_to_json(report)
        if format_type == OutputFormat.CSV:
            # For CSV, focus on the comparison results as the most important data
            comparison_data = []
            for comparison in report.comparisons:
                row = {
                    "metric_name": comparison.metric_name,
                    "baseline_experiment_id": comparison.baseline_experiment_id,
                    "comparison_experiment_id": comparison.comparison_experiment_id,
                    "baseline_mean": comparison.statistical_comparison.baseline_mean,
                    "comparison_mean": comparison.statistical_comparison.comparison_mean,
                    "improvement_percentage": comparison.improvement_percentage,
                    "p_value": comparison.statistical_comparison.p_value,
                    "is_significant": comparison.statistical_comparison.is_significant,
                    "effect_size": comparison.statistical_comparison.effect_size,
                    "confidence_interval_lower": comparison.statistical_comparison.confidence_interval_lower,
                    "confidence_interval_upper": comparison.statistical_comparison.confidence_interval_upper,
                }
                comparison_data.append(row)

            return self.format_to_csv(comparison_data)
        raise FormatConversionError(f"Unsupported format: {format_type}")
