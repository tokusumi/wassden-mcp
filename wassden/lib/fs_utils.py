"""File system utilities."""

from pathlib import Path

# Error messages
FILE_NOT_FOUND_MSG = "File not found: {}"


async def read_file(file_path: Path) -> str:
    """Read a file asynchronously."""
    if not file_path.exists():
        raise FileNotFoundError(FILE_NOT_FOUND_MSG.format(file_path))
    return file_path.read_text(encoding="utf-8")


async def write_file(file_path: Path, content: str) -> None:
    """Write a file asynchronously."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


async def file_exists(file_path: Path) -> bool:
    """Check if a file exists."""
    return file_path.exists()


async def ensure_dir(dir_path: Path) -> None:
    """Ensure a directory exists."""
    dir_path.mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path.cwd()

    # Look for common project markers
    markers = [".git", "pyproject.toml", "package.json", "setup.py", "specs"]

    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent

    # If no marker found, use current directory
    return Path.cwd()


def resolve_path(file_path: Path) -> Path:
    """Resolve a path relative to the project root."""
    if file_path.is_absolute():
        return file_path
    return get_project_root() / file_path
