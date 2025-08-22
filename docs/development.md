# Development Guide

This document contains detailed information for developers working with wassden, including installation options, development setup, testing, and contributing guidelines.

## Installation Methods

### Production Installation

```bash
# Direct install from GitHub (recommended)
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden

# Or with pip
pip install git+https://github.com/tokusumi/wassden-mcp
```

### Development Installation

```bash
# Clone and install for development
git clone https://github.com/tokusumi/wassden-mcp
cd wassden-mcp
uv sync  # Installs all dependencies including dev dependencies
```

### Development MCP Setup

For development with local installation:

```json
{
  "mcpServers": {
    "wassden": {
      "command": "uv",
      "args": ["run", "wassden", "start-mcp-server", "--transport", "stdio"],
      "cwd": "/path/to/wassden-mcp",
      "env": {}
    }
  }
}
```

## Transport Options

wassden supports multiple transport protocols for maximum compatibility:

- **stdio** (default): Standard input/output for Claude Code
- **sse**: Server-Sent Events for HTTP-based communication  
- **streamable-http**: Streamable HTTP for web-based clients

### Starting the Server

```bash
# Start with stdio (default for Claude Code)
uv run wassden start-mcp-server --transport stdio

# Start with SSE
uv run wassden start-mcp-server --transport sse --host 127.0.0.1 --port 3001

# Start with streamable-http
uv run wassden start-mcp-server --transport streamable-http --host 0.0.0.0 --port 3001
```

## Development Commands

### Essential Commands

```bash
# Install development dependencies
uv sync

# Run all quality checks (format, lint, typecheck, test)
make check

# Run CI checks without modifying files
make ci

# Individual checks
make format      # Format code with ruff
make lint        # Lint code with ruff check
make typecheck   # Type check with mypy
make test        # Run tests with coverage

# Validate specification examples
make validate-examples
```

### Testing CLI Locally

```bash
# Show available commands
uv run wassden --help

# Test completeness check (auto-detects Japanese)
uv run wassden check-completeness --userInput "テストプロジェクト"

# Test with English
uv run wassden check-completeness --userInput "test project" --language en

# Test validation
uv run wassden validate-requirements specs/requirements.md
uv run wassden validate-design specs/design.md
uv run wassden validate-tasks specs/tasks.md

# Test traceability
uv run wassden get-traceability
```

## Project Structure

```
wassden-mcp/
├── wassden/
│   ├── handlers/           # Tool implementation handlers
│   │   ├── completeness.py # Project completeness analysis
│   │   ├── requirements.py # Requirements prompt generation
│   │   ├── design.py       # Design prompt generation
│   │   ├── tasks.py        # Tasks prompt generation
│   │   ├── code_analysis.py # Code review and analysis
│   │   └── traceability.py  # Traceability matrix generation
│   ├── lib/               # Core functionality
│   │   ├── validate.py    # Validation logic
│   │   ├── traceability.py # Traceability utilities
│   │   ├── fs_utils.py    # File system utilities
│   │   └── prompts.py     # Prompt templates
│   ├── i18n/              # Internationalization
│   │   ├── __init__.py    # i18n singleton
│   │   └── locales/       # Translation files
│   │       ├── ja/        # Japanese translations
│   │       └── en/        # English translations
│   ├── tools/             # MCP tool definitions
│   │   └── definitions.py # Tool interfaces
│   ├── server.py          # FastMCP server implementation
│   └── cli.py             # Typer CLI interface
├── specs/                 # Generated specifications (examples)
│   ├── requirements.md
│   ├── design.md
│   └── tasks.md
├── tests/                 # Comprehensive test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end MCP tests
├── benchmarks/            # Performance benchmarks
│   ├── run_all.py        # Run all benchmarks
│   └── results.json      # Benchmark results
├── docs/                  # Documentation
│   ├── ja/               # Japanese documentation
│   ├── en/               # English documentation
│   └── validation/       # Validation rule details
├── pyproject.toml        # Project configuration
├── Makefile              # Development commands
└── CLAUDE.md             # Claude Code instructions
```

## Configuration

### Default Paths

The default specification paths can be overridden:

```python
{
    "requirementsPath": "specs/requirements.md",
    "designPath": "specs/design.md",
    "tasksPath": "specs/tasks.md"
}
```

### Validation Rules

wassden enforces strict validation rules:

