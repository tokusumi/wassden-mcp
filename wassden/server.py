"""MCP server implementation for wassden."""

from fastmcp import FastMCP

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

# Create FastMCP server instance
mcp = FastMCP("wassden")


# Register all tools
@mcp.tool(
    name="check_completeness",
    description="Analyze user input for completeness and either generate clarifying questions "
    "or create requirements.md directly",
)
async def check_completeness(user_input: str) -> str:
    """Analyze user input for completeness."""
    result = await handle_check_completeness({"userInput": user_input})
    return str(result["content"][0]["text"])


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
    result = await handle_prompt_requirements(
        {
            "projectDescription": project_description,
            "scope": scope,
            "constraints": constraints,
        }
    )
    return str(result["content"][0]["text"])


@mcp.tool(
    name="validate_requirements",
    description="Validate requirements.md and generate fix instructions if needed",
)
async def validate_requirements(
    requirements_path: str = "specs/requirements.md",
) -> str:
    """Validate requirements document."""
    result = await handle_validate_requirements(
        {
            "requirementsPath": requirements_path,
        }
    )
    return str(result["content"][0]["text"])


@mcp.tool(
    name="prompt_design",
    description="Generate prompt for agent to create design.md from requirements.md",
)
async def prompt_design(
    requirements_path: str = "specs/requirements.md",
) -> str:
    """Generate design prompt."""
    result = await handle_prompt_design(
        {
            "requirementsPath": requirements_path,
        }
    )
    return str(result["content"][0]["text"])


@mcp.tool(
    name="validate_design",
    description="Validate design.md structure and traceability, generate fix instructions if needed",
)
async def validate_design(
    design_path: str = "specs/design.md",
    requirements_path: str = "specs/requirements.md",
) -> str:
    """Validate design document."""
    result = await handle_validate_design(
        {
            "designPath": design_path,
            "requirementsPath": requirements_path,
        }
    )
    return str(result["content"][0]["text"])


@mcp.tool(
    name="prompt_tasks",
    description="Generate prompt for agent to create tasks.md (WBS) from design.md",
)
async def prompt_tasks(
    design_path: str = "specs/design.md",
    requirements_path: str = "specs/requirements.md",
) -> str:
    """Generate tasks prompt."""
    result = await handle_prompt_tasks(
        {
            "designPath": design_path,
            "requirementsPath": requirements_path,
        }
    )
    return str(result["content"][0]["text"])


@mcp.tool(
    name="validate_tasks",
    description="Validate tasks.md structure and dependencies, generate fix instructions if needed",
)
async def validate_tasks(
    tasks_path: str = "specs/tasks.md",
) -> str:
    """Validate tasks document."""
    result = await handle_validate_tasks(
        {
            "tasksPath": tasks_path,
        }
    )
    return str(result["content"][0]["text"])


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
    result = await handle_prompt_code(
        {
            "tasksPath": tasks_path,
            "requirementsPath": requirements_path,
            "designPath": design_path,
        }
    )
    return str(result["content"][0]["text"])


@mcp.tool(
    name="analyze_changes",
    description="Analyze changes to specs and generate prompts for dependent modifications",
)
async def analyze_changes(
    changed_file: str,
    change_description: str,
) -> str:
    """Analyze impact of changes."""
    result = await handle_analyze_changes(
        {
            "changedFile": changed_file,
            "changeDescription": change_description,
        }
    )
    return str(result["content"][0]["text"])


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
    result = await handle_get_traceability(
        {
            "requirementsPath": requirements_path,
            "designPath": design_path,
            "tasksPath": tasks_path,
        }
    )
    return str(result["content"][0]["text"])


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
