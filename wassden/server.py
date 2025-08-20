"""MCP server implementation for wassden."""

from pathlib import Path

from fastmcp import FastMCP

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
from .types import Language

# Create FastMCP server instance
mcp = FastMCP("wassden")


async def _determine_language_for_file(file_path: str, is_spec_document: bool = True) -> Language:
    """Determine language from file content, with fallback to Japanese."""
    try:
        content = await fs_utils.read_file(Path(file_path))
        return determine_language(content=content, is_spec_document=is_spec_document)
    except FileNotFoundError:
        return determine_language()


# Register all tools
@mcp.tool(
    name="check_completeness",
    description="Analyze user input for completeness and either generate clarifying questions "
    "or create requirements.md directly",
)
async def check_completeness(user_input: str) -> str:
    """Analyze user input for completeness."""
    language = determine_language(user_input=user_input)
    result = await handle_check_completeness(user_input, language)
    return str(result.content[0].text)


@mcp.tool(
    name="prompt_requirements",
    description="Generate prompt for agent to create requirements.md in EARS format "
    "(deprecated - use check_completeness instead)",
)
async def prompt_requirements(
    project_description: str,
    scope: str = "",
    constraints: str = "",
) -> str:
    """Generate requirements prompt."""
    language = determine_language(user_input=project_description)
    result = await handle_prompt_requirements(project_description, scope, constraints, language)
    return str(result.content[0].text)


@mcp.tool(
    name="validate_requirements",
    description="Validate requirements.md and generate fix instructions if needed",
)
async def validate_requirements(
    requirements_path: str = "specs/requirements.md",
) -> str:
    """Validate requirements document."""
    language = await _determine_language_for_file(requirements_path)
    result = await handle_validate_requirements(Path(requirements_path), language)
    return str(result.content[0].text)


@mcp.tool(
    name="prompt_design",
    description="Generate prompt for agent to create design.md from requirements.md",
)
async def prompt_design(
    requirements_path: str = "specs/requirements.md",
) -> str:
    """Generate design prompt."""
    language = await _determine_language_for_file(requirements_path)
    result = await handle_prompt_design(Path(requirements_path), language)
    return str(result.content[0].text)


@mcp.tool(
    name="validate_design",
    description="Validate design.md structure and traceability, generate fix instructions if needed",
)
async def validate_design(
    design_path: str = "specs/design.md",
    requirements_path: str = "specs/requirements.md",
) -> str:
    """Validate design document."""
    language = await _determine_language_for_file(design_path)
    result = await handle_validate_design(Path(design_path), Path(requirements_path), language)
    return str(result.content[0].text)


@mcp.tool(
    name="prompt_tasks",
    description="Generate prompt for agent to create tasks.md (WBS) from design.md",
)
async def prompt_tasks(
    design_path: str = "specs/design.md",
    requirements_path: str = "specs/requirements.md",
) -> str:
    """Generate tasks prompt."""
    language = await _determine_language_for_file(design_path)
    result = await handle_prompt_tasks(Path(design_path), Path(requirements_path), language)
    return str(result.content[0].text)


@mcp.tool(
    name="validate_tasks",
    description="Validate tasks.md structure and dependencies, generate fix instructions if needed",
)
async def validate_tasks(
    tasks_path: str = "specs/tasks.md",
) -> str:
    """Validate tasks document."""
    language = await _determine_language_for_file(tasks_path)
    result = await handle_validate_tasks(Path(tasks_path), language)
    return str(result.content[0].text)


@mcp.tool(
    name="prompt_code",
    description="Generate prompt for agent to implement code step by step with important guidelines",
)
async def prompt_code(
    tasks_path: str = "specs/tasks.md",
    requirements_path: str = "specs/requirements.md",
    design_path: str = "specs/design.md",
) -> str:
    """Generate implementation prompt."""
    language = await _determine_language_for_file(tasks_path)
    result = await handle_prompt_code(Path(tasks_path), Path(requirements_path), Path(design_path), language)
    return str(result.content[0].text)


@mcp.tool(
    name="analyze_changes",
    description="Analyze changes to specs and generate prompts for dependent modifications",
)
async def analyze_changes(
    changed_file: str,
    change_description: str,
) -> str:
    """Analyze impact of changes."""
    language = await _determine_language_for_file(changed_file)
    result = await handle_analyze_changes(Path(changed_file), change_description, language)
    return str(result.content[0].text)


@mcp.tool(
    name="get_traceability",
    description="Generate current traceability report showing REQ↔DESIGN↔TASK mappings",
)
async def get_traceability(
    requirements_path: str = "specs/requirements.md",
    design_path: str = "specs/design.md",
    tasks_path: str = "specs/tasks.md",
) -> str:
    """Generate traceability report."""
    language = await _determine_language_for_file(requirements_path)
    result = await handle_get_traceability(Path(requirements_path), Path(design_path), Path(tasks_path), language)
    return str(result.content[0].text)


@mcp.tool(
    name="generate_review_prompt",
    description="Generate implementation review prompt for specific TASK-ID to validate implementation quality",
)
async def generate_review_prompt(
    task_id: str,
    tasks_path: str = "specs/tasks.md",
    requirements_path: str = "specs/requirements.md",
    design_path: str = "specs/design.md",
) -> str:
    """Generate review prompt for specific TASK-ID."""
    language = await _determine_language_for_file(tasks_path)
    result = await handle_generate_review_prompt(
        task_id, Path(tasks_path), Path(requirements_path), Path(design_path), language
    )
    return str(result.content[0].text)


def main(
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 3001,
) -> None:
    """Run the MCP server with specified transport.

    Args:
        transport: Transport type - 'stdio', 'sse', or 'streamable-http'
        host: HTTP host (only used for sse/streamable-http transports)
        port: HTTP port (only used for sse/streamable-http transports)
    """
    if transport == "stdio":
        mcp.run()
    elif transport in ["sse", "streamable-http"]:
        mcp.run(transport=transport, host=host, port=port)  # type: ignore[arg-type]
    else:
        msg = f"Invalid transport: {transport}"
        raise ValueError(msg)


if __name__ == "__main__":
    main()
