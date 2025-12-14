# Validation System

## Overview

wassden provides comprehensive validation for specification documents using an AST (Abstract Syntax Tree) based validation system that ensures document quality, completeness, and traceability.

### Key Features

- **Structured Parsing**: Uses mistune v3 to parse markdown into a structured block tree
- **Object-Based Validation**: Validates document structure using typed block objects
- **Cross-Document Traceability**: Automated checking of references between requirements, design, and tasks
- **Test Scenario Coverage**: Validates test scenario coverage from design to tasks
- **Multi-Language Support**: Robust section classification for both Japanese and English

## Architecture

### Block Types

The validation system uses typed block objects to represent document structure:

```python
from wassden.lib.spec_ast.blocks import (
    DocumentBlock,      # Root document
    SectionBlock,       # Document sections (## headings)
    RequirementBlock,   # Requirements (REQ-XX, NFR-XX, etc.)
    TaskBlock,          # Tasks (TASK-XX-XX)
    ListItemBlock,      # Generic list items
)
```

### Section Classification

Sections are automatically classified into normalized types:

```python
from wassden.lib.spec_ast.section_patterns import SectionType

# Requirements sections
SectionType.FUNCTIONAL_REQUIREMENTS      # 機能要求仕様 / Functional Requirements
SectionType.NON_FUNCTIONAL_REQUIREMENTS  # 非機能要求仕様 / Non-Functional Requirements
SectionType.TESTING_REQUIREMENTS         # テスト要求仕様 / Testing Requirements

# Design sections
SectionType.ARCHITECTURE       # アーキテクチャ / Architecture
SectionType.TRACEABILITY       # トレーサビリティ / Traceability

# Tasks sections
SectionType.TASK_LIST          # タスクリスト / Task List
SectionType.DEPENDENCIES       # 依存関係 / Dependencies
```

## Validation Rules

### Requirements Document

- **Structure**: Validates presence of required sections (Overview, Glossary, Scope, etc.)
- **ID Format**: Ensures REQ-XX format (XX: 01-99)
- **Duplicates**: Checks for duplicate requirement IDs
- **EARS**: Validates EARS (Easy Approach to Requirements Syntax) patterns

### Design Document

- **Structure**: Validates required sections (Architecture, Component Design, Data, API, etc.)
- **Traceability**: Ensures traceability section exists and references all requirements
- **Coverage**: Validates that all requirements from requirements.md are covered
- **References**: Checks requirement ID references are valid

### Tasks Document

- **Structure**: Validates required sections (Overview, Task List, Dependencies, Milestones)
- **ID Format**: Ensures TASK-XX-XX format (XX: 01-99)
- **Duplicates**: Checks for duplicate task IDs
- **Dependencies**: Detects circular dependencies
- **Coverage**: Validates all requirements and test scenarios are covered
- **Test Scenarios**: Ensures all test scenarios from design.md are referenced

## Test Scenario Coverage

One of the key features is automated test scenario coverage validation:

### Example

**Design Document** (`design.md`):
```markdown
## テスト設計

テスト戦略:
- **test-input-processing**: 入力処理のテストシナリオ
- **test-output-generation**: 出力生成のテストシナリオ
- **test-error-handling**: エラー処理のテストシナリオ
```

**Tasks Document** (`tasks.md`):
```markdown
## タスクリスト

- [ ] **TASK-01-01**: 入力処理の実装
  - **REQ**: [TR-01]
  - **DC**: **test-input-processing**  ✅ Referenced
  - **依存**: なし

- [ ] **TASK-01-02**: 出力生成の実装
  - **REQ**: [TR-02]
  - **DC**: **test-output-generation**  ✅ Referenced
  - **依存**: TASK-01-01
```

**Validation Error** if test scenario is missing:
```
Test scenario not referenced in tasks: test-error-handling
```

## Usage

### CLI Commands

```bash
# Validate requirements document
uv run wassden validate-requirements specs/requirements.md

# Validate design document (with traceability checking)
uv run wassden validate-design specs/design.md --requirements specs/requirements.md

# Validate tasks document (with full traceability)
uv run wassden validate-tasks specs/tasks.md \
  --requirements specs/requirements.md \
  --design specs/design.md

# Validate with language specification
uv run wassden validate-requirements specs/requirements.md --language en
```

