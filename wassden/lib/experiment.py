"""Experiment runner component for wassden validation framework.

This module provides experiment functionality for EARS compliance measurement,
performance testing, language detection accuracy, and comparative analysis.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, Field


class ExperimentType(str, Enum):
    """Types of experiments supported by the runner."""

    EARS_COVERAGE = "ears_coverage"
    PERFORMANCE = "performance"
    LANGUAGE_DETECTION = "language_detection"
    COMPARATIVE = "comparative"


class OutputFormat(str, Enum):
    """Supported output formats for experiment results."""

    JSON = "json"
    CSV = "csv"
    YAML = "yaml"


class ExperimentStatus(str, Enum):
    """Status of experiment execution."""

    PENDING = "pending"
    RUNNING = "running"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExperimentConfig(BaseModel):
    """Configuration for experiment execution."""

    experiment_type: ExperimentType = Field(description="Type of experiment to run")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Experiment-specific parameters")
    output_format: list[OutputFormat] = Field(default=[OutputFormat.JSON], description="Output formats")
    timeout_seconds: int = Field(default=600, description="Maximum execution time in seconds")
    memory_limit_mb: int = Field(default=100, description="Memory limit in megabytes")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class StatisticalSummary(BaseModel):
    """Statistical summary of experiment results."""

    mean: float = Field(description="Mean value")
    variance: float = Field(description="Variance")
    std_dev: float = Field(description="Standard deviation")
    confidence_interval: tuple[float, float] = Field(description="95% confidence interval")
    sample_size: int = Field(description="Number of samples")
    min_value: float = Field(description="Minimum value")
    max_value: float = Field(description="Maximum value")


class EARSViolationDetail(BaseModel):
    """Details of an EARS pattern violation."""

    line_number: int = Field(description="Line number in document")
    requirement_text: str = Field(description="Original requirement text")
    violation_type: str = Field(description="Type of EARS violation")
    suggestion: str | None = Field(default=None, description="Suggested correction")


class EARSCoverageReport(BaseModel):
    """Report of EARS coverage analysis."""

    total_requirements: int = Field(description="Total number of requirements found")
    ears_compliant: int = Field(description="Number of EARS-compliant requirements")
    coverage_rate: float = Field(description="EARS compliance rate (0.0-1.0)")
    violations: list[EARSViolationDetail] = Field(default_factory=list, description="Detected violations")
    document_path: Path = Field(description="Path to analyzed document")


class PerformanceMetrics(BaseModel):
    """Performance measurement results."""

    execution_time_ms: float = Field(description="Execution time in milliseconds")
    memory_usage_bytes: int = Field(description="Peak memory usage in bytes")
    cpu_usage_percent: float = Field(description="Average CPU usage percentage")
    operation_name: str = Field(description="Name of measured operation")


class PerformanceDetail(BaseModel):
    """Detailed performance measurement for a single execution."""

    wall_time_ms: float = Field(description="Wall clock time in milliseconds")
    cpu_time_ms: float = Field(description="CPU time in milliseconds")
    memory_used_mb: float = Field(description="Memory used in megabytes")
    peak_memory_mb: float = Field(description="Peak memory usage in megabytes")
    function_name: str = Field(description="Name of profiled function")
    success: bool = Field(description="Whether execution was successful")
    error_message: str | None = Field(default=None, description="Error message if failed")


class PerformanceReport(BaseModel):
    """Report of performance analysis."""

    total_executions: int = Field(description="Total number of executions")
    successful_executions: int = Field(description="Number of successful executions")
    failed_executions: int = Field(description="Number of failed executions")
    average_wall_time_ms: float = Field(description="Average wall time in milliseconds")
    average_cpu_time_ms: float = Field(description="Average CPU time in milliseconds")
    average_memory_mb: float = Field(description="Average memory usage in megabytes")
    peak_memory_mb: float = Field(description="Peak memory usage in megabytes")
    details: list[PerformanceDetail] = Field(description="Detailed measurements")
    result_data: Any = Field(default=None, description="Execution result data")


class LanguageDetectionResult(BaseModel):
    """Result of language detection accuracy test."""

    document_path: Path = Field(description="Path to tested document")
    expected_language: str = Field(description="Expected language")
    detected_language: str = Field(description="Actually detected language")
    confidence_score: float = Field(description="Detection confidence (0.0-1.0)")
    is_correct: bool = Field(description="Whether detection was correct")


class LanguageDetectionReport(BaseModel):
    """Report of language detection accuracy analysis."""

    results: list[LanguageDetectionResult] = Field(description="Individual detection results")
    accuracy_rate: float = Field(description="Overall accuracy rate (0.0-1.0)")
    japanese_accuracy: float = Field(description="Japanese detection accuracy")
    english_accuracy: float = Field(description="English detection accuracy")
    statistics: StatisticalSummary = Field(description="Confidence score statistics")


class StatisticalComparison(BaseModel):
    """Statistical comparison between two groups of data."""

    baseline_mean: float = Field(description="Mean of baseline group")
    comparison_mean: float = Field(description="Mean of comparison group")
    baseline_std: float = Field(description="Standard deviation of baseline group")
    comparison_std: float = Field(description="Standard deviation of comparison group")
    t_statistic: float = Field(description="T-test statistic")
    p_value: float = Field(description="P-value from statistical test")
    degrees_of_freedom: int = Field(description="Degrees of freedom")
    effect_size: float = Field(description="Cohen's d effect size")
    is_significant: bool = Field(description="Whether difference is statistically significant (p < 0.05)")
    confidence_interval_lower: float = Field(description="Lower bound of 95% confidence interval for difference")
    confidence_interval_upper: float = Field(description="Upper bound of 95% confidence interval for difference")


class ComparisonResult(BaseModel):
    """Result of comparison between two experiments."""

    baseline_experiment_id: str = Field(description="ID of baseline experiment")
    comparison_experiment_id: str = Field(description="ID of comparison experiment")
    metric_name: str = Field(description="Name of compared metric")
    baseline_values: list[float] = Field(description="Values from baseline experiment")
    comparison_values: list[float] = Field(description="Values from comparison experiment")
    statistical_comparison: StatisticalComparison = Field(description="Statistical analysis results")
    improvement_percentage: float = Field(description="Percentage improvement (negative if worse)")


class ComparativeExperimentReport(BaseModel):
    """Report of comparative experiment analysis."""

    baseline_experiment: "ExperimentResult" = Field(description="Baseline experiment result")
    comparison_experiments: list["ExperimentResult"] = Field(description="Comparison experiment results")
    comparisons: list[ComparisonResult] = Field(description="Statistical comparison results")
    summary_statistics: dict[str, Any] = Field(description="Overall summary statistics")
    recommendations: list[str] = Field(default_factory=list, description="Analysis recommendations")


class ExperimentResult(BaseModel):
    """Result of experiment execution."""

    experiment_id: str = Field(description="Unique experiment identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Execution timestamp")
    config: ExperimentConfig = Field(description="Experiment configuration used")
    status: ExperimentStatus = Field(description="Execution status")
    duration_seconds: float = Field(description="Total execution time")

    # Type-specific results (only one will be populated based on experiment_type)
    ears_report: EARSCoverageReport | None = Field(default=None, description="EARS coverage results")
    performance_report: PerformanceReport | None = Field(default=None, description="Performance results")
    language_report: LanguageDetectionReport | None = Field(default=None, description="Language detection results")

    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error_message: str | None = Field(default=None, description="Error message if failed")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders: ClassVar = {datetime: lambda v: v.isoformat(), Path: lambda v: str(v)}
