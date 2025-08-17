# Claude Code Instructions

## Linter and Test Policy
- **NEVER ignore linter errors** - All linting issues must be fixed
- **NEVER ignore test failures** - All tests must pass
- **NEVER disable or skip linter rules** without explicit user approval
- **NEVER disable or skip tests** without explicit user approval
- Always run `make check` after code changes
- If linter/test commands fail, the task is NOT complete

## Commands
- **All checks**: `make check` - Runs format, lint, typecheck, and test in sequence
- CI checks: `make ci` - Runs all checks without modifying files

## Code Quality Standards
- All code must pass linting without warnings
- All code must pass type checking with mypy
- All tests must pass
- Code formatting must be consistent
- No exceptions to quality standards without explicit user permission

## Project Information
- Package name: wassden
- Python version: 3.12+
- Description: MCP-based Spec-Driven Development toolkit with automated Claude Code integration testing
- Main module: wassden.cli:main