### API

```python
from wassden.lib.validate import (
    validate_requirements,
    validate_design,
    validate_tasks,
)
from wassden.language_types import Language

# Validate requirements
result = validate_requirements(
    requirements_content,
    language=Language.JAPANESE
)

# Validate design with traceability
result = validate_design(
    design_content,
    requirements_content,  # For traceability checking
)

# Validate tasks with full traceability
result = validate_tasks(
    tasks_content,
    requirements_content,
    design_content,  # For test scenario coverage
)
```

### Validation Result Format

```python
{
    "isValid": True,
    "issues": [],  # List of validation error messages
    "stats": {
        # Requirements stats
        "totalRequirements": 10,
        "totalNFRs": 5,
        "totalKPIs": 3,
        "totalTRs": 2,

        # Design stats
        "referencedRequirements": 10,
        "missingReferences": [],

        # Tasks stats
        "totalTasks": 15,
        "dependencies": 8,
        "missingRequirementReferences": [],
    },
    "foundSections": [
        "概要",
        "用語集",
        "スコープ",
        # ... other sections
    ]
}
```

## Performance

The validation system is highly performant:

- **Parse time**: <10ms for typical spec documents
- **Validation time**: <20ms for full document validation
- **Memory usage**: Minimal overhead with efficient AST representation

## Parser API

For advanced use cases, you can use the parser directly:

```python
from wassden.lib.spec_ast.parser import SpecMarkdownParser
from wassden.lib.spec_ast.blocks import BlockType
from wassden.language_types import Language

# Create parser
parser = SpecMarkdownParser(Language.JAPANESE)

# Parse markdown to AST
document = parser.parse(markdown_content)

# Access blocks
sections = document.get_blocks_by_type(BlockType.SECTION)
requirements = document.get_blocks_by_type(BlockType.REQUIREMENT)
tasks = document.get_blocks_by_type(BlockType.TASK)

# Inspect document structure
print(f"Total blocks: {len(document.blocks)}")
print(f"Sections: {len(sections)}")
print(f"Requirements: {len(requirements)}")
```

## Troubleshooting

### Debug Parsing

```python
from wassden.lib.spec_ast.parser import SpecMarkdownParser
from wassden.language_types import Language

parser = SpecMarkdownParser(Language.JAPANESE)
document = parser.parse(content)

# Debug specific block
for block in document.blocks:
    print(f"{block.block_type}: {block.raw_content[:50]}...")
```

### Common Issues

#### Section Recognition

Ensure section headers:
- Use proper markdown format (`## SectionName`)
- Match supported patterns (see `wassden/lib/spec_ast/section_patterns.py`)
- Have no extra whitespace or special characters

#### Test Scenario Coverage

Add DC references in tasks to link test scenarios:

```markdown
- [ ] **TASK-01-01**: 機能実装
  - **REQ**: [REQ-01]
  - **DC**: **test-input-processing**
  - **依存**: なし
```

## Testing

```bash
# Run validation test suite
pytest tests/unit/test_spec_ast/ -v

# Run full test suite
make test

# Test coverage
pytest --cov=wassden tests/
```

### Test Coverage

- **172 unit tests** covering parser, blocks, and validation rules
- **788 total tests** with 91% code coverage
- **100% coverage** of core validation logic

## Contributing

When contributing to validation system:

1. **Add tests**: All new validation rules require comprehensive tests
2. **Update docs**: Document new validation rules and patterns
3. **Performance**: Keep validation fast (<50ms for typical documents)
4. **Multi-language**: Support both Japanese and English patterns

## References

- [mistune v3 documentation](https://mistune.lepture.com/)
- [Section Patterns](../wassden/lib/spec_ast/section_patterns.py)
- [Traceability Guide](./en/traceability.md) / [トレーサビリティガイド](./ja/traceability.md)
- [Spec Format](./en/spec-format.md) / [仕様フォーマット](./ja/spec-format.md)

---

For issues or questions, please check the [GitHub Issues](https://github.com/tokusumi/wassden-mcp/issues).
