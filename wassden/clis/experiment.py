"""Experiment CLI commands for development mode."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Annotated, Any

import typer

from wassden.clis.utils import (
    _supports_color,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from wassden.language_types import Language
from wassden.lib.constants import DEFAULT_CONFIG_PATH
from wassden.lib.experiment import ExperimentResult, ExperimentType, OutputFormat
from wassden.lib.experiment_api import (
    measure_ears_coverage,
    measure_performance,
    run_experiment,
)
from wassden.lib.experiment_manager import ExperimentManager
from wassden.lib.output_formatter import OutputFormat as FormatterOutputFormat
from wassden.lib.output_formatter import OutputFormatter

experiment_app = typer.Typer(
    help="Experiment runner commands for validation framework testing.",
    rich_markup_mode="markdown" if _supports_color() else None,
)


# Async implementation
async def _run_experiment_async(
    experiment_type: ExperimentType,
    output_format: list[OutputFormat] | None,
    timeout: int,
    memory_limit: int,
    config_path: Path,
) -> ExperimentResult:
    """Async implementation for running experiments."""
    # Prepare experiment parameters
    parameters = {"timeout_seconds": timeout, "memory_limit_mb": memory_limit}

    # Run experiment
    return await run_experiment(
        experiment_type=experiment_type,
        parameters=parameters,
        output_format=output_format or [OutputFormat.JSON],
        timeout_seconds=timeout,
        memory_limit_mb=memory_limit,
        config_path=config_path,
    )


# Create experiment subcommand group
@experiment_app.command()
def run(
    experiment_type: Annotated[ExperimentType, typer.Argument(help="Type of experiment to run")],
    output_format: Annotated[list[OutputFormat] | None, typer.Option("--format", "-f", help="Output format(s)")] = None,
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Timeout in seconds")] = 600,
    memory_limit: Annotated[int, typer.Option("--memory", "-m", help="Memory limit in MB")] = 100,
    config_path: Annotated[
        Path, typer.Option("--config-path", help="Configuration directory path")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Run an experiment of specified type - implements REQ-08."""
    print_info(f"Starting {experiment_type.value} experiment")

    try:
        # Thin sync wrapper - call async implementation with timeout (if positive)
        async_task = _run_experiment_async(experiment_type, output_format, timeout, memory_limit, config_path)
        if timeout > 0:
            result = asyncio.run(asyncio.wait_for(async_task, timeout=timeout))
        else:
            result = asyncio.run(async_task)

        # Display results
        print_success("Experiment completed successfully")
        print_info(f"Experiment ID: {result.experiment_id}")
        print_info(f"Status: {result.status}")

    except Exception as e:
        print_error(f"Experiment failed: {e}")
        sys.exit(1)


