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
- **All checks**: `make check` - Runs format, lint, typecheck, test, and CLI verification for dev mode
- **CI dev mode**: `make ci` - Runs all checks for dev mode in CI (format --check, with dev dependencies)
- **CI core mode**: `make ci-core` - Runs checks for core functionality only (no dev dependencies)
- **Format code**: `make format` - Format code with ruff
- **Lint code**: `make lint` - Lint code with ruff check
- **Type check**: `make typecheck` - Type check with mypy
- **Run all tests**: `make test` - Run all tests with coverage using pytest
- **Run core tests**: `make test-core` - Run core tests only (excludes dev-marked tests)
- **Run dev tests**: `make test-dev` - Run dev tests only (requires dev dependencies)
- **Validate examples**: `make validate-examples` - Run integration tests for spec examples in both Japanese and English
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

### Experiment Framework Commands (Dev Mode Only)
**⚠️ NOTE: These commands require development installation with `uv sync --extra dev` and are only available when dev dependencies are installed.**

#### Running Experiments
- **Run experiment**: `uv run wassden experiment run <type>` - Execute validation experiments
  - Types: `ears`, `performance`, `language`, `comprehensive`
  - Options: `--output-format [json|csv]`, `--timeout <seconds>`, `--memory-limit <bytes>`
  - Example: `uv run wassden experiment run performance --output-format json`

#### Configuration Management
- **Save config**: `uv run wassden experiment save-config <type> [name]` - Save experiment configuration
- **Load config**: `uv run wassden experiment load-config <name>` - Display saved configuration
- **Import config**: `uv run wassden experiment import-config <json-file>` - Import from JSON
- **List configs**: `uv run wassden experiment list-configs` - Show all saved configurations
- **Show status**: `uv run wassden experiment status` - Display active experiments

#### Analysis & Comparison
- **Compare experiments**: `uv run wassden experiment compare <exp1> <exp2>` - Statistical comparison
- **Run from config**: `uv run wassden experiment run-experiment <config-name>` - Execute saved config

#### Test Coverage
- **Unit tests**: `pytest tests/unit/test_experiment*.py -v` - Run experiment framework tests
- **Integration tests**: `pytest tests/integration/test_experiment_integration.py -v`
- **E2E tests**: `pytest tests/e2e/test_experiment_e2e.py -v`
- **Dev gate tests**: `pytest tests/test_dev_gate.py -v` - Test dev mode detection

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
- **Install core deps**: `uv sync` - Install core dependencies only
- **Install with dev deps**: `uv sync --extra dev` - Install all dependencies including dev dependencies
- **Pre-commit**: `pre-commit install` - Install pre-commit hooks (runs `make check` and validates spec examples)

## Code Quality Standards
- All code must pass linting without warnings (ruff with extensive rule set)
- All code must pass type checking with mypy (strict typing enforced)
- All tests must pass with coverage reporting
- Code formatting must be consistent (ruff format with 120 char line length)
- No exceptions to quality standards without explicit user permission
- Pre-commit hooks automatically enforce quality standards
- Spec examples must pass validation for both Japanese and English versions

## CI/CD Pipeline
- **Dev CI (ci.yml)**: Runs `make ci` with dev dependencies - tests all functionality including experiments
- **Core CI (ci-mcp.yml)**: Runs `make ci-core` without dev dependencies - tests core MCP functionality only
- **Spec Examples CI**: Validates multi-language documentation when docs or core code changes
- **Pre-commit hooks**: Run quality checks and spec validation before commits
- **Automated validation**: GitHub Actions ensures spec examples remain consistent across languages

## Project Information
- **Package name**: wassden
- **Version**: 0.1.0
- **Python version**: 3.12+
- **License**: MIT
- **Description**: MCP-based Spec-Driven Development toolkit with automated Claude Code integration testing, multi-language support, and experimental validation framework
- **Main module**: wassden.cli:app (Typer CLI application)
- **Repository**: https://github.com/tokusumi/wassden-mcp
- **Test coverage**: 405+ comprehensive tests with full MCP integration testing
- **Languages**: Full Japanese and English support with i18n framework
- **Performance**: Sub-millisecond response times for all core operations
- **Dev Features**: Experiment framework for validation and benchmarking (requires dev installation)

## Key Dependencies

### Core Dependencies
- **FastMCP**: High-performance MCP server framework (>=2.11.3)
- **Typer**: Modern CLI framework with enhanced type safety (>=0.12.5)
- **pycld2**: Compact Language Detector v2 for automatic language detection
- **pytest**: Testing framework with asyncio and coverage support
- **ruff**: Fast Python linter and formatter
- **mypy**: Static type checker

### Development Dependencies (Dev Mode Only)
- **language-tool-python**: Language validation and analysis
- **pandas**: Data analysis for experiment results
- **rich**: Enhanced terminal output for development tools
- **scipy**: Statistical analysis for experiment comparisons
- **numpy**: Numerical computing for performance metrics

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

## Async Testing Best Practices (pytest-asyncio v1.0+)
- **Use real async tests**: NEVER mock `asyncio.run` - test actual async behavior
- **Leverage loop_scope**: Use `@pytest.mark.asyncio(loop_scope="class")` for performance
- **Async fixtures**: Use `@pytest_asyncio.fixture(loop_scope="session")` with proper context managers
- **Concurrent testing**: Test parallel operations with `asyncio.gather()` 
- **Timeout testing**: Use `asyncio.wait_for()` to test actual timeout behavior
- **Race condition testing**: Use `asyncio.Event` objects for controlled execution order
- **Resource management**: Always use async context managers in fixtures
- **Configuration**: Set `asyncio_default_fixture_loop_scope = "function"` in pytest config

### Async Test Patterns
```python
# ✅ Good - Real async testing
@pytest.mark.asyncio
async def test_experiment_execution():
    result = await run_experiment(config)
    assert result.status == ExperimentStatus.COMPLETED

# ✅ Good - Concurrent testing  
@pytest.mark.asyncio
async def test_concurrent_experiments():
    results = await asyncio.gather(
        run_experiment(config1),
        run_experiment(config2),
        return_exceptions=True
    )
    assert all(r.status == ExperimentStatus.COMPLETED for r in results)

# ❌ Bad - Mocking async behavior
@patch("asyncio.run")
def test_experiment_mocked(mock_run):  # Avoid this pattern
```

## Development Workflow
1. Make changes to code
2. Run `make check` to ensure all quality standards are met (dev mode)
3. Pre-commit hooks will automatically run `make check` before commits
4. CI runs either `make ci` (dev mode) or `make ci-core` (core only) based on environment
5. 405+ tests must pass including MCP integration tests

## Test Organization
- **pytest markers**: Tests marked with `@pytest.mark.dev` require dev dependencies
- **Core tests**: Run with `make test-core` or `-m "not dev"` - excludes dev-dependent tests
- **Dev tests**: Run with `make test-dev` or `-m dev` - requires `uv sync --extra dev`
- **CLI verification**: `scripts/verify-core-cli.sh` and `scripts/verify-dev-cli.sh` test CLI entry points