"""CLI interface for wassden."""

import asyncio
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
from .lib.language_detection import determine_language
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
