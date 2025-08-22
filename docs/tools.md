# Tool Reference

Complete documentation for all wassden MCP tools.

## Overview

wassden provides a comprehensive set of tools for Spec-Driven Development (SDD) workflows. All tools support automatic language detection (Japanese/English) and can be used via CLI or MCP integration.

## Prompt Generation Tools

These tools provide structured prompts for AI agents to create high-quality specifications.

### check-completeness

Analyzes user input for completeness and generates requirements prompts.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden check-completeness \
  --userInput "Create a task management API with authentication"
```

**Parameters:**
- `userInput` (required): Project description or requirements
- `--language` (optional): Force language (ja/en), auto-detects by default

**Output:**
- If incomplete: Clarifying questions in detected language
- If complete: Structured prompt for EARS-format requirements generation

### prompt-requirements

Generates specialized requirements generation prompt.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-requirements \
  --projectName "TaskAPI" \
  --description "Task management system" \
  --goals "Enable task CRUD operations"
```

**Parameters:**
- `projectName`: Project name
- `description`: Project description
- `goals`: Project goals
- `constraints` (optional): Technical constraints
- `--language` (optional): Output language

### prompt-design

Generates architectural design prompt from requirements.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-design \
  --requirementsPath specs/requirements.md
```

**Parameters:**
- `requirementsPath`: Path to requirements document
- Auto-detects language from document content

### prompt-tasks

Generates WBS task breakdown prompt from design.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-tasks \
  --designPath specs/design.md
```

**Parameters:**
- `designPath`: Path to design document
- Auto-detects language from document content

### prompt-code

Generates implementation prompt from all specifications.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-code \
  --requirementsPath specs/requirements.md \
  --designPath specs/design.md \
  --tasksPath specs/tasks.md
```

**Parameters:**
- `requirementsPath`: Path to requirements
- `designPath`: Path to design
- `tasksPath`: Path to tasks

### generate-review-prompt

Generates task-specific implementation review prompt.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden generate-review-prompt TASK-01-01
```

**Parameters:**
- `taskId`: Specific task ID to review
- `requirementsPath` (optional): Custom requirements path
- `designPath` (optional): Custom design path
- `tasksPath` (optional): Custom tasks path

**Features:**
- Quality guardrails preventing test tampering
- Project-specific quality checks
- Requirements traceability validation
- Pass/fail criteria with actionable feedback

## Validation Tools

These tools validate agent-generated documents for quality and consistency.

### validate-requirements

Validates requirements document format and completeness.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-requirements \
  specs/requirements.md
```

**Validation Checks:**
- EARS format compliance
- REQ-ID sequential numbering
- TR-ID test requirement numbering
- Section structure completeness
- Language consistency

### validate-design

Validates design document structure and references.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-design \
  specs/design.md
```

**Validation Checks:**
- Component structure
- Interface definitions
- Requirements coverage (all REQs referenced)
- Design pattern consistency

### validate-tasks

Validates task dependencies and coverage.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-tasks \
  specs/tasks.md
```

**Validation Checks:**
- Task ID format
- Dependency DAG (no circular dependencies)
- Requirements coverage (100% REQ + TR)
- Design component coverage
- Test scenario references (DC field)

## Traceability & Analysis Tools

These tools provide project insights and dependency tracking.

### get-traceability

Generates complete traceability matrix.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability
```

**Parameters:**
- `requirementsPath` (optional): Custom requirements path
- `designPath` (optional): Custom design path
- `tasksPath` (optional): Custom tasks path

**Output:**
```json
{
  "requirements_to_design": {
    "REQ-01": ["COMP-01", "COMP-02"],
    "REQ-02": ["COMP-03"]
  },
  "requirements_to_tasks": {
    "REQ-01": ["TASK-01-01", "TASK-01-02"],
    "REQ-02": ["TASK-02-01"]
  },
  "design_to_tasks": {
    "COMP-01": ["TASK-01-01"],
    "COMP-02": ["TASK-01-02"]
  },
  "test_requirements_to_tasks": {
    "TR-01": ["TASK-03-01"],
    "TR-02": ["TASK-03-02"]
  },
  "coverage": {
    "requirements": 100,
    "design": 100,
    "test_requirements": 100
  }
}
```

