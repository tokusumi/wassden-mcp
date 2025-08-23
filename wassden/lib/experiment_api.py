"""API interface for experiment execution and measurement operations.

This module provides the core API functions required by TASK-02-05:
- run_experiment: Generic experiment runner
- measure_ears_coverage: EARS coverage measurement API
- measure_performance: Performance measurement API

Implements: REQ-08, TASK-02-05
"""

from pathlib import Path
from typing import Any

from wassden.language_types import Language
from wassden.lib.comparative_analyzer import ComparativeAnalyzer
from wassden.lib.constants import DEFAULT_CONFIG_PATH
from wassden.lib.ears_analyzer import EARSAnalyzer
from wassden.lib.experiment import (
    EARSCoverageReport,
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType,
    OutputFormat,
    PerformanceReport,
)
from wassden.lib.experiment_manager import ExperimentManager
from wassden.lib.language_detector_analyzer import LanguageDetectorAnalyzer
from wassden.lib.output_formatter import OutputFormat as FormatterOutputFormat
from wassden.lib.output_formatter import OutputFormatter
from wassden.lib.performance_profiler import PerformanceProfiler


class ExperimentAPIError(Exception):
    """Base exception for experiment API errors."""


class InvalidParametersError(ExperimentAPIError):
    """Raised when API parameters are invalid."""


class ExecutionError(ExperimentAPIError):
    """Raised when experiment execution fails."""


