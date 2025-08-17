# Claude Code Instructions

## Linter and Test Policy
- **NEVER ignore linter errors** - All linting issues must be fixed
- **NEVER ignore test failures** - All tests must pass
- **NEVER disable or skip linter rules** without explicit user approval
- **NEVER disable or skip tests** without explicit user approval
- Always run `make check` after code changes
- If linter/test commands fail, the task is NOT complete

## Commands

### Development Commands
- **All checks**: `make check` - Runs format, lint, typecheck, and test with coverage in sequence
- **CI checks**: `make ci` - Runs all checks without modifying files (format --check mode)
- **Format code**: `make format` - Format code with ruff
- **Lint code**: `make lint` - Lint code with ruff check
- **Type check**: `make typecheck` - Type check with mypy
- **Run tests**: `make test` - Run tests with coverage using pytest
- **Help**: `make help` - Show all available make commands

### CLI Testing Commands
- **Local CLI**: `uv run wassden --help` - Show available CLI commands
- **Test functionality**: `uv run wassden check-completeness --userInput "test"` - Test CLI functionality
- **Start MCP server**: `uv run wassden start-mcp-server --transport stdio` - Start MCP server locally

### Development Setup
- **Install deps**: `uv sync` - Install all dependencies including dev dependencies
- **Pre-commit**: `pre-commit install` - Install pre-commit hooks (runs `make check` before commits)

## Code Quality Standards
- All code must pass linting without warnings (ruff with extensive rule set)
- All code must pass type checking with mypy (strict typing enforced)
- All tests must pass with coverage reporting
- Code formatting must be consistent (ruff format with 120 char line length)
- No exceptions to quality standards without explicit user permission
- Pre-commit hooks automatically enforce quality standards

## Project Information
- **Package name**: wassden
- **Version**: 0.1.0
- **Python version**: 3.12+
- **License**: MIT
- **Description**: MCP-based Spec-Driven Development toolkit with automated Claude Code integration testing
- **Main module**: wassden.cli:app (Typer CLI application)
- **Repository**: https://github.com/tokusumi/wassden-mcp
- **Test coverage**: 118+ comprehensive tests with full MCP integration testing

## Key Dependencies
- **FastMCP**: High-performance MCP server framework (>=2.11.3)
- **Typer**: Modern CLI framework with enhanced type safety (>=0.12.5)
- **pytest**: Testing framework with asyncio and coverage support
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker

## Development Workflow
1. Make changes to code
2. Run `make check` to ensure all quality standards are met
3. Pre-commit hooks will automatically run `make check` before commits
4. All CI/CD runs the same checks via `make ci`
5. 118+ tests must pass including MCP integration tests