### analyze-changes

Analyzes impact of specification changes.

**Usage:**
```bash
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden analyze-changes \
  --changedFile specs/requirements.md \
  --changeDescription "Added authentication requirement REQ-10"
```

**Parameters:**
- `changedFile`: Path to modified file
- `changeDescription`: Description of changes

**Output:**
- Affected components list
- Required updates in other documents
- Specific update prompts for each affected document
- Validation checklist

## MCP Integration

All tools are available through MCP when wassden is configured in Claude Code or other MCP clients.

### Tool Names in MCP

| CLI Command | MCP Tool Name |
|------------|--------------|
| `check-completeness` | `check_completeness` |
| `prompt-requirements` | `prompt_requirements` |
| `prompt-design` | `prompt_design` |
| `prompt-tasks` | `prompt_tasks` |
| `prompt-code` | `prompt_code` |
| `generate-review-prompt` | `generate_review_prompt` |
| `validate-requirements` | `validate_requirements` |
| `validate-design` | `validate_design` |
| `validate-tasks` | `validate_tasks` |
| `get-traceability` | `get_traceability` |
| `analyze-changes` | `analyze_changes` |

### Using with Claude Code

Once configured, tools appear in Claude Code's tool palette. Example usage:

```
User: Check if my project description is complete
Assistant: I'll analyze your project description for completeness.

[Uses check_completeness tool]

Based on the analysis, your project description is missing:
1. Specific authentication methods
2. Database technology preferences
3. Performance requirements
...
```

## Language Support

### Automatic Detection

All tools automatically detect language from:
1. User input content (for prompts)
2. Document section headers (for validation)
3. Content analysis using pycld2

### Manual Override

Force specific language output:
```bash
# Force Japanese
--language ja

# Force English  
--language en
```

### Detection Priority

1. Explicit `--language` parameter (highest)
2. Document content patterns
3. User input analysis
4. Default to Japanese (fallback)

## Performance Characteristics

All tools are optimized for speed:

| Tool | Average Response Time |
|------|---------------------|
| check_completeness | <0.01ms |
| prompt_* | <0.003ms |
| validate_* | <0.02ms |
| get_traceability | <0.02ms |
| analyze_changes | <0.02ms |

## Error Handling

### Common Errors

1. **File Not Found**
   ```
   Error: File 'specs/requirements.md' not found
   ```
   Solution: Ensure file exists at specified path

2. **Invalid Format**
   ```
   Error: Invalid EARS format in requirement REQ-01
   ```
   Solution: Follow format guidelines in validation output

3. **Missing Dependencies**
   ```
   Error: Task TASK-01-02 depends on non-existent TASK-01-01
   ```
   Solution: Ensure all referenced IDs exist

### Debug Mode

Enable detailed error output:
```bash
export WASSDEN_DEBUG=1
uv run wassden validate-requirements specs/requirements.md
```

## Best Practices

1. **Start with check-completeness**: Ensure project description is complete
2. **Validate after generation**: Always validate agent-generated documents
3. **Maintain traceability**: Use get-traceability regularly
4. **Track changes**: Use analyze-changes when modifying specs
5. **Review implementations**: Use generate-review-prompt for each task

## Examples

### Complete Workflow Example

```bash
# 1. Check project completeness
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden check-completeness \
  --userInput "Create a REST API for task management with JWT auth"

# 2. Generate requirements (agent uses prompt)
# Agent creates specs/requirements.md

# 3. Validate requirements
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-requirements \
  specs/requirements.md

# 4. Generate design prompt
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-design \
  --requirementsPath specs/requirements.md

# 5. Validate design (after agent creates it)
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-design \
  specs/design.md

# 6. Generate tasks prompt
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden prompt-tasks \
  --designPath specs/design.md

# 7. Validate tasks
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-tasks \
  specs/tasks.md

# 8. Check traceability
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability

# 9. Review specific task implementation
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden generate-review-prompt TASK-01-01
```

## Related Documentation

- [Specification Format Guide](spec-format.md)
- [Validation Rules](validation/)
- [Development Guide](development.md)
- [Performance Benchmarks](performance.md)