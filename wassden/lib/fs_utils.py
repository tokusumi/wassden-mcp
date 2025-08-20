"""File system utilities."""

from pathlib import Path

# Error messages
FILE_NOT_FOUND_MSG = "File not found: {}"


async def read_file(file_path: str) -> str:
    """Read a file asynchronously."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(FILE_NOT_FOUND_MSG.format(file_path))
    return path.read_text(encoding="utf-8")


async def file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return Path(file_path).exists()


async def ensure_dir(dir_path: str) -> None:
    """Ensure a directory exists."""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


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


def resolve_path(file_path: str) -> Path:
    """Resolve a path relative to the project root."""
    path = Path(file_path)
    if path.is_absolute():
        return path
    return get_project_root() / path
