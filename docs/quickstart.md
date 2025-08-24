# Quick Start Guide

Get started with wassden in 5 minutes.

## Prerequisites

- Python 3.12 or higher
- MCP-compatible client (Claude Code, Cursor, GitHub Copilot, etc.)
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/) (`pip install uv`)

## Installation

### Claude Code (CLI)

```bash
claude mcp add wassden -- uvx --from git+https://github.com/tokusumi/wassden-mcp wassden start-mcp-server --transport stdio
# Restart Claude Code
```

### Cursor, GitHub Copilot, Other MCP Clients

Edit your MCP settings file (location varies by client):

```json
{
  "mcpServers": {
    "wassden": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/tokusumi/wassden-mcp",
        "wassden",
        "start-mcp-server",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

## Your First Project

### Step 1: Describe Your Project

```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-requirements \
  --userInput "I want to build a TODO app with user authentication"
```

wassden will analyze your description and either:
- Ask clarifying questions if more information is needed (default behavior)
- Provide a structured prompt for generating requirements (when using --force to skip completeness verification)

### Step 2: Generate Specifications

Use the prompts from wassden with your AI agent (Claude, ChatGPT, etc.) to create:

1. **Requirements** (`specs/requirements.md`)
2. **Design** (`specs/design.md`)
3. **Tasks** (`specs/tasks.md`)

### Step 3: Validate Your Specs

```bash
# Validate each document
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-requirements specs/requirements.md
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-design specs/design.md
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-tasks specs/tasks.md
```

### Step 4: Check Traceability

```bash
# Ensure 100% requirement coverage
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability
```

## Example: TODO App Project

### 1. Initial Analysis

```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-requirements \
  --userInput "TODO app with React frontend, FastAPI backend, PostgreSQL database, JWT authentication"
```

Output:
```
Your project description is complete! Here's a structured prompt for requirements:

## Requirements Generation Prompt

Create a requirements document following EARS format...
[Detailed prompt follows]
```

### 2. Requirements Generation

Copy the prompt to your AI agent. It will generate:

```markdown
# TODO App Requirements Specification

## Overview
A task management application with user authentication...

## Functional Requirements

### REQ-01: User Registration
The system shall allow users to register with email and password

### REQ-02: User Authentication  
The system shall authenticate users using JWT tokens
...
```

### 3. Validation

```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-requirements specs/requirements.md
```

Output:
```
✅ Validation passed!
- All requirements follow EARS format
- Sequential REQ-ID numbering verified
- Test requirements (TR) properly defined
```

### 4. Design Generation

```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-design \
  --requirementsPath specs/requirements.md
```

### 5. Complete Workflow

Continue through design validation, task generation, and implementation with full traceability.

## Using with Claude Code

Once installed, wassden tools are available directly in Claude Code:

```
You: I need to create a chat application

Claude: I'll help you create a chat application. Let me first analyze your requirements for completeness.

[Uses prompt_requirements tool]

I need more information about your chat application:
1. What type of chat (1-on-1, group, or both)?
2. Do you need user authentication?
3. Should messages be persistent?
...
```

## Language Support

wassden automatically detects Japanese or English:

```bash
# Japanese input - responds in Japanese
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-requirements \
  --userInput "タスク管理アプリを作りたい"

# English input - responds in English  
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-requirements \
  --userInput "I want to create a task management app"

# Force specific language
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-requirements \
  --userInput "Create an app" --language ja
```

## Common Commands

### Generate Requirements Prompt
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-requirements --userInput "YOUR_PROJECT_DESCRIPTION"
```

### Validate All Specs
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-requirements specs/requirements.md
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-design specs/design.md
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-tasks specs/tasks.md
```

### Get Traceability Matrix
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability
```

### Analyze Change Impact
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden analyze-changes \
  --changedFile specs/requirements.md \
  --changeDescription "Added new authentication requirement"
```

### Review Task Implementation
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden generate-review-prompt TASK-01-01
```

## Tips for Success

1. **Start Small**: Begin with a simple project description and iterate
2. **Use Validation**: Always validate after generating each document
3. **Maintain Traceability**: Check coverage regularly with `get-traceability`
4. **Review Changes**: Use `analyze-changes` when modifying specifications
5. **Language Auto-Detection**: Let wassden detect language automatically

## Troubleshooting

### wassden tools not appearing in your MCP client

1. Ensure complete restart of your MCP client (not just reload)
2. Check MCP settings file syntax
3. Verify uv is installed: `which uv` or `pip install uv`

### Command not found

```bash
# Install uv
pip install uv
# See: https://docs.astral.sh/uv/getting-started/installation/
```

### Validation failures

Read the validation output carefully - it provides specific guidance on what needs to be fixed.

## Next Steps

- Read the [Tool Reference](tools.md) for detailed tool documentation
- Review [Specification Format Guide](spec-format.md) for document standards
- Check [Examples](ja/spec-example/) for sample specifications
- See [Development Guide](development.md) for contributing

## Getting Help

- Check [GitHub Issues](https://github.com/tokusumi/wassden-mcp/issues)
- Read the [FAQ](https://github.com/tokusumi/wassden-mcp/wiki/FAQ)
- Join discussions in [GitHub Discussions](https://github.com/tokusumi/wassden-mcp/discussions)

---

**Ready to build with structured specifications? Start with `prompt-requirements` and let wassden guide you!**