- **EARS Format**: Requirements must follow "システムは...すること" pattern (Japanese) or "The system shall..." (English)
- **REQ-ID Format**: Sequential numbering (REQ-01, REQ-02, ...)
- **TR-ID Format**: Test requirements numbering (TR-01, TR-02, ...)
- **100% Traceability**: All requirements (REQ + TR) must be referenced in design and tasks
- **Test Coverage**: All test scenarios must be referenced in tasks via DC field
- **Design Coverage**: All design components must be referenced in tasks
- **Dependencies**: Task dependencies checked for circular references

## Testing

### Running Tests

```bash
# Run all tests with coverage
make test

# Run specific test categories
pytest tests/unit -v           # Unit tests only
pytest tests/integration -v    # Integration tests
pytest tests/e2e -v            # End-to-end MCP tests

# Run with specific markers
pytest -m "not slow"           # Skip slow tests
pytest -k "test_validate"      # Run tests matching pattern

# Run performance benchmarks
python benchmarks/run_all.py
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
uv add --dev pre-commit
pre-commit install

# Manually run hooks
pre-commit run --all-files
```

The hooks automatically run:
- Code formatting (ruff format)
- Linting (ruff check)
- Type checking (mypy)
- Tests (pytest)
- Spec example validation

## Performance Benchmarking

wassden includes a comprehensive benchmarking system:

```bash
# Run all benchmarks
python benchmarks/run_all.py

# View results
cat benchmarks/results.json
```

Expected performance metrics:
- **check_completeness**: <0.01ms average
- **analyze_changes**: <0.02ms average
- **get_traceability**: <0.02ms average
- **prompt_requirements**: <0.003ms average
- **concurrent_20_tools**: <0.3ms average

## Language Support

### Multi-Language Features

wassden supports Japanese and English with automatic detection:

- **Auto-detection**: Uses pycld2 for language detection
- **Manual override**: Use `--language ja` or `--language en`
- **Translation files**: Located in `wassden/i18n/locales/`

### Adding Translations

To add or modify translations:

1. Edit translation files in `wassden/i18n/locales/{language}/`
2. Follow the existing JSON structure
3. Test with both languages

## Contributing

### Development Workflow

1. Fork the repository
2. Create your feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes
4. Run quality checks
   ```bash
   make check
   ```
5. Commit your changes
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. Push to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
7. Open a Pull Request

### Code Style Guidelines

- **Formatting**: Use ruff format (120 char line length)
- **Linting**: Follow ruff rules (extensive rule set)
- **Type hints**: Required for all functions (mypy strict)
- **Docstrings**: Required for public functions
- **Tests**: Required for new features (maintain >90% coverage)

### Continuous Integration

All pull requests are automatically validated through GitHub Actions:

- Code formatting check
- Linting validation
- Type checking
- Full test suite with coverage
- Spec example validation (both languages)

## Framework & Dependencies

### Core Dependencies

- **Python**: 3.12+ required
- **FastMCP**: >=2.11.3 - High-performance MCP server framework
- **Typer**: >=0.12.5 - Modern CLI framework
- **pycld2**: Language detection library
- **pydantic**: >=2.0 - Data validation

### Development Dependencies

- **pytest**: >=7.4.0 - Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **ruff**: >=0.5.0 - Fast Python linter and formatter
- **mypy**: >=1.10.0 - Static type checker
- **pre-commit**: Git hooks management

## Troubleshooting

### Common Issues

1. **MCP server not connecting**
   - Ensure Claude Code is fully restarted
   - Check `~/.claude/settings.json` syntax
   - Verify uv is installed and in PATH

2. **Language detection issues**
   - Use explicit `--language` parameter
   - Ensure input text has sufficient content

3. **Performance issues**
   - Run benchmarks to identify bottlenecks
   - Check for large specification files
   - Verify system resources

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export WASSDEN_DEBUG=1

# Run with debug output
uv run wassden check-completeness --userInput "test"
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [EARS Format Guide](docs/validation/ears.md)
- [Traceability Rules](docs/validation/traceability.md)

## Support

For issues or questions:
1. Check existing [GitHub Issues](https://github.com/tokusumi/wassden-mcp/issues)
2. Read the [documentation](https://github.com/tokusumi/wassden-mcp/tree/main/docs)
3. Open a new issue with detailed information

---

**Note**: This document is continuously updated. For the latest information, check the [GitHub repository](https://github.com/tokusumi/wassden-mcp).