@experiment_app.command(name="save-config")
def save_config(
    experiment_type: Annotated[ExperimentType, typer.Argument(help="Type of experiment")],
    config_name: Annotated[str, typer.Argument(help="Configuration name")],
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Timeout in seconds")] = 600,
    memory_limit: Annotated[int, typer.Option("--memory", "-m", help="Memory limit in MB")] = 100,
    config_path: Annotated[
        Path, typer.Option("--config-path", help="Configuration directory path")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Save experiment configuration to file."""

    manager = ExperimentManager(config_dir=config_path)

    try:
        print_info(f"Saving {experiment_type.value} configuration as '{config_name}'...")

        config = manager.create_default_config(experiment_type)
        config.timeout_seconds = timeout
        config.memory_limit_mb = memory_limit

        saved_path = manager.save_config(config, config_name)
        print_success(f"Configuration saved to: {saved_path}")

    except Exception as e:
        print_error(f"Failed to save configuration: {e}")
        sys.exit(1)


@experiment_app.command(name="import-config")
def import_config(
    config_name: Annotated[str, typer.Argument(help="Configuration name to save as")],
    json_file: Annotated[Path, typer.Argument(help="JSON configuration file path")],
    config_path: Annotated[
        Path, typer.Option("--config-path", help="Configuration directory path")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Import experiment configuration from JSON file."""

    manager = ExperimentManager(config_dir=config_path)

    try:
        if not json_file.exists():
            print_error(f"Configuration file '{json_file}' not found")
            sys.exit(1)

        print_info(f"Importing configuration from '{json_file}' as '{config_name}'...")

        with json_file.open() as f:
            config_data = json.load(f)

        saved_path = manager.save_config(config_data, config_name)
        print_success(f"Configuration '{config_name}' imported successfully to: {saved_path}")

    except json.JSONDecodeError:
        print_error("Invalid JSON in configuration file")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to import configuration: {e}")
        sys.exit(1)


@experiment_app.command()
def load_config(
    name: Annotated[str, typer.Argument(help="Configuration name to load")],
    config_path: Annotated[
        Path, typer.Option("--config-path", help="Configuration directory path")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Load and display experiment configuration."""
    print_info(f"Loading configuration '{name}'...")

    manager = ExperimentManager(config_dir=config_path)

    try:
        config = manager.load_config(name)

        print_success("Configuration loaded successfully:")
        exp_type = (
            config.experiment_type.value if hasattr(config.experiment_type, "value") else str(config.experiment_type)
        )
        print_info(f"Type: {exp_type}")
        print_info(f"Timeout: {config.timeout_seconds}s")
        print_info(f"Memory limit: {config.memory_limit_mb}MB")
        output_formats = [fmt.value if hasattr(fmt, "value") else str(fmt) for fmt in config.output_format]
        print_info(f"Output formats: {output_formats}")
        print_info(f"Parameters: {config.parameters}")

    except Exception as e:
        print_error(f"Failed to load configuration: {e}")
        sys.exit(1)


@experiment_app.command()
def list_configs(
    config_path: Annotated[
        Path, typer.Option("--config-path", help="Configuration directory path")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """List available experiment configurations."""
    print_info("Available configurations:")

    manager = ExperimentManager(config_dir=config_path)
    configs = manager.list_configs()

    if not configs:
        print_warning("No configurations found")
        return

    for config_name in configs:
        print_info(f"  - {config_name}")


@experiment_app.command()
def status(
    config_path: Annotated[
        Path, typer.Option("--config-path", help="Configuration directory path")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Show status of active experiments."""
    print_info("Active experiments:")

    manager = ExperimentManager(config_dir=config_path)
    experiments = manager.list_active_experiments()

    if not experiments:
        print_warning("No active experiments")
        return

    for exp in experiments:
        print_info(f"  {exp.experiment_id}: {exp.status.value} ({exp.config.experiment_type.value})")
        if exp.duration_seconds > 0:
            print_info(f"    Duration: {exp.duration_seconds:.2f}s")


# Async implementation
async def _run_experiment_cmd_async(
    experiment_type: ExperimentType,
    parsed_params: dict,
    output_format: list[OutputFormat],
    config_path: Path,
    *,
    timeout: int = 600,
    memory_limit: int = 100,
) -> ExperimentResult:
    """Async implementation for running experiment command."""
    return await run_experiment(
        experiment_type=experiment_type,
        parameters=parsed_params,
        output_format=output_format,
        timeout_seconds=timeout,
        memory_limit_mb=memory_limit,
        config_path=config_path,
    )


# Core API commands - Implements REQ-08 and TASK-02-05
@experiment_app.command(name="run-experiment")
def run_experiment_cmd(
    experiment_type: Annotated[ExperimentType, typer.Argument(help="Type of experiment to run")],
    parameters: Annotated[str, typer.Option("--parameters", "-p", help="JSON parameters for experiment")] = "{}",
    output_format: Annotated[list[OutputFormat] | None, typer.Option("--format", "-f", help="Output format(s)")] = None,
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Timeout in seconds")] = 600,
    memory_limit: Annotated[int, typer.Option("--memory", "-m", help="Memory limit in MB")] = 100,
    config_path: Annotated[
        Path, typer.Option("--config-path", help="Configuration directory path")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Run experiment using the core API - implements REQ-08."""

    print_info(f"Running {experiment_type.value} experiment via API...")

    if output_format is None:
        output_format = [OutputFormat.JSON]

    try:
        # Parse parameters JSON
        parsed_params = json.loads(parameters)

        # Thin sync wrapper - call async implementation
        result = asyncio.run(
            _run_experiment_cmd_async(
                experiment_type, parsed_params, output_format, config_path, timeout=timeout, memory_limit=memory_limit
            )
        )

        print_success(f"Experiment completed: {result.experiment_id}")
        print_info(f"Status: {result.status.value}")
        print_info(f"Duration: {result.duration_seconds:.2f}s")

        if result.error_message:
            print_error(f"Error: {result.error_message}")

        # Display formatted outputs if available
        if result.metadata and "formatted_outputs" in result.metadata:
            outputs = result.metadata["formatted_outputs"]
            for format_name, content in outputs.items():
                print_info(f"\n--- {format_name.upper()} Output ---")
                typer.echo(content)

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON parameters: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Experiment failed: {e}")
        sys.exit(1)


# Async implementation
async def _measure_ears_coverage_async(
    input_paths: list[Path],
    language: Language,
    detail_level: str,
) -> Any:
    """Async implementation for EARS coverage measurement."""
    return await measure_ears_coverage(
        input_paths=input_paths,
        _language=language,
        _output_detail_level=detail_level,
    )


@experiment_app.command(name="measure-ears-coverage")
def measure_ears_coverage_cmd(
    input_paths: Annotated[list[Path], typer.Argument(help="Paths to markdown documents")],
    language: Annotated[Language, typer.Option("--language", "-l", help="Analysis language")] = Language.JAPANESE,
    detail_level: Annotated[str, typer.Option("--detail", "-d", help="Output detail level")] = "summary",
    output_format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.JSON,
) -> None:
    """Measure EARS coverage using the core API - implements REQ-08."""
    print_info(f"Measuring EARS coverage for {len(input_paths)} document(s)...")

    try:
        # Thin sync wrapper - call async implementation
        report = asyncio.run(_measure_ears_coverage_async(input_paths, language, detail_level))

        print_success("EARS coverage analysis completed")
        print_info(f"Total requirements: {report.total_requirements}")
        print_info(f"EARS compliant: {report.ears_compliant}")
        print_info(f"Coverage rate: {report.coverage_rate:.1f}%")

        # Format and display output
        formatter = OutputFormatter()

        if output_format == OutputFormat.JSON:
            content = formatter.format_ears_coverage_report(report, FormatterOutputFormat.JSON)
        else:
            content = formatter.format_ears_coverage_report(report, FormatterOutputFormat.CSV)

        print_info(f"\n--- {output_format.value.upper()} Report ---")
        typer.echo(content)

    except Exception as e:
        print_error(f"EARS coverage measurement failed: {e}")
        sys.exit(1)


# Async implementation
async def _measure_performance_async(
    operation_name: str,
    rounds: int,
    warmup: int,
    memory_profiling: bool,
) -> Any:
    """Async implementation for performance measurement."""
    return await measure_performance(
        operation_name=operation_name,
        measurement_rounds=rounds,
        warmup_rounds=warmup,
        memory_profiling=memory_profiling,
    )


@experiment_app.command(name="measure-performance")
def measure_performance_cmd(
    operation_name: Annotated[str, typer.Argument(help="Name of operation to measure")],
    rounds: Annotated[int, typer.Option("--rounds", "-r", help="Measurement rounds")] = 5,
    warmup: Annotated[int, typer.Option("--warmup", "-w", help="Warmup rounds")] = 2,
    memory_profiling: Annotated[bool, typer.Option("--memory/--no-memory", help="Enable memory profiling")] = True,
    output_format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.JSON,
) -> None:
    """Measure performance using the core API - implements REQ-08."""
    print_info(f"Measuring performance for operation: {operation_name}")

    try:
        # Thin sync wrapper - call async implementation
        report = asyncio.run(_measure_performance_async(operation_name, rounds, warmup, memory_profiling))

        print_success("Performance measurement completed")
        print_info(f"Total executions: {report.total_executions}")
        print_info(f"Successful: {report.successful_executions}")
        print_info(f"Average wall time: {report.average_wall_time_ms:.2f}ms")
        print_info(f"Average CPU time: {report.average_cpu_time_ms:.2f}ms")
        if report.average_memory_mb:
            print_info(f"Average memory: {report.average_memory_mb:.2f}MB")

        # Format and display output
        formatter = OutputFormatter()

        if output_format == OutputFormat.JSON:
            content = formatter.format_performance_report(report, FormatterOutputFormat.JSON)
        else:
            content = formatter.format_performance_report(report, FormatterOutputFormat.CSV)
        print_info(f"\n--- {output_format.value.upper()} Report ---")
        typer.echo(content)

    except Exception as e:
        print_error(f"Performance measurement failed: {e}")
        sys.exit(1)


# Async implementation
async def _compare_experiments_async(
    baseline_id: str,
    comparison_ids: list[str],
    metrics: list[str] | None,
    output_format: OutputFormat,
    config_path: Path,
) -> ExperimentResult:
    """Async implementation for experiment comparison."""
    # Prepare parameters
    parameters = {
        "baseline_experiment_id": baseline_id,
        "comparison_experiment_ids": comparison_ids,
    }
    if metrics:
        parameters["metrics_to_compare"] = metrics

    # Run comparative experiment
    return await run_experiment(
        experiment_type=ExperimentType.COMPARATIVE,
        parameters=parameters,
        output_format=[output_format],
        config_path=config_path,
    )


@experiment_app.command(name="compare")
def compare_experiments_cmd(
    baseline_id: Annotated[str, typer.Argument(help="Baseline experiment ID")],
    comparison_ids: Annotated[list[str], typer.Argument(help="Comparison experiment IDs")],
    metrics: Annotated[list[str] | None, typer.Option("--metrics", "-m", help="Metrics to compare")] = None,
    output_format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.JSON,
    config_path: Annotated[
        Path, typer.Option("--config-path", help="Configuration directory path")
    ] = DEFAULT_CONFIG_PATH,
) -> None:
    """Compare experiments with statistical analysis - implements REQ-07."""
    print_info(f"Comparing experiments: {baseline_id} vs {comparison_ids}")

    try:
        # Thin sync wrapper - call async implementation
        result = asyncio.run(
            _compare_experiments_async(baseline_id, comparison_ids, metrics, output_format, config_path)
        )

        print_success("Comparative analysis completed")
        print_info(f"Experiment ID: {result.experiment_id}")
        print_info(f"Status: {result.status.value}")

        # Display summary from metadata
        if result.metadata:
            total_comparisons = result.metadata.get("total_comparisons", 0)
            significant_differences = result.metadata.get("significant_differences", 0)
            print_info(f"Total comparisons: {total_comparisons}")
            print_info(f"Significant differences: {significant_differences}")

            # Display formatted output
            formatted_outputs = result.metadata.get("formatted_outputs", {})
            if output_format.value in formatted_outputs:
                print_info(f"\n--- {output_format.value.upper()} Report ---")
                typer.echo(formatted_outputs[output_format.value])

    except Exception as e:
        print_error(f"Comparative analysis failed: {e}")
        sys.exit(1)
