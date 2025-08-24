"""CLI interface for wassden."""

import asyncio
from importlib import metadata
from pathlib import Path
from typing import Annotated, Any

import typer

from wassden.clis.utils import (
    _determine_language_for_file,
    _determine_language_for_user_input,
    _supports_color,
    print_error,
    print_info,
    print_warning,
)
from wassden.handlers import (
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
from wassden.language_types import Language
from wassden.server import main as run_server_with_transport
from wassden.types import SpecDocuments, TransportType


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
        # Don't exit with error code - handle gracefully


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
        # Don't exit with error code - handle gracefully


app = typer.Typer(
    help="wassden - MCP-based Spec-Driven Development toolkit.",
    rich_markup_mode="markdown" if _supports_color() else None,
    pretty_exceptions_enable=_supports_color(),
)


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


# Async implementation


# Async implementation
async def _prompt_requirements_async(userinput: str, force: bool, language: Language | None) -> None:
    """Async implementation for requirements prompt generation."""
    determined_language = _determine_language_for_user_input(language, userinput)

    if force:
        # Force mode: generate requirements prompt without completeness verification
        specs = SpecDocuments(
            requirements_path=Path("specs/requirements.md"),
            design_path=Path("specs/design.md"),
            tasks_path=Path("specs/tasks.md"),
            language=determined_language,
        )
        await run_handler_typed(
            handle_prompt_requirements,
            specs,
            userinput,
            "",
            "",
        )
    else:
        # Default mode: check completeness
        await run_handler_typed(handle_check_completeness, userinput, determined_language)


@app.command()
def prompt_requirements(
    userinput: Annotated[str, typer.Option("--userInput", "-i", help="User's project description")],
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Generate requirements prompt without completeness verification")
    ] = False,
    language: Annotated[Language | None, typer.Option("--language", "-l", help="Language for output")] = None,
) -> None:
    """Analyze user input for completeness and generate requirements prompt."""
    if force:
        print_info("Generating requirements prompt...")
    else:
        print_info("Analyzing input completeness...")
    asyncio.run(_prompt_requirements_async(userinput, force, language))


# Async implementation
async def _validate_requirements_async(requirementspath: Path) -> None:
    """Async implementation for requirements validation."""
    specs = await SpecDocuments.from_paths(requirements_path=requirementspath)  # Auto-detect language
    await run_handler_typed(handle_validate_requirements, specs)


@app.command()
def validate_requirements(
    requirementspath: Annotated[Path, typer.Argument(help="Path to requirements.md")] = Path("specs/requirements.md"),
) -> None:
    """Validate requirements.md document."""
    print_info(f"Validating {requirementspath}...")
    asyncio.run(_validate_requirements_async(requirementspath))


# Async implementation
async def _prompt_design_async(requirementspath: Path) -> None:
    """Async implementation for design prompt generation."""
    specs = await SpecDocuments.from_paths(requirements_path=requirementspath, language=Language.JAPANESE)
    await run_handler_typed(handle_prompt_design, specs)


@app.command()
def prompt_design(
    requirementspath: Annotated[Path, typer.Argument(help="Path to requirements.md")] = Path("specs/requirements.md"),
) -> None:
    """Generate prompt for creating design.md."""
    print_info("Generating design prompt...")
    asyncio.run(_prompt_design_async(requirementspath))


# Async implementation
async def _validate_design_async(designpath: Path, requirementspath: Path | None) -> None:
    """Async implementation for design validation."""
    specs = await SpecDocuments.from_paths(requirements_path=requirementspath, design_path=designpath)
    await run_handler_typed(handle_validate_design, specs)


@app.command()
def validate_design(
    designpath: Annotated[Path, typer.Argument(help="Path to design.md")] = Path("specs/design.md"),
    requirementspath: Annotated[
        Path | None, typer.Option("--requirementsPath", "-r", help="Path to requirements.md (optional)")
    ] = None,
) -> None:
    """Validate design.md document."""
    print_info(f"Validating {designpath}...")
    asyncio.run(_validate_design_async(designpath, requirementspath))


# Async implementation
async def _prompt_tasks_async(designpath: Path, requirementspath: Path | None) -> None:
    """Async implementation for tasks prompt generation."""
    specs = await SpecDocuments.from_paths(requirements_path=requirementspath, design_path=designpath)
    await run_handler_typed(handle_prompt_tasks, specs)


@app.command()
def prompt_tasks(
    designpath: Annotated[Path, typer.Argument(help="Path to design.md")] = Path("specs/design.md"),
    requirementspath: Annotated[
        Path | None, typer.Option("--requirementsPath", "-r", help="Path to requirements.md (optional)")
    ] = None,
) -> None:
    """Generate prompt for creating tasks.md."""
    print_info("Generating tasks prompt...")
    asyncio.run(_prompt_tasks_async(designpath, requirementspath))


