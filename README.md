# wassden

[![CI](https://github.com/tokusumi/wassden-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/tokusumi/wassden-mcp/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-passing-green)](https://github.com/tokusumi/wassden-mcp/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)

A powerful **READ-ONLY** MCP-based Spec-Driven Development (SDD) toolkit that transforms any LLM into a comprehensive development agent with structured specification generation and validation capabilities.

> "Spec-first development made intelligent and systematic"

## 🔒 Security Guarantee

**wassden is a completely READ-ONLY MCP server** with the following security guarantees:

- ✅ **No file writing capabilities** - Cannot create, modify, or delete any files
- ✅ **Analysis only** - Reads existing files for validation and traceability analysis  
- ✅ **Prompt generation** - Generates structured prompts for agents to create specifications
- ✅ **Safe integration** - Zero risk of unintended filesystem modifications

## 🎯 Core Philosophy

**wassden** is designed as an **intelligent prompt orchestrator** for SDD workflows. It doesn't generate documents itself—instead, it:

- **🧠 Provides expert-crafted prompts** that guide AI agents to create high-quality specifications
- **🤝 Enables seamless agent collaboration** through standardized SDD workflows  
- **✅ Validates generated documents** to ensure consistency and completeness
- **📋 Maintains project coherence** across the entire development lifecycle

The tool acts as your **SDD methodology expert**, ensuring AI agents follow best practices while you focus on the creative aspects of development.

## ✨ Key Features

- **🎯 Spec-Driven Development**: Complete Requirements → Design → Tasks → Code workflow
- **🔄 Intelligent Validation**: Automated quality checks with actionable feedback and **100% traceability enforcement**
- **📊 Traceability Management**: Complete REQ↔DESIGN↔TASK + TR↔TEST-SCENARIO mapping with mandatory 100% coverage validation
- **🚀 Progressive Prompting**: Step-by-step guidance for high-quality deliverables
- **🛠️ MCP Integration**: Seamless integration with Claude Code and other MCP clients via FastMCP
- **🌍 Multi-Language**: Full Japanese and English support with automatic language detection and intelligent validation  
- **🧪 Robust Testing**: [Comprehensive test suite](https://github.com/tokusumi/wassden-mcp/actions/workflows/ci.yml) with 405+ tests and consistently fast response times (<0.01ms avg)

## 🎪 Demonstrations

Demo videos showcasing the development workflow will be added to this section soon.  
Detailed usage examples will be provided in the videos—please stay tuned!

## 🚀 Quick Start

### Installation

```bash
# Direct install from GitHub (recommended)
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden

# Or development installation
git clone https://github.com/tokusumi/wassden-mcp
cd wassden-py
uv pip install -e .
```

### MCP Integration

#### Transport Options

wassden supports multiple transport protocols for maximum compatibility:

- **stdio** (default): Standard input/output for Claude Code
- **sse**: Server-Sent Events for HTTP-based communication
- **streamable-http**: Streamable HTTP for web-based clients

#### Claude Code Setup (Recommended)

1. **Install uv (if not already installed)**

   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Via pip
   pip install uv
   ```

2. **Add to Claude Code settings**

   Edit `~/.claude/settings.json`:

   **Using stdio transport (recommended for Claude Code)**
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
         ],
         "env": {}
       }
     }
   }
   ```

3. **Restart Claude Code**
   - Complete application restart required
   - wassden tools will appear in tool palette

4. **Verify connection**
   ```bash
   # Manual verification
   uvx --from git+https://github.com/tokusumi/wassden-mcp wassden check-completeness --userInput "test project"
   ```

#### IDE Compatibility

wassden provides flexible transport options for MCP-compatible environments:

- **Claude Code**: Full support via stdio transport (recommended)

The transport flexibility ensures wassden can be integrated into any MCP-compatible development environment.

#### Alternative Installation Methods

**1. Development Installation**
```bash
git clone https://github.com/tokusumi/wassden-mcp
cd wassden-py
uv sync
```

Then use uv run in settings:
```json
{
  "mcpServers": {
    "wassden": {
      "command": "uv",
      "args": ["run", "wassden", "start-mcp-server", "--transport", "stdio"],
      "cwd": "/path/to/wassden-py",
      "env": {}
    }
  }
}
```

**2. Claude Code CLI**
For quick setup with Claude Code CLI:
```bash
claude mcp add wassden "uvx --from git+https://github.com/tokusumi/wassden-mcp wassden start-mcp-server --transport stdio"
```

### Basic Usage

1. **Complete Project Analysis & Requirements Generation**

   ```bash
   # Auto-detect language from input (recommended)
   uvx --from git+https://github.com/tokusumi/wassden-mcp wassden check-completeness --userInput "Python FastAPI project"
   
   # Force specific language
   uvx --from git+https://github.com/tokusumi/wassden-mcp wassden check-completeness --userInput "Your project description" --language ja
   ```
   
   This command analyzes your input for completeness and:
   - **Automatically detects language** from your input text (English/Japanese)
   - If information is missing: Returns clarifying questions (in detected/chosen language)
   - If information is sufficient: **Provides structured prompts** for the agent to generate EARS format requirements.md

2. **Agent-Driven Document Creation**
   
   The agent uses wassden's prompts to create specifications:
   - **Requirements**: Agent generates `specs/requirements.md` using wassden's EARS-formatted prompts
   - **Design**: Agent creates `specs/design.md` following wassden's architectural guidance
   - **Tasks**: Agent produces `specs/tasks.md` with wassden's WBS structure

3. **Quality Assurance Through Validation**
   
   wassden validates the agent-generated documents with automatic language detection:
   ```bash
   # Auto-detects document language and provides appropriate feedback
   uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-requirements specs/requirements.md
   uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-design specs/design.md
   uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-tasks specs/tasks.md
   ```
   
   **Auto-detection features:**
   - Detects document language from content (Japanese/English section headers)
   - Provides validation feedback in the detected language
   - Supports mixed-language environments seamlessly

4. **Task-Specific Implementation Review**
   
   Generate structured review prompts for each TASK-ID implementation:
   ```bash
   uvx --from git+https://github.com/tokusumi/wassden-mcp wassden generate-review-prompt TASK-01-01
   ```
   
   This provides agents with:
   - **Quality guardrails** preventing test tampering and TODO shortcuts
   - **Project-specific quality checks** (linting, formatting, testing)
   - **Requirements traceability** validation against REQ/TR specifications
   - **Pass/fail criteria** with actionable feedback for fixes

## 🛠️ Available Tools

### 📝 Prompt Generation Tools
*These tools provide structured prompts for AI agents to create specifications (auto-detects language or supports explicit --language)*

| Tool                     | Purpose                                     | Input                                                   | Agent Output                                |
| ------------------------ | ------------------------------------------- | ------------------------------------------------------- | ------------------------------------------- |
| `check-completeness`     | Analyze input & provide requirements prompt | User description (auto-detects) + optional `--language` | Questions or structured requirements prompt |
| `prompt-requirements`    | Generate specialized requirements prompt    | Project details (auto-detects) + optional `--language`  | EARS-formatted requirements prompt          |
| `prompt-design`          | Generate design document prompt             | Requirements path (auto-detects language)               | Architectural design prompt                 |
| `prompt-tasks`           | Generate WBS tasks prompt                   | Design path (auto-detects language)                     | Task breakdown prompt                       |
| `prompt-code`            | Generate implementation prompt              | All spec paths (auto-detects language)                  | Implementation guide prompt                 |
| `generate-review-prompt` | Generate TASK-specific review prompt        | Task ID + spec paths (auto-detects language)            | Quality review prompt with guardrails       |

### ✅ Validation Tools  
*These tools validate agent-generated documents for quality and consistency (auto-detects document language)*

| Tool                    | Purpose                       | Input                                     | Output            |
| ----------------------- | ----------------------------- | ----------------------------------------- | ----------------- |
| `validate-requirements` | Validate requirements quality | Requirements path (auto-detects language) | Validation report |
| `validate-design`       | Validate design structure     | Design path (auto-detects language)       | Validation report |
| `validate-tasks`        | Validate task dependencies    | Tasks path (auto-detects language)        | Validation report |

> **📋 Validation Standards**: wassden enforces **100% traceability** - all requirements must be referenced in design and tasks. See [Validation Documentation](docs/validation/) for detailed requirements and examples.

### 📊 Traceability & Analysis Tools
*These tools provide project insights, dependency tracking, and change impact analysis*

| Tool               | Purpose                                 | Input                      | Output                           |
| ------------------ | --------------------------------------- | -------------------------- | -------------------------------- |
| `get-traceability` | Complete traceability matrix generation | Spec paths (optional)      | Full REQ↔DESIGN↔TASK mapping     |
| `analyze-changes`  | Impact analysis for spec changes        | Changed file + description | Dependency impact & update guide |

#### 🔗 Traceability Features

wassden provides comprehensive traceability management that ensures full project coherence:

- **📋 Complete Mapping**: Automated REQ↔DESIGN↔TASK + TR↔TEST-SCENARIO relationship tracking
- **🔍 Impact Analysis**: Identifies dependencies when specifications change
- **📝 Update Guidance**: Generates specific prompts for updating affected documents
- **✅ Coverage Validation**: Ensures 100% traceability compliance for all requirements and test scenarios

> **💡 Pro Tip**: Use `analyze-changes` after modifying any spec file to identify all dependent documents that need updates. The tool provides step-by-step guidance for maintaining project consistency.

## 📁 Project Structure

```
wassden-py/
├── wassden/
│   ├── handlers/           # Tool implementation handlers
│   │   ├── completeness.py
│   │   ├── requirements.py
│   │   ├── design.py
│   │   ├── tasks.py
│   │   ├── code_analysis.py
│   │   └── traceability.py
│   ├── lib/               # Core functionality
│   │   ├── validate.py
│   │   ├── traceability.py
│   │   ├── fs_utils.py
│   │   └── prompts.py
│   ├── tools/             # MCP tool definitions
│   │   └── definitions.py
│   ├── server.py          # FastMCP server
│   └── cli.py             # CLI interface
├── specs/                 # Generated specifications
│   ├── requirements.md
│   ├── design.md
│   └── tasks.md
├── tests/                 # Comprehensive test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── pyproject.toml         # Project configuration
```

## 🧩 Language & Framework Support

- **Primary**: Python 3.12+
- **Human Languages**: Japanese (ja) and English (en) with full i18n support
- **MCP Framework**: FastMCP for high-performance MCP server implementation
- **CLI**: Typer for modern command-line interface with enhanced type safety
- **Testing**: pytest + pytest-asyncio with [405+ comprehensive tests (100% passing)](https://github.com/tokusumi/wassden-mcp/actions/workflows/ci.yml)
- **Performance**: Sub-millisecond response times with concurrent load support
- **Code Quality**: ruff + mypy for linting and type checking
- **Standards**: EARS format, WBS structure, 100% Traceability matrices
- **Internationalization**: Namespace-based translation system with automatic language detection

## 🧪 Development Mode Features (Experimental)

### Experiment Framework (Dev Mode Only)

**⚠️ NOTE: These features are only available in development mode and require installation with dev dependencies.**

The experiment framework provides validation and benchmarking capabilities for the wassden toolkit itself:

```bash
# Install with dev dependencies
git clone https://github.com/tokusumi/wassden-mcp
cd wassden-py
uv sync  # Installs all dependencies including dev extras

# Experiment CLI commands (dev mode only)
uv run wassden experiment run <type>           # Run experiments
uv run wassden experiment save-config <type>   # Save experiment config
uv run wassden experiment load-config <name>   # Load experiment config  
uv run wassden experiment list-configs         # List available configs
uv run wassden experiment compare <exp1> <exp2> # Compare experiment results
```

#### Available Experiment Types

- **ears**: EARS pattern compliance validation (REQ-01)
- **performance**: Performance benchmarking (REQ-02)
- **language**: Language detection accuracy testing (REQ-03)
- **comprehensive**: Full validation suite

#### Key Features

- **Statistical Analysis**: Mean, variance, std deviation, 95% confidence intervals (REQ-04)
- **Structured Output**: JSON/CSV export formats (REQ-05)
- **Configuration Management**: YAML-based experiment configs (REQ-06)
- **Comparative Analysis**: Statistical significance testing between experiments (REQ-07)
- **Resource Constraints**: 10-minute timeout, 100MB memory limit (NFR-01, NFR-02)

#### Example Usage

```bash
# Run EARS validation experiment
uv run wassden experiment run ears --output-format json

# Run performance benchmark with custom config
uv run wassden experiment run performance --config-path ./my-config.yaml

# Compare two experiment results
uv run wassden experiment compare exp-001 exp-002 --output-format csv
```

## 🎯 Use Cases

### For Development Teams

- **Requirement Analysis**: Systematic requirements gathering with gap analysis
- **Design Documentation**: Structured design with automatic traceability
- **Project Planning**: WBS generation with dependency management
- **Quality Assurance**: Built-in validation and feedback loops

### For AI Agents

- **Structured Prompting**: Progressive prompts for complex development tasks
- **Context Preservation**: Maintains context across development phases
- **Error Recovery**: Validation-driven error detection and correction
- **Change Management**: Impact analysis for specification changes

### For Technical Writers

- **Documentation Generation**: Automated prompt generation for technical documentation
- **Consistency Checking**: Format and structure validation
- **Cross-reference Management**: Automatic traceability link generation

## 🔧 Configuration

### Default Paths

```python
{
    "requirementsPath": "specs/requirements.md",
    "designPath": "specs/design.md",
    "tasksPath": "specs/tasks.md"
}
```

### Validation Rules

- **EARS Format**: Requirements must follow "システムは...すること" pattern
- **REQ-ID Format**: Sequential numbering (REQ-01, REQ-02, ...)
- **TR-ID Format**: Test requirements numbering (TR-01, TR-02, ...)
- **100% Traceability**: All requirements (REQ + TR) must be referenced in design and tasks
- **Test Coverage**: All test scenarios must be referenced in tasks via DC field
- **Design Coverage**: All design components must be referenced in tasks
- **Dependencies**: Task dependencies checked for circular references

📖 **Detailed Documentation**:
- [Specification Format Standards](docs/spec-format.md) - Complete format guide for requirements, design, and tasks documents
- [Traceability Management](docs/traceability.md) - Complete guide to dependency tracking and change impact analysis
- [Performance & Benchmarking](docs/performance.md) - Reproducible benchmark system and performance analysis
- [Requirements Validation](docs/validation/ears.md) - EARS format and ID validation
- [Traceability Requirements](docs/validation/traceability.md) - REQ↔DESIGN↔TASK mapping rules
- [Tasks Validation](docs/validation/tasks.md) - DAG requirements and coverage rules
- [CLI Reference](docs/cli.md) - Command usage and troubleshooting


## ⚡ Performance Metrics

Ultra-fast response times with **reproducible benchmarks**:

- **check_completeness**: 0.008ms median (ultra-fast completeness analysis) ⚡️
- **analyze_changes**: 0.018ms median (rapid change impact assessment)  
- **get_traceability**: 0.018ms median (instant traceability matrix generation)
- **prompt_requirements**: 0.003ms median (lightning-fast prompt generation)
- **concurrent_20_tools**: 0.251ms median (excellent concurrency performance)
- **Memory Efficient**: <50MB growth per 1000 operations
- **Reproducible Testing**: `python benchmarks/run_all.py`

📊 [Detailed Performance Analysis](docs/performance.md) | 🧪 [Comprehensive Test Suite](https://github.com/tokusumi/wassden-mcp/actions/workflows/ci.yml)

## 🧪 Development & Testing

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks automatically run `make check` before each commit.

```bash
# Install pre-commit hooks
uv add --dev pre-commit
pre-commit install
```

### Development Commands

```bash
# Install development dependencies
uv sync

# Quality checks (recommended)
make check                # Run format, lint, typecheck, and test with coverage
make ci                   # CI checks without modifying files

# Run CLI commands locally
uv run wassden --help                                     # Show available commands
uv run wassden check-completeness --userInput "test"      # Test CLI functionality (Japanese)
uv run wassden check-completeness --userInput "test" --language en  # Test CLI functionality (English)

# Run MCP server with different transports (development)
uv run wassden start-mcp-server --transport stdio                                       # Start with stdio (default)
uv run wassden start-mcp-server --transport sse --host 127.0.0.1 --port 3001           # Start with SSE
uv run wassden start-mcp-server --transport streamable-http --host 0.0.0.0 --port 3001 # Start with streamable-http

# Or using production method with uvx
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden start-mcp-server --transport stdio

# For detailed CLI options and troubleshooting, see docs/cli.md
```

### Continuous Integration

All pull requests and pushes to main are automatically validated through GitHub Actions CI, which runs:
- Code formatting (ruff format)
- Linting (ruff check)
- Type checking (mypy)
- Full test suite with coverage reporting

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run quality checks (`make check`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

MIT License – see LICENSE file for details.

## 🙏 Acknowledgments

- **Model Context Protocol**: Enabling seamless AI-tool integration
- **FastMCP**: High-performance MCP server framework for Python
- **Claude Code**: Primary development and testing environment
- **Spec-Driven Development**: Methodology inspiration and best practices

---

**Built with ❤️ for the AI-driven development community**