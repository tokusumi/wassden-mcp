"""Unit tests for fs_utils module."""

import os
import tempfile
from pathlib import Path

import pytest

from wassden.lib import fs_utils


@pytest.mark.asyncio
async def test_read_file_success(temp_dir):
    """Test successful file reading."""
    test_file = temp_dir / "test.txt"
    test_content = "Hello, World!"
    test_file.write_text(test_content)

    result = await fs_utils.read_file(test_file)
    assert result == test_content


@pytest.mark.asyncio
async def test_read_file_not_found():
    """Test file not found error."""
    with pytest.raises(FileNotFoundError):
        await fs_utils.read_file(Path("/nonexistent/file.txt"))


@pytest.mark.asyncio
async def test_file_exists_true(temp_dir):
    """Test file_exists returns True for existing file."""
    test_file = temp_dir / "exists.txt"
    test_file.write_text("content")

    result = await fs_utils.file_exists(test_file)
    assert result is True


@pytest.mark.asyncio
async def test_file_exists_false():
    """Test file_exists returns False for non-existing file."""
    result = await fs_utils.file_exists(Path("/nonexistent/file.txt"))
    assert result is False


@pytest.mark.asyncio
async def test_ensure_dir_creates_directory(temp_dir):
    """Test ensure_dir creates directory."""
    new_dir = temp_dir / "new_directory"

    await fs_utils.ensure_dir(new_dir)

    assert new_dir.exists()
    assert new_dir.is_dir()


@pytest.mark.asyncio
async def test_ensure_dir_nested_directories(temp_dir):
    """Test ensure_dir creates nested directories."""
    nested_dir = temp_dir / "level1" / "level2" / "level3"

    await fs_utils.ensure_dir(nested_dir)

    assert nested_dir.exists()
    assert nested_dir.is_dir()


def test_get_project_root_with_git():
    """Test project root detection with .git directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        git_dir = temp_path / ".git"
        git_dir.mkdir()

        subdir = temp_path / "subdir"
        subdir.mkdir()

        # Change to subdir and test
        original_cwd = Path.cwd()
        try:
            os.chdir(subdir)
            root = fs_utils.get_project_root()
            # Resolve paths to handle symlinks (macOS /var -> /private/var)
            assert root.resolve() == temp_path.resolve()
        finally:
            os.chdir(original_cwd)


def test_get_project_root_with_pyproject():
    """Test project root detection with pyproject.toml."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        pyproject = temp_path / "pyproject.toml"
        pyproject.write_text("[build-system]")

        subdir = temp_path / "subdir"
        subdir.mkdir()

        # Change to subdir and test
        original_cwd = Path.cwd()
        try:
            os.chdir(subdir)
            root = fs_utils.get_project_root()
            # Resolve paths to handle symlinks (macOS /var -> /private/var)
            assert root.resolve() == temp_path.resolve()
        finally:
            os.chdir(original_cwd)


def test_resolve_path_absolute():
    """Test resolve_path with absolute path."""
    abs_path = "/absolute/path/to/file"
    result = fs_utils.resolve_path(Path(abs_path))
    assert result == Path(abs_path)


def test_resolve_path_relative():
    """Test resolve_path with relative path."""
    rel_path = "relative/path/to/file"
    result = fs_utils.resolve_path(Path(rel_path))
    expected = fs_utils.get_project_root() / rel_path
    assert result == expected


@pytest.mark.asyncio
async def test_read_file_encoding_utf8(temp_dir):
    """Test reading file with UTF-8 encoding."""
    test_file = temp_dir / "utf8.txt"
    japanese_content = "こんにちは、世界！"
    test_file.write_text(japanese_content, encoding="utf-8")

    result = await fs_utils.read_file(test_file)
    assert result == japanese_content
