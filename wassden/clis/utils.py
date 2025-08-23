import os
import sys
from pathlib import Path

import typer
from colorama import Fore, Style, init

from wassden.lib import fs_utils
from wassden.lib.language_detection import determine_language
from wassden.types import Language

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
