"""CLI interface for wassden."""

import asyncio
import json
import os
import sys
from enum import Enum
from importlib import metadata
from pathlib import Path
from typing import Annotated, Any

import typer
from colorama import Fore, Style, init

from .handlers import (
    handle_analyze_changes,
    handle_check_completeness,
    handle_generate_review_prompt,
    handle_get_traceability,
    handle_prompt_code,
    handle_prompt_design,
    handle_prompt_requirements,
    handle_prompt_tasks,
    handle_validate_design,
    handle_validate_requirements,
    handle_validate_tasks,
)
from .lib import fs_utils
from .lib.experiment import ExperimentType, OutputFormat
from .lib.experiment_api import (
    measure_ears_coverage,
    measure_performance,
    run_experiment,
)
from .lib.experiment_manager import ExperimentManager
from .lib.language_detection import determine_language
from .lib.output_formatter import OutputFormat as FormatterOutputFormat
from .lib.output_formatter import OutputFormatter
from .server import main as run_server_with_transport
from .types import Language

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def _determine_language_for_user_input(language: Language | None, user_input: str = "") -> Language:
    """Determine language from CLI input and user text."""
    return determine_language(explicit_language=language, user_input=user_input)


async def _determine_language_for_file(
    language: Language | None, file_path: str, is_spec_document: bool = True
) -> Language:
    """Determine language from CLI input and file content."""
    try:
        content = await fs_utils.read_file(Path(file_path))
        return determine_language(explicit_language=language, content=content, is_spec_document=is_spec_document)
    except FileNotFoundError:
        return determine_language(explicit_language=language)


def _supports_color() -> bool:
    """Check if the terminal supports color output."""
    # Check for NO_COLOR environment variable (standard)
    if os.environ.get("NO_COLOR"):
        return False

    # Check for FORCE_COLOR environment variable
    if os.environ.get("FORCE_COLOR"):
        return True

    # Check if running in CI environment
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return False

    # Check if stdout is a TTY
    if not sys.stdout.isatty():
        return False

    # Check TERM environment variable
    term = os.environ.get("TERM", "")
    return term not in ("dumb", "")


class TransportType(str, Enum):
    """Available transport types for MCP server."""

    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable-http"