async def run_experiment(
    experiment_type: ExperimentType,
    parameters: dict[str, Any] | None = None,
    output_format: list[OutputFormat] | None = None,
    timeout_seconds: int = 600,
    memory_limit_mb: int = 100,
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> ExperimentResult:
    """Run experiment with specified configuration.

    Args:
        experiment_type: Type of experiment to run
        parameters: Experiment-specific parameters
        output_format: Output format(s) for results
        timeout_seconds: Maximum execution time
        memory_limit_mb: Memory usage limit

    Returns:
        Experiment result with status and metadata

    Raises:
        InvalidParametersError: If parameters are invalid
        ExecutionError: If experiment execution fails

    Implements: REQ-08 - システムは、実験実行時、CLI経由でrun_experiment関数を提供すること
    """
    try:
        # Validate parameters
        if parameters is None:
            parameters = {}
        if output_format is None:
            output_format = [OutputFormat.JSON]

        # Create configuration
        config = ExperimentConfig(
            experiment_type=experiment_type,
            parameters=parameters,
            output_format=output_format,
            timeout_seconds=timeout_seconds,
            memory_limit_mb=memory_limit_mb,
        )

        # Execute experiment based on type
        manager = ExperimentManager(config_dir=config_path)

        if experiment_type == ExperimentType.EARS_COVERAGE:
            return await _run_ears_coverage_experiment(config, manager)
        if experiment_type == ExperimentType.PERFORMANCE:
            return await _run_performance_experiment(config, manager)
        if experiment_type == ExperimentType.LANGUAGE_DETECTION:
            return await _run_language_detection_experiment(config, manager)
        if experiment_type == ExperimentType.COMPARATIVE:
            return await _run_comparative_experiment(config, manager)

        _raise_unsupported_experiment_type(experiment_type)

    except Exception as e:
        if isinstance(e, InvalidParametersError | ExecutionError):
            raise
        raise ExecutionError(f"Experiment execution failed: {e}") from e


async def measure_ears_coverage(
    input_paths: list[Path],
    _language: Language = Language.JAPANESE,
    _output_detail_level: str = "summary",
) -> EARSCoverageReport:
    """Measure EARS coverage for specified documents.

    Args:
        input_paths: Paths to markdown documents to analyze
        language: Language for analysis (auto-detected if None)
        output_detail_level: Level of detail in output ("summary" or "detailed")

    Returns:
        EARS coverage analysis report

    Raises:
        InvalidParametersError: If input paths are invalid
        ExecutionError: If analysis fails

    Implements: REQ-08 - システムは、実験実行時、CLI経由でmeasure_ears_coverage関数を提供すること
    """
    try:
        _validate_input_paths(input_paths)

        # Validate all paths exist
        for path in input_paths:
            _validate_path_exists(path)

        analyzer = EARSAnalyzer()

        # For multiple files, analyze each and combine results
        if len(input_paths) == 1:
            return await analyzer.analyze_document(input_paths[0])

        # Combine multiple document analyses
        all_reports = []
        for path in input_paths:
            report = await analyzer.analyze_document(path)
            all_reports.append(report)

        # Create combined report
        total_requirements = sum(r.total_requirements for r in all_reports)
        total_ears_compliant = sum(r.ears_compliant for r in all_reports)

        combined_violations = []
        for report in all_reports:
            combined_violations.extend(report.violations)

        coverage_rate = (total_ears_compliant / total_requirements) if total_requirements > 0 else 0.0

        return EARSCoverageReport(
            document_path=input_paths[0],  # Use first path as representative
            total_requirements=total_requirements,
            ears_compliant=total_ears_compliant,
            coverage_rate=coverage_rate,
            violations=combined_violations,
        )

    except Exception as e:
        if isinstance(e, InvalidParametersError | ExecutionError):
            raise
        raise ExecutionError(f"EARS coverage measurement failed: {e}") from e


async def measure_performance(
    operation_name: str,
    measurement_rounds: int = 5,
    warmup_rounds: int = 2,
    memory_profiling: bool = True,
    custom_operation: Any = None,
) -> PerformanceReport:
    """Measure performance for specified operation.

    Args:
        operation_name: Name of operation to measure
        measurement_rounds: Number of measurement rounds
        warmup_rounds: Number of warmup rounds
        memory_profiling: Whether to profile memory usage
        custom_operation: Custom operation function to measure

    Returns:
        Performance measurement report

    Raises:
        InvalidParametersError: If parameters are invalid
        ExecutionError: If measurement fails

    Implements: REQ-08 - システムは、実験実行時、CLI経由でmeasure_performance関数を提供すること
    """
    try:
        _validate_measurement_rounds(measurement_rounds)
        _validate_warmup_rounds(warmup_rounds)

        profiler = PerformanceProfiler()

        # If custom operation provided, use it; otherwise use predefined operations
        if custom_operation is not None:
            return await profiler.profile_custom_operation(
                custom_operation,
                operation_name,
                rounds=measurement_rounds,
                warmup=warmup_rounds,
                memory_profiling=memory_profiling,
            )

        # Use predefined operation based on name
        return await profiler.profile_operation(
            operation_name,
            rounds=measurement_rounds,
            warmup=warmup_rounds,
            memory_profiling=memory_profiling,
        )

    except Exception as e:
        if isinstance(e, InvalidParametersError | ExecutionError):
            raise
        raise ExecutionError(f"Performance measurement failed: {e}") from e


# Internal experiment runners


async def _run_ears_coverage_experiment(config: ExperimentConfig, manager: ExperimentManager) -> ExperimentResult:
    """Run EARS coverage experiment."""
    result = manager.create_experiment_result(config)

    try:
        manager.update_experiment_status(result.experiment_id, ExperimentStatus.RUNNING)

        # Extract parameters
        input_paths = config.parameters.get("input_paths", [])
        _validate_input_paths_parameter(input_paths)

        # Convert string paths to Path objects
        paths = [Path(p) for p in input_paths]

        # Run analysis
        report = await measure_ears_coverage(
            input_paths=paths,
            _language=Language.JAPANESE,
            _output_detail_level=config.parameters.get("output_detail_level", "summary"),
        )

        # Format output if requested
        formatter = OutputFormatter()
        formatted_outputs = {}
        for fmt in config.output_format:
            if fmt == OutputFormat.JSON:
                formatted_outputs["json"] = formatter.format_ears_coverage_report(report, FormatterOutputFormat.JSON)
            elif fmt == OutputFormat.CSV:
                formatted_outputs["csv"] = formatter.format_ears_coverage_report(report, FormatterOutputFormat.CSV)

        metadata = {
            "report": report.model_dump(),
            "formatted_outputs": formatted_outputs,
        }

        manager.update_experiment_status(result.experiment_id, ExperimentStatus.COMPLETED, metadata=metadata)

    except Exception as e:
        manager.update_experiment_status(result.experiment_id, ExperimentStatus.FAILED, error_message=str(e))
        raise ExecutionError(f"EARS coverage experiment failed: {e}") from e

    return manager.get_experiment_result(result.experiment_id) or result


async def _run_performance_experiment(config: ExperimentConfig, manager: ExperimentManager) -> ExperimentResult:
    """Run performance measurement experiment."""
    result = manager.create_experiment_result(config)

    try:
        manager.update_experiment_status(result.experiment_id, ExperimentStatus.RUNNING)

        # Extract parameters
        operation_name = config.parameters.get("operation_name", "default_operation")
        measurement_rounds = config.parameters.get("measurement_rounds", 5)
        warmup_rounds = config.parameters.get("warmup_rounds", 2)
        memory_profiling = config.parameters.get("memory_profiling", True)

        # Validate parameters
        _validate_measurement_rounds(measurement_rounds)
        _validate_warmup_rounds(warmup_rounds)

        # Run performance measurement
        report = await measure_performance(
            operation_name=operation_name,
            measurement_rounds=measurement_rounds,
            warmup_rounds=warmup_rounds,
            memory_profiling=memory_profiling,
        )

        # Format output if requested
        formatter = OutputFormatter()
        formatted_outputs = {}
        for fmt in config.output_format:
            if fmt == OutputFormat.JSON:
                formatted_outputs["json"] = formatter.format_performance_report(report, FormatterOutputFormat.JSON)
            elif fmt == OutputFormat.CSV:
                formatted_outputs["csv"] = formatter.format_performance_report(report, FormatterOutputFormat.CSV)

        metadata = {
            "report": report.model_dump(),
            "formatted_outputs": formatted_outputs,
        }

        manager.update_experiment_status(result.experiment_id, ExperimentStatus.COMPLETED, metadata=metadata)

    except Exception as e:
        manager.update_experiment_status(result.experiment_id, ExperimentStatus.FAILED, error_message=str(e))
        raise ExecutionError(f"Performance experiment failed: {e}") from e

    return manager.get_experiment_result(result.experiment_id) or result


async def _run_language_detection_experiment(config: ExperimentConfig, manager: ExperimentManager) -> ExperimentResult:
    """Run language detection accuracy experiment."""
    result = manager.create_experiment_result(config)

    try:
        manager.update_experiment_status(result.experiment_id, ExperimentStatus.RUNNING)

        # Extract parameters
        test_documents = config.parameters.get("test_documents", [])
        _validate_test_documents_parameter(test_documents)

        analyzer = LanguageDetectorAnalyzer()

        # Process test documents
        results = []
        for doc_info in test_documents:
            doc_path = Path(doc_info.get("path", ""))
            expected_lang = Language(doc_info.get("expected_language", "ja"))
            is_spec = doc_info.get("is_spec_document", True)

            detection_result = await analyzer.analyze_document(doc_path, expected_lang, is_spec)
            results.append(detection_result)

        # Generate combined report
        report = analyzer.generate_accuracy_report(results)

        # Format output if requested
        formatter = OutputFormatter()
        formatted_outputs = {}
        for fmt in config.output_format:
            if fmt == OutputFormat.JSON:
                formatted_outputs["json"] = formatter.format_language_detection_report(
                    report, FormatterOutputFormat.JSON
                )
            elif fmt == OutputFormat.CSV:
                formatted_outputs["csv"] = formatter.format_language_detection_report(report, FormatterOutputFormat.CSV)

        metadata = {
            "report": report.model_dump(),
            "formatted_outputs": formatted_outputs,
        }

        manager.update_experiment_status(result.experiment_id, ExperimentStatus.COMPLETED, metadata=metadata)

    except Exception as e:
        manager.update_experiment_status(result.experiment_id, ExperimentStatus.FAILED, error_message=str(e))
        raise ExecutionError(f"Language detection experiment failed: {e}") from e

    return manager.get_experiment_result(result.experiment_id) or result


async def _run_comparative_experiment(config: ExperimentConfig, manager: ExperimentManager) -> ExperimentResult:
    """Run comparative experiment with statistical analysis."""
    result = manager.create_experiment_result(config)

    try:
        manager.update_experiment_status(result.experiment_id, ExperimentStatus.RUNNING)

        # Extract parameters
        baseline_experiment_id = config.parameters.get("baseline_experiment_id")
        comparison_experiment_ids = config.parameters.get("comparison_experiment_ids", [])
        metrics_to_compare = config.parameters.get("metrics_to_compare")

        # Validate parameters
        _validate_baseline_experiment_id(baseline_experiment_id)
        _validate_comparison_experiment_ids(comparison_experiment_ids)

        # Get experiment results from manager
        baseline_exp = manager.get_experiment_result(str(baseline_experiment_id))
        _validate_experiment_exists(str(baseline_experiment_id), baseline_exp)

        comparison_exps = []
        for comp_id in comparison_experiment_ids:
            comp_exp = manager.get_experiment_result(comp_id)
            _validate_experiment_exists(comp_id, comp_exp)
            comparison_exps.append(comp_exp)

        # Ensure all experiments are non-None before analysis
        _validate_baseline_experiment_exists(str(baseline_experiment_id), baseline_exp)
        _validate_comparison_experiments_exist(comparison_exps)

        # Type assertion after validation
        assert baseline_exp is not None
        valid_comparison_exps = [comp_exp for comp_exp in comparison_exps if comp_exp is not None]

        # Run comparative analysis
        analyzer = ComparativeAnalyzer()
        comparative_report = analyzer.compare_experiments(
            baseline_experiment=baseline_exp,
            comparison_experiments=valid_comparison_exps,
            metrics_to_compare=metrics_to_compare,
        )

        # Format output if requested
        formatter = OutputFormatter()
        formatted_outputs = {}
        for fmt in config.output_format:
            if fmt == OutputFormat.JSON:
                formatted_outputs["json"] = formatter.format_to_json(comparative_report)
            elif fmt == OutputFormat.CSV:
                formatted_outputs["csv"] = formatter.format_to_csv(comparative_report)

        metadata = {
            "comparative_report": comparative_report.model_dump(),
            "formatted_outputs": formatted_outputs,
            "baseline_experiment_id": baseline_experiment_id,
            "comparison_experiment_ids": comparison_experiment_ids,
            "total_comparisons": len(comparative_report.comparisons),
            "significant_differences": len(
                [c for c in comparative_report.comparisons if c.statistical_comparison.is_significant]
            ),
        }

        manager.update_experiment_status(result.experiment_id, ExperimentStatus.COMPLETED, metadata=metadata)

    except Exception as e:
        manager.update_experiment_status(result.experiment_id, ExperimentStatus.FAILED, error_message=str(e))
        raise ExecutionError(f"Comparative experiment failed: {e}") from e

    return manager.get_experiment_result(result.experiment_id) or result


# Validation helper functions


def _validate_input_paths(input_paths: list[Path]) -> None:
    """Validate input paths list is not empty."""
    if not input_paths:
        raise InvalidParametersError("At least one input path must be provided")


def _validate_path_exists(path: Path) -> None:
    """Validate that a path exists."""
    if not path.exists():
        raise InvalidParametersError(f"Input path does not exist: {path}")


def _validate_measurement_rounds(rounds: int) -> None:
    """Validate measurement rounds parameter."""
    if rounds <= 0:
        raise InvalidParametersError("measurement_rounds must be positive")


def _validate_warmup_rounds(rounds: int) -> None:
    """Validate warmup rounds parameter."""
    if rounds < 0:
        raise InvalidParametersError("warmup_rounds must be non-negative")


def _validate_input_paths_parameter(input_paths: list[str]) -> None:
    """Validate input_paths parameter for experiments."""
    if not input_paths:
        raise InvalidParametersError("input_paths parameter is required for EARS coverage experiment")


def _validate_test_documents_parameter(test_documents: list[dict[str, Any]]) -> None:
    """Validate test_documents parameter for experiments."""
    if not test_documents:
        raise InvalidParametersError("test_documents parameter is required for language detection experiment")


def _validate_baseline_experiment_id(baseline_experiment_id: str | None) -> None:
    """Validate baseline experiment ID parameter."""
    if not baseline_experiment_id:
        raise InvalidParametersError("baseline_experiment_id parameter is required for comparative experiment")


def _validate_comparison_experiment_ids(comparison_experiment_ids: list[str]) -> None:
    """Validate comparison experiment IDs parameter."""
    if not comparison_experiment_ids:
        raise InvalidParametersError("comparison_experiment_ids parameter is required for comparative experiment")


def _validate_experiment_exists(experiment_id: str, experiment: ExperimentResult | None) -> None:
    """Validate that an experiment result exists."""
    if not experiment:
        raise InvalidParametersError(f"Experiment not found: {experiment_id}")


def _validate_baseline_experiment_exists(baseline_experiment_id: str, baseline_exp: ExperimentResult | None) -> None:
    """Validate that baseline experiment exists."""
    if baseline_exp is None:
        raise InvalidParametersError(f"Baseline experiment not found: {baseline_experiment_id}")


def _validate_comparison_experiments_exist(comparison_exps: list[ExperimentResult | None]) -> None:
    """Validate that all comparison experiments exist."""
    for comp_exp in comparison_exps:
        if comp_exp is None:
            raise InvalidParametersError("One or more comparison experiments not found")


def _raise_unsupported_experiment_type(experiment_type: ExperimentType) -> None:
    """Raise error for unsupported experiment type."""
    raise InvalidParametersError(f"Unsupported experiment type: {experiment_type}")
