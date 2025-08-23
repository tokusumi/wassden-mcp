"""Common type definitions for wassden."""

from enum import Enum
from pathlib import Path

from pydantic import BaseModel

from wassden.language_types import Language
from wassden.lib import fs_utils
from wassden.lib.language_detection import determine_language


class TextContent(BaseModel):
    """Text content structure for handler responses."""

    type: str = "text"
    text: str


class HandlerResponse(BaseModel):
    """Standard response structure for all handlers."""

    content: list[TextContent]


class TransportType(str, Enum):
    """Available transport types for MCP server."""

    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable-http"


class SpecDocuments(BaseModel):
    """Container for all three spec documents with their paths, language, and lazy-loaded content."""

    # Path fields - always set (non-optional)
    requirements_path: Path
    """Path to requirements.md file."""

    design_path: Path
    """Path to design.md file."""

    tasks_path: Path
    """Path to tasks.md file."""

    # Language field
    language: Language = Language.JAPANESE
    """Language for processing these specs."""

    # Private content cache fields
    _requirements: str | None = None
    _design: str | None = None
    _tasks: str | None = None

    # Flags to track if we've attempted to load (to avoid re-reading non-existent files)
    _requirements_loaded: bool = False
    _design_loaded: bool = False
    _tasks_loaded: bool = False

    model_config = {"extra": "forbid"}

    @property
    def feature_dir(self) -> Path:
        """Get the feature directory containing these specs."""
        return self.requirements_path.parent

    @property
    def feature_name(self) -> str:
        """Extract feature name from spec paths."""
        feature_dir = self.feature_dir

        # If parent is "specs", this is a root-level spec
        if feature_dir.name == "specs" or feature_dir == Path("specs"):
            return ""

        # Otherwise, return the feature directory name
        return feature_dir.name

    async def get_requirements(self) -> str | None:
        """Get requirements content, loading lazily if needed."""
        if not self._requirements_loaded:
            try:
                self._requirements = await fs_utils.read_file(self.requirements_path)
            except FileNotFoundError:
                self._requirements = None
            self._requirements_loaded = True
        return self._requirements

    async def get_design(self) -> str | None:
        """Get design content, loading lazily if needed."""
        if not self._design_loaded:
            try:
                self._design = await fs_utils.read_file(self.design_path)
            except FileNotFoundError:
                self._design = None
            self._design_loaded = True
        return self._design

    async def get_tasks(self) -> str | None:
        """Get tasks content, loading lazily if needed."""
        if not self._tasks_loaded:
            try:
                self._tasks = await fs_utils.read_file(self.tasks_path)
            except FileNotFoundError:
                self._tasks = None
            self._tasks_loaded = True
        return self._tasks

    # Legacy properties for backwards compatibility (read-only)
    @property
    def requirements(self) -> str | None:
        """Get cached requirements content (synchronous, may be None if not loaded)."""
        return self._requirements

    @property
    def design(self) -> str | None:
        """Get cached design content (synchronous, may be None if not loaded)."""
        return self._design

    @property
    def tasks(self) -> str | None:
        """Get cached tasks content (synchronous, may be None if not loaded)."""
        return self._tasks

    @classmethod
    async def from_paths(
        cls,
        requirements_path: Path | None = None,
        design_path: Path | None = None,
        tasks_path: Path | None = None,
        language: Language | None = None,
    ) -> "SpecDocuments":
        """Create SpecDocuments with resolved paths and auto-detected language.

        Args:
            requirements_path: Optional path to requirements.md
            design_path: Optional path to design.md
            tasks_path: Optional path to tasks.md
            language: Language for processing these specs (auto-detected if None)

        Returns:
            SpecDocuments with all paths and language set (content not loaded)

        Raises:
            ValueError: If all paths are None
        """
        if not any([requirements_path, design_path, tasks_path]):
            raise ValueError("At least one path must be provided")

        # Auto-resolve all paths from any given reference
        reference_path = requirements_path or design_path or tasks_path
        assert reference_path is not None  # Already checked above
        feature_dir = reference_path.parent

        resolved_requirements_path = requirements_path or feature_dir / "requirements.md"
        resolved_design_path = design_path or feature_dir / "design.md"
        resolved_tasks_path = tasks_path or feature_dir / "tasks.md"

        # Auto-detect language if not provided
        loaded_content = {}
        if language is None:
            # Try to detect language from the first available file
            for spec_type, path in [
                ("requirements", resolved_requirements_path),
                ("design", resolved_design_path),
                ("tasks", resolved_tasks_path),
            ]:
                try:
                    content = await fs_utils.read_file(path)
                    language = determine_language(content=content, is_spec_document=True)
                    # Cache the content we just loaded
                    loaded_content[spec_type] = content
                    break
                except FileNotFoundError:
                    continue

            # Fallback to Japanese if no files found or detection failed
            if language is None:
                language = Language.JAPANESE

        # Create instance
        instance = cls(
            requirements_path=resolved_requirements_path,
            design_path=resolved_design_path,
            tasks_path=resolved_tasks_path,
            language=language,
        )

        # Pre-populate cache with content loaded during language detection
        if "requirements" in loaded_content:
            instance._requirements = loaded_content["requirements"]
            instance._requirements_loaded = True
        if "design" in loaded_content:
            instance._design = loaded_content["design"]
            instance._design_loaded = True
        if "tasks" in loaded_content:
            instance._tasks = loaded_content["tasks"]
            instance._tasks_loaded = True

        return instance

    @classmethod
    async def from_feature_dir(cls, feature_dir: Path, language: Language | None = None) -> "SpecDocuments":
        """Create SpecDocuments from a feature directory with auto-detected language.

        Args:
            feature_dir: Directory containing spec files (e.g., specs/auth)
            language: Language for processing these specs (auto-detected if None)

        Returns:
            SpecDocuments with all paths and language set (content not loaded)
        """
        return await cls.from_paths(
            requirements_path=feature_dir / "requirements.md",
            design_path=feature_dir / "design.md",
            tasks_path=feature_dir / "tasks.md",
            language=language,
        )
