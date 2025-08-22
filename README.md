# wassden 🎯

[![CI](https://github.com/tokusumi/wassden-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/tokusumi/wassden-mcp/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)

**Spec-Driven Development MCP server that transforms any LLM into a systematic development agent**

> 🚀 Generate requirements → design → tasks → code with 100% traceability and validation

## ⚡ Quick Start (MCP)

```bash
# Add to Claude Code
claude mcp add wassden "uvx --from git+https://github.com/tokusumi/wassden-mcp wassden start-mcp-server --transport stdio"

# Test it
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden check-completeness --userInput "Create a TODO app"
```

## 🎯 What It Does

- ✅ **Requirements → Design → Tasks → Code** - Complete SDD workflow with structured prompts
- 🔒 **100% READ-ONLY** - No file modification risk, only analysis and prompt generation
- 🌍 **Auto Language Detection** - Seamless Japanese/English support
- ⚡ **Ultra-fast Performance** - <0.01ms response time with 405+ tests passing
- 📊 **100% Traceability** - Complete REQ↔DESIGN↔TASK mapping enforcement

## 📦 Installation

### Prerequisites
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/) (`pip install uv`)
- MCP-compatible client (Claude Code, Cursor, GitHub Copilot, etc.)

### Claude Code
```bash
claude mcp add wassden "uvx --from git+https://github.com/tokusumi/wassden-mcp wassden start-mcp-server --transport stdio"
```

### Cursor, GitHub Copilot, Other MCP Clients
Edit your MCP settings file:
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

> 📚 For detailed setup and development installation, see [docs/development.md](docs/development.md)

## 🚀 Basic Usage

### 1. Analyze & Generate Requirements

```bash
# Analyze project description and generate requirements prompt
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden check-completeness \
  --userInput "Create a task management API with authentication"
```

### 2. Validate Generated Specs

```bash
# Validate specifications with auto language detection
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-requirements specs/requirements.md
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-design specs/design.md  
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden validate-tasks specs/tasks.md
```

### 3. Get Traceability Matrix

```bash
# Generate complete dependency mapping
uvx --from git+https://github.com/tokusumi/wassden-mcp wassden get-traceability
```

## 🛠️ Core Tools

### Requirements Generation
- **`check-completeness`** - Analyzes input and generates EARS requirements prompt
- **`prompt-requirements`** - Creates specialized requirements generation prompt

### Design & Planning  
- **`prompt-design`** - Generates architectural design prompt from requirements
- **`prompt-tasks`** - Creates WBS task breakdown prompt from design

### Validation Suite
- **`validate-requirements`** - Ensures EARS format and completeness
- **`validate-design`** - Checks architectural consistency
- **`validate-tasks`** - Verifies task dependencies and coverage

### Traceability & Analysis
- **`get-traceability`** - Complete REQ↔DESIGN↔TASK dependency mapping
- **`analyze-changes`** - Impact analysis for specification changes
- **`generate-review-prompt`** - Task-specific implementation review

> 📚 See [full tool documentation](docs/tools.md) for detailed usage and examples

## 📊 Performance

- **Response Time**: <0.01ms average (ultra-fast analysis)
- **Test Coverage**: 405+ tests with 100% passing
- **Memory Efficient**: <50MB growth per 1000 operations
- **Concurrent Support**: Handles 20+ parallel tool calls efficiently

> 🧪 Run benchmarks: `python benchmarks/run_all.py`

## 🎯 Use Cases

- **Development Teams**: Systematic requirements gathering and project planning
- **AI Agents**: Structured prompts for complex development workflows
- **Technical Writers**: Automated documentation validation and traceability
- **Quality Assurance**: Built-in validation with actionable feedback

## 📚 Documentation

- **[Getting Started](docs/quickstart.md)** - Installation and first steps
- **[Tool Reference](docs/tools.md)** - Complete tool documentation
- **[Spec Format Guide](docs/spec-format.md)** - Requirements, design, and tasks format
- **[Validation Rules](docs/validation/)** - EARS format and traceability requirements
- **[Development](docs/development.md)** - Development setup and contributing
- **[Examples](docs/ja/spec-example/)** - Sample specifications (Japanese/English)



## 🤝 Contributing

Contributions are welcome! See [docs/development.md](docs/development.md) for development setup.

```bash
make check  # Run all quality checks before committing
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the AI-driven development community**