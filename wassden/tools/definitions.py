"""Tool definitions for wassden MCP server."""

from typing import Any

tool_definitions: list[dict[str, Any]] = [
    {
        "name": "check_completeness",
        "description": "Analyze user input for completeness and either generate clarifying questions "
        "or create requirements.md directly",
        "inputSchema": {
            "type": "object",
            "properties": {
                "userInput": {
                    "type": "string",
                    "description": "User's project description or requirements input",
                },
            },
            "required": ["userInput"],
        },
    },
    {
        "name": "prompt_requirements",
        "description": "Generate prompt for agent to create requirements.md in EARS format "
        "(deprecated - use check_completeness instead)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "projectDescription": {
                    "type": "string",
                    "description": "Project description",
                },
                "scope": {
                    "type": "string",
                    "description": "Project scope",
                },
                "constraints": {
                    "type": "string",
                    "description": "Technical constraints",
                },
            },
            "required": ["projectDescription"],
        },
    },
    {
        "name": "validate_requirements",
        "description": "Validate requirements.md and generate fix instructions if needed",
        "inputSchema": {
            "type": "object",
            "properties": {
                "requirementsPath": {
                    "type": "string",
                    "description": "Path to requirements.md file",
                    "default": "specs/requirements.md",
                },
            },
        },
    },
    {
        "name": "prompt_design",
        "description": "Generate prompt for agent to create design.md from requirements.md",
        "inputSchema": {
            "type": "object",
            "properties": {
                "requirementsPath": {
                    "type": "string",
                    "description": "Path to requirements.md file",
                    "default": "specs/requirements.md",
                },
            },
        },
    },
    {
        "name": "validate_design",
        "description": "Validate design.md structure and traceability, generate fix instructions if needed",
        "inputSchema": {
            "type": "object",
            "properties": {
                "designPath": {
                    "type": "string",
                    "description": "Path to design.md file",
                    "default": "specs/design.md",
                },
                "requirementsPath": {
                    "type": "string",
                    "description": "Path to requirements.md file for traceability check",
                    "default": "specs/requirements.md",
                },
            },
        },
    },
    {
        "name": "prompt_tasks",
        "description": "Generate prompt for agent to create tasks.md (WBS) from design.md",
        "inputSchema": {
            "type": "object",
            "properties": {
                "designPath": {
                    "type": "string",
                    "description": "Path to design.md file",
                    "default": "specs/design.md",
                },
                "requirementsPath": {
                    "type": "string",
                    "description": "Path to requirements.md file",
                    "default": "specs/requirements.md",
                },
            },
        },
    },
    {
        "name": "validate_tasks",
        "description": "Validate tasks.md structure and dependencies, generate fix instructions if needed",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tasksPath": {
                    "type": "string",
                    "description": "Path to tasks.md file",
                    "default": "specs/tasks.md",
                },
            },
        },
    },
    {
        "name": "prompt_code",
        "description": "Generate prompt for agent to implement code step by step with important guidelines",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tasksPath": {
                    "type": "string",
                    "description": "Path to tasks.md file",
                    "default": "specs/tasks.md",
                },
                "requirementsPath": {
                    "type": "string",
                    "description": "Path to requirements.md file",
                    "default": "specs/requirements.md",
                },
                "designPath": {
                    "type": "string",
                    "description": "Path to design.md file",
                    "default": "specs/design.md",
                },
            },
        },
    },
    {
        "name": "analyze_changes",
        "description": "Analyze changes to specs and generate prompts for dependent modifications",
        "inputSchema": {
            "type": "object",
            "properties": {
                "changedFile": {
                    "type": "string",
                    "description": "Path to the changed spec file",
                },
                "changeDescription": {
                    "type": "string",
                    "description": "Description of what was changed",
                },
            },
            "required": ["changedFile", "changeDescription"],
        },
    },
    {
        "name": "get_traceability",
        "description": "Generate current traceability report showing REQ↔DESIGN↔TASK mappings",
        "inputSchema": {
            "type": "object",
            "properties": {
                "requirementsPath": {
                    "type": "string",
                    "description": "Path to requirements.md file",
                    "default": "specs/requirements.md",
                },
                "designPath": {
                    "type": "string",
                    "description": "Path to design.md file",
                    "default": "specs/design.md",
                },
                "tasksPath": {
                    "type": "string",
                    "description": "Path to tasks.md file",
                    "default": "specs/tasks.md",
                },
            },
        },
    },
]
