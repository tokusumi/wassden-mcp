"""CLI interface for wassden."""

import asyncio
import sys
from typing import Any

import click
from colorama import Fore, Style, init

from .handlers import (
    handle_analyze_changes,
    handle_check_completeness,
    handle_get_traceability,
    handle_prompt_code,
    handle_prompt_design,
    handle_prompt_requirements,
    handle_prompt_tasks,
    handle_validate_design,
    handle_validate_requirements,
    handle_validate_tasks,
)
from .server import main as run_server

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def print_success(message: str) -> None:
    """Print a success message in green."""
    click.echo(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    click.echo(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    click.echo(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def print_info(message: str) -> None:
    """Print an info message in blue."""
    click.echo(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")


async def run_handler(handler: Any, args: dict[str, Any]) -> None:
    """Run a handler and print the result."""
    try:
        result = await handler(args)
        content = result.get("content", [])
        if content and len(content) > 0:
            text = content[0].get("text", "")
            click.echo(text)
        else:
            print_warning("No content returned from handler")
    except Exception as e:
        print_error(f"Error: {e!s}")
        sys.exit(1)


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """wassden - MCP-based Spec-Driven Development toolkit."""


@cli.command()
@click.option("--server", is_flag=True, help="Run as MCP server")
def serve(server: bool) -> None:
    """Run wassden as an MCP server."""
    if server:
        print_info("Starting wassden MCP server...")
        run_server()
    else:
        print_error("Use --server flag to run as MCP server")
        sys.exit(1)


@cli.command()
@click.option("--userInput", "-i", required=True, help="User's project description")
def check_completeness(userinput: str) -> None:
    """Analyze user input for completeness."""
    print_info("Analyzing input completeness...")
    asyncio.run(run_handler(handle_check_completeness, {"userInput": userinput}))


@cli.command()
@click.option("--projectDescription", "-p", required=True, help="Project description")
@click.option("--scope", "-s", default="", help="Project scope")
@click.option("--constraints", "-c", default="", help="Technical constraints")
def prompt_requirements(projectdescription: str, scope: str, constraints: str) -> None:
    """Generate prompt for creating requirements.md."""
    print_info("Generating requirements prompt...")
    asyncio.run(
        run_handler(
            handle_prompt_requirements,
            {
                "projectDescription": projectdescription,
                "scope": scope,
                "constraints": constraints,
            },
        )
    )


@cli.command()
@click.option(
    "--requirementsPath",
    "-r",
    default="specs/requirements.md",
    help="Path to requirements.md",
)
def validate_requirements(requirementspath: str) -> None:
    """Validate requirements.md document."""
    print_info(f"Validating {requirementspath}...")
    asyncio.run(
        run_handler(
            handle_validate_requirements,
            {
                "requirementsPath": requirementspath,
            },
        )
    )


@cli.command()
@click.option(
    "--requirementsPath",
    "-r",
    default="specs/requirements.md",
    help="Path to requirements.md",
)
def prompt_design(requirementspath: str) -> None:
    """Generate prompt for creating design.md."""
    print_info("Generating design prompt...")
    asyncio.run(
        run_handler(
            handle_prompt_design,
            {
                "requirementsPath": requirementspath,
            },
        )
    )


@cli.command()
@click.option(
    "--designPath",
    "-d",
    default="specs/design.md",
    help="Path to design.md",
)
@click.option(
    "--requirementsPath",
    "-r",
    default="specs/requirements.md",
    help="Path to requirements.md",
)
def validate_design(designpath: str, requirementspath: str) -> None:
    """Validate design.md document."""
    print_info(f"Validating {designpath}...")
    asyncio.run(
        run_handler(
            handle_validate_design,
            {
                "designPath": designpath,
                "requirementsPath": requirementspath,
            },
        )
    )


@cli.command()
@click.option(
    "--designPath",
    "-d",
    default="specs/design.md",
    help="Path to design.md",
)
@click.option(
    "--requirementsPath",
    "-r",
    default="specs/requirements.md",
    help="Path to requirements.md",
)
def prompt_tasks(designpath: str, requirementspath: str) -> None:
    """Generate prompt for creating tasks.md."""
    print_info("Generating tasks prompt...")
    asyncio.run(
        run_handler(
            handle_prompt_tasks,
            {
                "designPath": designpath,
                "requirementsPath": requirementspath,
            },
        )
    )


@cli.command()
@click.option(
    "--tasksPath",
    "-t",
    default="specs/tasks.md",
    help="Path to tasks.md",
)
def validate_tasks(taskspath: str) -> None:
    """Validate tasks.md document."""
    print_info(f"Validating {taskspath}...")
    asyncio.run(
        run_handler(
            handle_validate_tasks,
            {
                "tasksPath": taskspath,
            },
        )
    )


@cli.command()
@click.option(
    "--tasksPath",
    "-t",
    default="specs/tasks.md",
    help="Path to tasks.md",
)
@click.option(
    "--requirementsPath",
    "-r",
    default="specs/requirements.md",
    help="Path to requirements.md",
)
@click.option(
    "--designPath",
    "-d",
    default="specs/design.md",
    help="Path to design.md",
)
def prompt_code(taskspath: str, requirementspath: str, designpath: str) -> None:
    """Generate implementation prompt."""
    print_info("Generating implementation prompt...")
    asyncio.run(
        run_handler(
            handle_prompt_code,
            {
                "tasksPath": taskspath,
                "requirementsPath": requirementspath,
                "designPath": designpath,
            },
        )
    )


@cli.command()
@click.option("--changedFile", "-f", required=True, help="Path to changed file")
@click.option("--changeDescription", "-c", required=True, help="Description of changes")
def analyze_changes(changedfile: str, changedescription: str) -> None:
    """Analyze impact of changes to spec files."""
    print_info(f"Analyzing changes to {changedfile}...")
    asyncio.run(
        run_handler(
            handle_analyze_changes,
            {
                "changedFile": changedfile,
                "changeDescription": changedescription,
            },
        )
    )


@cli.command()
@click.option(
    "--requirementsPath",
    "-r",
    default="specs/requirements.md",
    help="Path to requirements.md",
)
@click.option(
    "--designPath",
    "-d",
    default="specs/design.md",
    help="Path to design.md",
)
@click.option(
    "--tasksPath",
    "-t",
    default="specs/tasks.md",
    help="Path to tasks.md",
)
def get_traceability(requirementspath: str, designpath: str, taskspath: str) -> None:
    """Generate traceability report."""
    print_info("Generating traceability report...")
    asyncio.run(
        run_handler(
            handle_get_traceability,
            {
                "requirementsPath": requirementspath,
                "designPath": designpath,
                "tasksPath": taskspath,
            },
        )
    )


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
