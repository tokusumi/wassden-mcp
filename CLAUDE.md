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

### Multi-Language Support Commands
- **Japanese mode**: Add `--language ja` to any command for Japanese output
- **English mode**: Add `--language en` to any command for English output
- **Auto-detection**: Omit `--language` to let the system automatically detect language
- **Examples**:
  - `uv run wassden check-completeness --userInput "test" --language en` - Force English
  - `uv run wassden check-completeness --userInput "テストプロジェクト"` - Auto-detects Japanese
  - `uv run wassden validate-requirements --requirementsPath specs/requirements.md` - Detects from file content
- **MCP Server**: All MCP tools automatically detect language from content without parameters
- **Default Fallback**: Defaults to Japanese (`ja`) when detection is uncertain

### Performance & Benchmarking Commands
- **Run all benchmarks**: `python benchmarks/run_all.py` - Comprehensive performance benchmarks with statistical analysis
- **Performance tests**: `pytest tests/e2e/test_mcp_server.py::TestMCPServerPerformance -v` - Run reproducible performance tests
- **Benchmark results**: View `benchmarks/results.json` for detailed performance metrics
- **Benchmark library**: Use `from wassden.utils.benchmark import PerformanceBenchmark` for custom benchmarks

### Latest Performance Metrics (as of 2024)
- **check_completeness**: 0.01ms mean (ultra-fast completeness analysis)
- **analyze_changes**: 0.02ms mean (rapid change impact assessment)  
- **get_traceability**: 0.02ms mean (instant traceability matrix generation)
- **prompt_requirements**: 0.003ms mean (lightning-fast prompt generation)
- **concurrent_20_tools**: 0.26ms mean (excellent concurrency performance)

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
- **Description**: MCP-based Spec-Driven Development toolkit with automated Claude Code integration testing and multi-language support
- **Main module**: wassden.cli:app (Typer CLI application)
- **Repository**: https://github.com/tokusumi/wassden-mcp
- **Test coverage**: 405+ comprehensive tests with full MCP integration testing
- **Languages**: Full Japanese and English support with i18n framework
- **Performance**: Sub-millisecond response times for all core operations

## Key Dependencies
- **FastMCP**: High-performance MCP server framework (>=2.11.3)
- **Typer**: Modern CLI framework with enhanced type safety (>=0.12.5)
- **pycld2**: Compact Language Detector v2 for automatic language detection
- **pytest**: Testing framework with asyncio and coverage support
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker

## Internationalization (i18n) Features
- **Supported Languages**: Japanese (ja) and English (en)
- **Default Language**: Japanese (`ja`)
- **Translation Files**: Located in `wassden/i18n/locales/{language}/` directory
- **Framework**: Custom i18n singleton pattern with namespace-based organization
- **Coverage**: All user-facing text, error messages, prompts, and validation messages
- **CLI Integration**: Add `--language` parameter to any command
- **Validation**: Multi-language section detection (supports documents in either language)
- **Backwards Compatibility**: All existing functionality works without language parameter

### Intelligent Language Detection
- **Automatic Detection**: Uses `pycld2` library for robust language detection
- **Multi-mode Detection**: 
  - **Spec Document Mode**: Pattern-based detection using section headers (faster, more accurate for spec docs)
  - **General Content Mode**: Full language detection using pycld2
  - **User Input Mode**: Optimized for short user inputs
- **Priority System**:
  1. Explicit `--language` parameter (highest priority)
  2. Language detected from file content (spec patterns if applicable)
  3. Language detected from user input
  4. Default to Japanese (fallback)
- **MCP Server Integration**: Automatic language detection for all MCP tools without explicit language parameters
- **CLI Integration**: Automatic detection when `--language` is not specified
- **Spec Document Patterns**: Recognizes Japanese/English section headers like "## 概要" vs "## Overview"

### Translation Structure
```
wassden/i18n/locales/
├── ja/                 # Japanese translations
│   ├── commands.json   # CLI command messages
│   ├── prompts.json    # Prompt generation text
│   ├── traceability.json # Traceability analysis
│   └── ...
└── en/                 # English translations
    ├── commands.json
    ├── prompts.json
    ├── traceability.json
    └── ...
```

## Development Workflow
1. Make changes to code
2. Run `make check` to ensure all quality standards are met
3. Pre-commit hooks will automatically run `make check` before commits
4. All CI/CD runs the same checks via `make ci`
5. 405+ tests must pass including MCP integration tests