def print_success(message: str) -> None:
    """Print a success message in green."""
    if _supports_color():
        typer.echo(f"{Fore.GREEN}[SUCCESS] {message}{Style.RESET_ALL}")
    else:
        typer.echo(f"[SUCCESS] {message}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    if _supports_color():
        typer.echo(f"{Fore.YELLOW}[WARNING] {message}{Style.RESET_ALL}")
    else:
        typer.echo(f"[WARNING] {message}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    if _supports_color():
        typer.echo(f"{Fore.RED}[ERROR] {message}{Style.RESET_ALL}")
    else:
        typer.echo(f"[ERROR] {message}")


def print_info(message: str) -> None:
    """Print an info message in blue."""
    if _supports_color():
        typer.echo(f"{Fore.BLUE}[INFO] {message}{Style.RESET_ALL}")
    else:
        typer.echo(f"[INFO] {message}")


async def run_handler(handler: Any, args: dict[str, Any]) -> None:
    """Run a handler and print the result."""
    try:
        result = await handler(args)
        content = result.get("content", [])
        if content and len(content) > 0:
            text = content[0].get("text", "")
            typer.echo(text)
        else:
            print_warning("No content returned from handler")
    except Exception as e:
        print_error(f"Error: {e!s}")
        sys.exit(1)


async def run_handler_typed(handler: Any, *args: Any) -> None:
    """Run a typed handler and print the result."""
    try:
        result = await handler(*args)
        # Convert Pydantic model to dict if needed
        result_dict = result.model_dump() if hasattr(result, "model_dump") else result

        content = result_dict.get("content", [])
        if content and len(content) > 0:
            text = content[0].get("text", "")
            typer.echo(text)
        else:
            print_warning("No content returned from handler")
    except Exception as e:
        print_error(f"Error: {e!s}")
        sys.exit(1)


app = typer.Typer(
    help="wassden - MCP-based Spec-Driven Development toolkit.",
    rich_markup_mode="markdown" if _supports_color() else None,
    pretty_exceptions_enable=_supports_color(),
)

# Create experiment subcommand group
experiment_app = typer.Typer(
    help="Experiment runner commands for validation framework testing.",
    rich_markup_mode="markdown" if _supports_color() else None,
)
app.add_typer(experiment_app, name="experiment")


# Experiment CLI commands
@experiment_app.command()
def run(
    experiment_type: Annotated[ExperimentType, typer.Argument(help="Type of experiment to run")],
    config_name: Annotated[str, typer.Option("--config", "-c", help="Configuration name to use")] = "",
    output_format: Annotated[list[OutputFormat] | None, typer.Option("--format", "-f", help="Output format(s)")] = None,
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Timeout in seconds")] = 600,
    memory_limit: Annotated[int, typer.Option("--memory", "-m", help="Memory limit in MB")] = 100,
) -> None:
    """Run an experiment with specified configuration."""
    print_info(f"Running {experiment_type.value} experiment...")

    if output_format is None:
        output_format = [OutputFormat.JSON]

    manager = ExperimentManager()

    try:
        # Load or create configuration
        if config_name:
            config = manager.load_config(config_name)
        else:
            config = manager.create_default_config(experiment_type)
            config.timeout_seconds = timeout
            config.memory_limit_mb = memory_limit
            config.output_format = output_format

        # Run experiment
        result = asyncio.run(manager.run_experiment(config))

        print_success(f"Experiment completed: {result.experiment_id}")
        print_info(f"Status: {result.status.value}")
        print_info(f"Duration: {result.duration_seconds:.2f}s")

        if result.error_message:
            print_error(f"Error: {result.error_message}")

    except Exception as e:
        print_error(f"Experiment failed: {e}")
        sys.exit(1)


@experiment_app.command()
def save_config(
    experiment_type: Annotated[ExperimentType, typer.Argument(help="Type of experiment")],
    name: Annotated[str, typer.Argument(help="Configuration name")],
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Timeout in seconds")] = 600,
    memory_limit: Annotated[int, typer.Option("--memory", "-m", help="Memory limit in MB")] = 100,
) -> None:
    """Save experiment configuration to file."""
    print_info(f"Saving {experiment_type.value} configuration as '{name}'...")

    manager = ExperimentManager()

    try:
        config = manager.create_default_config(experiment_type)
        config.timeout_seconds = timeout
        config.memory_limit_mb = memory_limit

        config_path = manager.save_config(config, name)
        print_success(f"Configuration saved to: {config_path}")

    except Exception as e:
        print_error(f"Failed to save configuration: {e}")
        sys.exit(1)


@experiment_app.command()
def load_config(
    name: Annotated[str, typer.Argument(help="Configuration name to load")],
) -> None:
    """Load and display experiment configuration."""
    print_info(f"Loading configuration '{name}'...")

    manager = ExperimentManager()

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
def list_configs() -> None:
    """List available experiment configurations."""
    print_info("Available configurations:")

    manager = ExperimentManager()
    configs = manager.list_configs()

    if not configs:
        print_warning("No configurations found")
        return

    for config_name in configs:
        print_info(f"  - {config_name}")


@experiment_app.command()
def status() -> None:
    """Show status of active experiments."""
    print_info("Active experiments:")

    manager = ExperimentManager()
    experiments = manager.list_active_experiments()

    if not experiments:
        print_warning("No active experiments")
        return

    for exp in experiments:
        print_info(f"  {exp.experiment_id}: {exp.status.value} ({exp.config.experiment_type.value})")
        if exp.duration_seconds > 0:
            print_info(f"    Duration: {exp.duration_seconds:.2f}s")


# Core API commands - Implements REQ-08 and TASK-02-05
@experiment_app.command(name="run-experiment")
def run_experiment_cmd(
    experiment_type: Annotated[ExperimentType, typer.Argument(help="Type of experiment to run")],
    parameters: Annotated[str, typer.Option("--parameters", "-p", help="JSON parameters for experiment")] = "{}",
    output_format: Annotated[list[OutputFormat] | None, typer.Option("--format", "-f", help="Output format(s)")] = None,
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Timeout in seconds")] = 600,
    memory_limit: Annotated[int, typer.Option("--memory", "-m", help="Memory limit in MB")] = 100,
) -> None:
    """Run experiment using the core API - implements REQ-08."""

    print_info(f"Running {experiment_type.value} experiment via API...")

    if output_format is None:
        output_format = [OutputFormat.JSON]

    try:
        # Parse parameters JSON
        parsed_params = json.loads(parameters)

        # Run experiment via API
        result = asyncio.run(
            run_experiment(
                experiment_type=experiment_type,
                parameters=parsed_params,
                output_format=output_format,
                timeout_seconds=timeout,
                memory_limit_mb=memory_limit,
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


@experiment_app.command(name="measure-ears-coverage")
def measure_ears_coverage_cmd(
    input_paths: Annotated[list[Path], typer.Argument(help="Paths to markdown documents")],
    language: Annotated[Language | None, typer.Option("--language", "-l", help="Analysis language")] = None,
    detail_level: Annotated[str, typer.Option("--detail", "-d", help="Output detail level")] = "summary",
    output_format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.JSON,
) -> None:
    """Measure EARS coverage using the core API - implements REQ-08."""
    print_info(f"Measuring EARS coverage for {len(input_paths)} document(s)...")

    try:
        # Run EARS coverage measurement via API
        report = asyncio.run(
            measure_ears_coverage(
                input_paths=input_paths,
                _language=language,
                _output_detail_level=detail_level,
            )
        )

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
        # Run performance measurement via API
        report = asyncio.run(
            measure_performance(
                operation_name=operation_name,
                measurement_rounds=rounds,
                warmup_rounds=warmup,
                memory_profiling=memory_profiling,
            )
        )

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


@experiment_app.command(name="compare")
def compare_experiments_cmd(
    baseline_id: Annotated[str, typer.Argument(help="Baseline experiment ID")],
    comparison_ids: Annotated[list[str], typer.Argument(help="Comparison experiment IDs")],
    metrics: Annotated[list[str] | None, typer.Option("--metrics", "-m", help="Metrics to compare")] = None,
    output_format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.JSON,
) -> None:
    """Compare experiments with statistical analysis - implements REQ-07."""
    print_info(f"Comparing experiments: {baseline_id} vs {comparison_ids}")

    try:
        # Prepare parameters
        parameters = {
            "baseline_experiment_id": baseline_id,
            "comparison_experiment_ids": comparison_ids,
        }
        if metrics:
            parameters["metrics_to_compare"] = metrics

        # Run comparative experiment
        result = asyncio.run(
            run_experiment(
                experiment_type=ExperimentType.COMPARATIVE,
                parameters=parameters,
                output_format=[output_format],
            )
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


@app.command()
def start_mcp_server(
    transport: Annotated[TransportType, typer.Option(help="Transport type")] = TransportType.STDIO,
    host: Annotated[str, typer.Option(help="HTTP host (only used for sse/streamable-http transports)")] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="HTTP port (only used for sse/streamable-http transports)")] = 3001,
) -> None:
    """Start wassden MCP server with specified transport."""
    print_info(f"Starting wassden MCP server with {transport.value} transport...")

    if transport in [TransportType.SSE, TransportType.STREAMABLE_HTTP]:
        print_info(f"Listening on {host}:{port}")

    run_server_with_transport(transport=transport.value, host=host, port=port)


@app.command()
def check_completeness(
    userinput: Annotated[str, typer.Option("--userInput", "-i", help="User's project description")],
    language: Annotated[Language | None, typer.Option("--language", "-l", help="Language for output")] = None,
) -> None:
    """Analyze user input for completeness."""
    print_info("Analyzing input completeness...")
    determined_language = _determine_language_for_user_input(language, userinput)
    asyncio.run(run_handler_typed(handle_check_completeness, userinput, determined_language))


@app.command()
def prompt_requirements(
    projectdescription: Annotated[str, typer.Option("--projectDescription", "-p", help="Project description")],
    scope: Annotated[str, typer.Option("--scope", "-s", help="Project scope")] = "",
    constraints: Annotated[str, typer.Option("--constraints", "-c", help="Technical constraints")] = "",
    language: Annotated[Language | None, typer.Option("--language", "-l", help="Language for output")] = None,
) -> None:
    """Generate prompt for creating requirements.md."""
    print_info("Generating requirements prompt...")
    determined_language = _determine_language_for_user_input(language, projectdescription)
    asyncio.run(
        run_handler_typed(
            handle_prompt_requirements,
            projectdescription,
            scope,
            constraints,
            determined_language,
        )
    )


@app.command()
def validate_requirements(
    requirementspath: Annotated[Path, typer.Option("--requirementsPath", "-r", help="Path to requirements.md")] = Path(
        "specs/requirements.md"
    ),
) -> None:
    """Validate requirements.md document."""
    print_info(f"Validating {requirementspath}...")
    determined_language = asyncio.run(_determine_language_for_file(None, str(requirementspath)))
    asyncio.run(
        run_handler_typed(
            handle_validate_requirements,
            requirementspath,
            determined_language,
        )
    )


@app.command()
def prompt_design(
    requirementspath: Annotated[Path, typer.Option("--requirementsPath", "-r", help="Path to requirements.md")] = Path(
        "specs/requirements.md"
    ),
) -> None:
    """Generate prompt for creating design.md."""
    print_info("Generating design prompt...")
    determined_language = asyncio.run(_determine_language_for_file(None, str(requirementspath)))
    asyncio.run(
        run_handler_typed(
            handle_prompt_design,
            requirementspath,
            determined_language,
        )
    )


@app.command()
def validate_design(
    designpath: Annotated[Path, typer.Option("--designPath", "-d", help="Path to design.md")] = Path("specs/design.md"),
    requirementspath: Annotated[Path, typer.Option("--requirementsPath", "-r", help="Path to requirements.md")] = Path(
        "specs/requirements.md"
    ),
) -> None:
    """Validate design.md document."""
    print_info(f"Validating {designpath}...")
    determined_language = asyncio.run(_determine_language_for_file(None, str(designpath)))
    asyncio.run(
        run_handler_typed(
            handle_validate_design,
            designpath,
            requirementspath,
            determined_language,
        )
    )


@app.command()
def prompt_tasks(
    designpath: Annotated[Path, typer.Option("--designPath", "-d", help="Path to design.md")] = Path("specs/design.md"),
    requirementspath: Annotated[Path, typer.Option("--requirementsPath", "-r", help="Path to requirements.md")] = Path(
        "specs/requirements.md"
    ),
) -> None:
    """Generate prompt for creating tasks.md."""
    print_info("Generating tasks prompt...")
    determined_language = asyncio.run(_determine_language_for_file(None, str(designpath)))
    asyncio.run(
        run_handler_typed(
            handle_prompt_tasks,
            designpath,
            requirementspath,
            determined_language,
        )
    )


@app.command()
def validate_tasks(
    taskspath: Annotated[Path, typer.Option("--tasksPath", "-t", help="Path to tasks.md")] = Path("specs/tasks.md"),
) -> None:
    """Validate tasks.md document."""
    print_info(f"Validating {taskspath}...")
    determined_language = asyncio.run(_determine_language_for_file(None, str(taskspath)))
    asyncio.run(
        run_handler_typed(
            handle_validate_tasks,
            taskspath,
            determined_language,
        )
    )


@app.command()
def prompt_code(
    taskspath: Annotated[Path, typer.Option("--tasksPath", "-t", help="Path to tasks.md")] = Path("specs/tasks.md"),
    requirementspath: Annotated[Path, typer.Option("--requirementsPath", "-r", help="Path to requirements.md")] = Path(
        "specs/requirements.md"
    ),
    designpath: Annotated[Path, typer.Option("--designPath", "-d", help="Path to design.md")] = Path("specs/design.md"),
) -> None:
    """Generate implementation prompt."""
    print_info("Generating implementation prompt...")
    determined_language = asyncio.run(_determine_language_for_file(None, str(taskspath)))
    asyncio.run(
        run_handler_typed(
            handle_prompt_code,
            taskspath,
            requirementspath,
            designpath,
            determined_language,
        )
    )


@app.command()
def analyze_changes(
    changedfile: Annotated[Path, typer.Option("--changedFile", "-f", help="Path to changed file")],
    changedescription: Annotated[str, typer.Option("--changeDescription", "-c", help="Description of changes")],
) -> None:
    """Analyze impact of changes to spec files."""
    print_info(f"Analyzing changes to {changedfile}...")
    determined_language = asyncio.run(_determine_language_for_file(None, str(changedfile)))
    asyncio.run(
        run_handler_typed(
            handle_analyze_changes,
            changedfile,
            changedescription,
            determined_language,
        )
    )


@app.command()
def get_traceability(
    requirementspath: Annotated[Path, typer.Option("--requirementsPath", "-r", help="Path to requirements.md")] = Path(
        "specs/requirements.md"
    ),
    designpath: Annotated[Path, typer.Option("--designPath", "-d", help="Path to design.md")] = Path("specs/design.md"),
    taskspath: Annotated[Path, typer.Option("--tasksPath", "-t", help="Path to tasks.md")] = Path("specs/tasks.md"),
) -> None:
    """Generate traceability report."""
    print_info("Generating traceability report...")
    determined_language = asyncio.run(_determine_language_for_file(None, str(requirementspath)))
    asyncio.run(
        run_handler_typed(
            handle_get_traceability,
            requirementspath,
            designpath,
            taskspath,
            determined_language,
        )
    )


@app.command()
def generate_review_prompt(
    task_id: str = typer.Argument(..., help="Task ID to generate review prompt for (e.g., TASK-01-01)"),
    taskspath: Annotated[Path, typer.Option("--tasksPath", "-t", help="Path to tasks.md")] = Path("specs/tasks.md"),
    requirementspath: Annotated[Path, typer.Option("--requirementsPath", "-r", help="Path to requirements.md")] = Path(
        "specs/requirements.md"
    ),
    designpath: Annotated[Path, typer.Option("--designPath", "-d", help="Path to design.md")] = Path("specs/design.md"),
) -> None:
    """Generate implementation review prompt for specific TASK-ID to validate implementation quality."""
    print_info(f"Generating review prompt for {task_id}...")
    determined_language = asyncio.run(_determine_language_for_file(None, str(taskspath)))
    asyncio.run(
        run_handler_typed(
            handle_generate_review_prompt,
            task_id,
            taskspath,
            requirementspath,
            designpath,
            determined_language,
        )
    )


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        try:
            version = metadata.version("wassden")
        except metadata.PackageNotFoundError:
            version = "unknown"
        typer.echo(f"wassden version {version}")
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool, typer.Option("--version", callback=version_callback, help="Show version and exit")
    ] = False,
) -> None:
    """wassden - MCP-based Spec-Driven Development toolkit."""


if __name__ == "__main__":
    app()