# Async implementation
async def _validate_tasks_async(taskspath: Path) -> None:
    """Async implementation for tasks validation."""
    specs = await SpecDocuments.from_paths(tasks_path=taskspath, language=Language.JAPANESE)
    await run_handler_typed(handle_validate_tasks, specs)


@app.command()
def validate_tasks(
    taskspath: Annotated[Path, typer.Argument(help="Path to tasks.md")] = Path("specs/tasks.md"),
) -> None:
    """Validate tasks.md document."""
    print_info(f"Validating {taskspath}...")
    asyncio.run(_validate_tasks_async(taskspath))


# Async implementation
async def _prompt_code_async(taskspath: Path, requirementspath: Path | None, designpath: Path | None) -> None:
    """Async implementation for code prompt generation."""
    specs = await SpecDocuments.from_paths(
        requirements_path=requirementspath, design_path=designpath, tasks_path=taskspath
    )
    await run_handler_typed(handle_prompt_code, specs)


@app.command()
def prompt_code(
    taskspath: Annotated[Path, typer.Argument(help="Path to tasks.md")] = Path("specs/tasks.md"),
    requirementspath: Annotated[
        Path | None, typer.Option("--requirementsPath", "-r", help="Path to requirements.md (optional)")
    ] = None,
    designpath: Annotated[Path | None, typer.Option("--designPath", "-d", help="Path to design.md (optional)")] = None,
) -> None:
    """Generate implementation prompt."""
    print_info("Generating implementation prompt...")
    asyncio.run(_prompt_code_async(taskspath, requirementspath, designpath))


# Async implementation
async def _analyze_changes_async(changedfile: Path, changedescription: str) -> None:
    """Async implementation for change analysis."""
    determined_language = await _determine_language_for_file(None, str(changedfile))
    await run_handler_typed(
        handle_analyze_changes,
        changedfile,
        changedescription,
        determined_language,
    )


@app.command()
def analyze_changes(
    changedfile: Annotated[Path, typer.Option("--changedFile", "-f", help="Path to changed file")],
    changedescription: Annotated[str, typer.Option("--changeDescription", "-c", help="Description of changes")],
) -> None:
    """Analyze impact of changes to spec files."""
    print_info(f"Analyzing changes to {changedfile}...")
    asyncio.run(_analyze_changes_async(changedfile, changedescription))


# Async implementation
async def _get_traceability_async(requirementspath: Path, designpath: Path | None, taskspath: Path | None) -> None:
    """Async implementation for traceability report generation."""
    specs = await SpecDocuments.from_paths(
        requirements_path=requirementspath, design_path=designpath, tasks_path=taskspath
    )
    await run_handler_typed(handle_get_traceability, specs)


@app.command()
def get_traceability(
    requirementspath: Annotated[Path, typer.Argument(help="Path to requirements.md")] = Path("specs/requirements.md"),
    designpath: Annotated[Path | None, typer.Option("--designPath", "-d", help="Path to design.md (optional)")] = None,
    taskspath: Annotated[Path | None, typer.Option("--tasksPath", "-t", help="Path to tasks.md (optional)")] = None,
) -> None:
    """Generate traceability report."""
    print_info("Generating traceability report...")
    asyncio.run(_get_traceability_async(requirementspath, designpath, taskspath))


# Async implementation
async def _generate_review_prompt_async(
    task_id: str, taskspath: Path, requirementspath: Path | None, designpath: Path | None
) -> None:
    """Async implementation for review prompt generation."""
    specs = await SpecDocuments.from_paths(
        requirements_path=requirementspath, design_path=designpath, tasks_path=taskspath
    )
    await run_handler_typed(handle_generate_review_prompt, task_id, specs)


@app.command()
def generate_review_prompt(
    task_id: Annotated[str, typer.Argument(help="Task ID to generate review prompt for (e.g., TASK-01-01)")],
    taskspath: Annotated[Path, typer.Argument(help="Path to tasks.md")] = Path("specs/tasks.md"),
    requirementspath: Annotated[
        Path | None, typer.Option("--requirementsPath", "-r", help="Path to requirements.md (optional)")
    ] = None,
    designpath: Annotated[Path | None, typer.Option("--designPath", "-d", help="Path to design.md (optional)")] = None,
) -> None:
    """Generate implementation review prompt for specific TASK-ID to validate implementation quality."""
    print_info(f"Generating review prompt for {task_id}...")
    asyncio.run(_generate_review_prompt_async(task_id, taskspath, requirementspath, designpath))


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
