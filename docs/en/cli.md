# CLI Commands Reference

## Overview

wassden provides comprehensive MCP tools for spec-driven development. This document describes the available CLI commands and their usage.

## Basic Commands

### prompt-requirements
Analyze information sufficiency and generate requirements prompts.

```bash
# Default behavior - checks completeness first
uv run wassden prompt-requirements --userInput "Create user authentication system"

# Skip completeness verification
uv run wassden prompt-requirements --userInput "User authentication system" --force
```

### validate-requirements
Verify requirements.md structure and content.

```bash
uv run wassden validate-requirements --requirementsPath specs/requirements.md
```

### prompt-design
Generate design.md creation prompts based on requirements.

```bash
uv run wassden prompt-design --requirementsPath specs/requirements.md
```

### validate-design
Verify design.md structure, content, and traceability.

```bash
uv run wassden validate-design --designPath specs/design.md --requirementsPath specs/requirements.md
```

### prompt-tasks
Generate WBS format tasks.md creation prompts.

```bash
uv run wassden prompt-tasks --designPath specs/design.md --requirementsPath specs/requirements.md
```

### validate-tasks
Verify tasks.md structure, content, and dependencies.

```bash
uv run wassden validate-tasks --tasksPath specs/tasks.md --designPath specs/design.md --requirementsPath specs/requirements.md
```

### analyze-changes
Identify impact of spec changes and generate modification prompts.

```bash
uv run wassden analyze-changes --changedFile specs/requirements.md --allSpecs specs/
```

### get-traceability
Provide current traceability status in report format.

```bash
uv run wassden get-traceability --specsDir specs/
```

## Multi-Language Support

All commands support multi-language output through the `--language` parameter:

### Japanese Mode
```bash
uv run wassden prompt-requirements --userInput "test" --language ja
```

### English Mode
```bash
uv run wassden prompt-requirements --userInput "test" --language en
```

### Auto-Detection Mode
```bash
uv run wassden prompt-requirements --userInput "テストプロジェクト"
# Automatically detects Japanese and responds in Japanese
```

## MCP Server

Start the MCP server for IDE integration:

```bash
uv run wassden start-mcp-server --transport stdio
```

### MCP Tool Features
- All MCP tools automatically detect language from content
- No language parameters needed for MCP tools
- Supports both Japanese and English documentation
- Intelligent language detection for user inputs and file contents

## Language Detection

wassden uses intelligent language detection:

1. **Explicit Parameter** (highest priority): `--language ja/en`
2. **File Content Detection**: Detects language from spec document patterns
3. **User Input Detection**: Detects language from user input text
4. **Default Fallback**: Japanese (ja)

### Spec Document Pattern Detection
- Japanese: "## 概要", "## 用語集", "## スコープ"
- English: "## Overview", "## Glossary", "## Scope"

## Examples

### Complete Workflow
```bash
# 1. Check information completeness and generate requirements
uv run wassden prompt-requirements --userInput "E-commerce system development"

# (If needed) Skip completeness verification with --force
uv run wassden prompt-requirements --userInput "E-commerce system with user authentication, product catalog, shopping cart" --force

# 3. Validate requirements
uv run wassden validate-requirements --requirementsPath specs/requirements.md

# 4. Generate design
uv run wassden prompt-design --requirementsPath specs/requirements.md

# 5. Validate design
uv run wassden validate-design --designPath specs/design.md --requirementsPath specs/requirements.md

# 6. Generate tasks
uv run wassden prompt-tasks --designPath specs/design.md --requirementsPath specs/requirements.md

# 7. Validate tasks
uv run wassden validate-tasks --tasksPath specs/tasks.md --designPath specs/design.md --requirementsPath specs/requirements.md

# 8. Check traceability
uv run wassden get-traceability --specsDir specs/
```

### Multi-Language Workflow
```bash
# English workflow
uv run wassden prompt-requirements --userInput "Create REST API" --language en

# Japanese workflow
uv run wassden prompt-requirements --userInput "RESTAPIを作成" --language ja

# Auto-detection workflow
uv run wassden prompt-requirements --userInput "Create REST API"  # English detected
uv run wassden prompt-requirements --userInput "RESTAPIを作成"    # Japanese detected
```

## Error Handling

All commands provide clear error messages and suggestions:

- File not found errors include creation suggestions
- Validation errors include specific fix instructions
- Language detection failures fallback to Japanese
- MCP server errors include troubleshooting information

## Performance

- All core operations complete in < 1 second
- Sub-millisecond response times for most operations
- Optimized for real-time Agent interactions
- Efficient batch processing for multiple validations