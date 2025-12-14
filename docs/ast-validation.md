# AST-Based Validation System

## Overview

wassden includes a new AST (Abstract Syntax Tree) based validation system that provides more accurate and comprehensive validation of specification documents compared to the legacy text-scanning approach.

### Key Features

- **Structured Parsing**: Uses mistune v3 to parse markdown into a structured block tree
- **Object-Based Validation**: Validates document structure using typed block objects
- **Enhanced Traceability**: Improved cross-document reference tracking
- **Test Scenario Coverage**: New validation rule for test scenario coverage from design to tasks
- **Section Pattern Recognition**: Robust multi-language section classification

## Feature Flag: `USE_AST_VALIDATION`

The AST validation system is controlled via an environment variable feature flag:

```bash
# Enable AST validation
export USE_AST_VALIDATION=1

# Disable AST validation (use legacy text-based validation) - current default
export USE_AST_VALIDATION=0
```

**Current Status**: AST validation is available but disabled by default (`USE_AST_VALIDATION=0`). The feature flag must be explicitly enabled to use AST validation.

### When to Enable

**Enable AST validation** for:
- New projects starting from Phase 6
- Projects requiring test scenario coverage validation
- Projects with complex traceability requirements
- Projects needing accurate section structure validation

**Use legacy validation** for:
- Existing projects during migration
- Backward compatibility testing
- When debugging discrepancies between systems

## Architecture

### Block Types

The AST parser creates typed block objects:

```python
from wassden.lib.spec_ast.blocks import (
    DocumentBlock,      # Root document
    SectionBlock,       # Document sections (## headings)
    RequirementBlock,   # Requirements (REQ-XX, NFR-XX, etc.)
    TaskBlock,          # Tasks (TASK-XX-XX)
    ListItemBlock,      # Generic list items
)

# Additional BlockType enum values:
# BlockType.PARAGRAPH  # Paragraph blocks (internal use)
# BlockType.HEADING    # Heading blocks (internal use)
```

Note: `BlockType.PARAGRAPH` and `BlockType.HEADING` exist in the enum but don't have dedicated block classes. They are used internally during parsing for lower-level document structure representation.

### Section Classification

Sections are classified into normalized types:

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

### Validation Rules

Validation rules are organized by document type:

#### Requirements Document Rules
- `RequirementsStructureRule`: Validates required sections
- `RequirementIDFormatRule`: Validates REQ-XX format
- `DuplicateRequirementIDRule`: Checks for duplicate IDs

#### Design Document Rules
- `DesignStructureRule`: Validates required sections
- `TraceabilitySectionRule`: Ensures traceability section exists
- `DesignReferencesRequirementsRule`: Validates requirement references
- `RequirementCoverageRule`: Ensures all requirements are covered

#### Tasks Document Rules
- `TasksStructureRule`: Validates required sections
- `TaskIDFormatRule`: Validates TASK-XX-XX format
- `DuplicateTaskIDRule`: Checks for duplicate task IDs
- `CircularDependencyRule`: Detects circular task dependencies
- `TasksReferenceRequirementsRule`: Validates requirement references
- `TasksReferenceDesignRule`: Validates design component references
- `RequirementCoverageRule`: Ensures all requirements are covered
- `TestScenarioCoverageRule`: **NEW** - Validates test scenario coverage

## New Feature: Test Scenario Coverage

The AST validation system includes a new validation rule for test scenario coverage:

### What It Validates

Ensures that all test scenarios defined in the design document (in format `test-xxx`) are referenced in at least one task.

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

### Implementation Details

- **Pattern Recognition**: Extracts test scenarios using regex `test-[a-z0-9]+(?:-[a-z0-9]+)*`
- **Reference Checking**: Scans TaskBlock content for test scenario references
- **Cross-Document**: Validates design.md against tasks.md

## Rollout Plan

### Phase 5 (Completed)
✅ **Compatibility Layer**
- Create validation compatibility layer
- Add `USE_AST_VALIDATION` feature flag
- Maintain backward compatibility with legacy validation
- All tests passing with feature flag

### Phase 6 (In Progress)
🔄 **AST Validation Adoption**
- **Current Status**: Feature flag available but disabled by default
- **Next Steps**:
  - Enable `USE_AST_VALIDATION=1` in CI environments
  - Update documentation and examples
  - Encourage adoption through migration guide
  - Monitor for issues and gather feedback
- **Goal**: Make AST validation the default choice for new projects

### Phase 7 (Future)
📋 **Legacy Deprecation**
- Deprecate legacy text-based validation
- Remove `USE_AST_VALIDATION` feature flag
- AST validation becomes the only validation system
- Clean up compatibility layer code

## Migration Guide

### For New Projects

New projects should use AST validation from the start:

```bash
# Enable AST validation
export USE_AST_VALIDATION=1

# Generate and validate specs
uv run wassden prompt-requirements --userInput "プロジェクト概要"
uv run wassden validate-requirements specs/requirements.md
```

### For Existing Projects

Existing projects can migrate gradually:

1. **Test with AST validation**:
   ```bash
   export USE_AST_VALIDATION=1
   uv run wassden validate-requirements specs/requirements.md
   ```

2. **Fix any validation errors** (most common):
   - Section name variations (e.g., "サマリー" → "概要")
   - Missing test scenario references in tasks
   - Section structure issues

3. **Run full validation**:
   ```bash
   make validate-examples  # Validates all example specs
   ```

4. **Enable permanently**:
   ```bash
   # Add to .env or CI configuration
   export USE_AST_VALIDATION=1
   ```

### Common Migration Issues

#### Issue 1: Section Name Compatibility
**Note**: Both "サマリー" and "概要" are recognized and map to `SectionType.OVERVIEW` in AST validation. No changes needed for these section names.

If you encounter section recognition issues, verify that:
- Section headers use proper markdown format (`## SectionName`)
- Section names match the supported patterns (see `wassden/lib/spec_ast/section_patterns.py`)
- No extra whitespace or special characters in section headers

#### Issue 2: Test Scenario Coverage
**Problem**: Test scenarios defined in design but not referenced in tasks

**Solution**: Add DC references in tasks:

```diff
- [ ] **TASK-01-01**: 機能実装
  - **REQ**: [REQ-01]
+ - **DC**: **test-input-processing**
  - **依存**: なし
```

#### Issue 3: Non-Functional Section Naming
**Note**: Both "非機能" and "非機能要求仕様" are recognized by AST validation:
- "非機能要求仕様" maps to `SectionType.NON_FUNCTIONAL_REQUIREMENTS` (for requirements documents)
- "非機能" maps to `SectionType.NON_FUNCTIONAL` (for design documents)

Both patterns are supported, so no migration is needed unless you want to standardize naming conventions within your project.

## Testing

### Run AST Validation Tests

```bash
# Run AST validation test suite
pytest tests/unit/test_spec_ast/ -v

# Run compatibility layer tests
pytest tests/unit/test_validate.py -v

# Run with feature flag enabled
USE_AST_VALIDATION=1 pytest tests/unit/test_validate.py -v
```

### Test Coverage

The AST validation system includes:
- **172 unit tests** covering parser, blocks, and validation rules
- **12 compatibility tests** ensuring backward compatibility
- **100% coverage** of core validation logic

## API Reference

### Parser

```python
from wassden.lib.spec_ast.parser import SpecMarkdownParser
from wassden.language_types import Language

# Create parser
parser = SpecMarkdownParser(Language.JAPANESE)

# Parse markdown to AST
document = parser.parse(markdown_content)

# Access blocks
sections = document.get_blocks_by_type(BlockType.SECTION)
requirements = document.get_blocks_by_type(BlockType.REQUIREMENT)
tasks = document.get_blocks_by_type(BlockType.TASK)
```

### Validation

```python
from wassden.lib.spec_ast.validation_compat import (
    validate_requirements_ast,
    validate_design_ast,
    validate_tasks_ast,
)
from wassden.language_types import Language

# Validate requirements
result = validate_requirements_ast(
    requirements_content,
    language=Language.JAPANESE
)

# Validate design with traceability
result = validate_design_ast(
    design_content,
    requirements_content,  # For traceability checking
    language=Language.JAPANESE
)

# Validate tasks with full traceability
result = validate_tasks_ast(
    tasks_content,
    requirements_content,
    design_content,  # For test scenario coverage
    language=Language.JAPANESE
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

AST validation is highly performant:

- **Parse time**: <10ms for typical spec documents
- **Validation time**: <20ms for full document validation
- **Memory usage**: Minimal overhead vs legacy validation

## Troubleshooting

### Debug AST Parsing

```python
from wassden.lib.spec_ast.parser import SpecMarkdownParser

parser = SpecMarkdownParser(Language.JAPANESE)
document = parser.parse(content)

# Inspect document structure
print(f"Total blocks: {len(document.blocks)}")
print(f"Sections: {len(document.get_blocks_by_type(BlockType.SECTION))}")
print(f"Requirements: {len(document.get_blocks_by_type(BlockType.REQUIREMENT))}")

# Debug specific block
for block in document.blocks:
    print(f"{block.block_type}: {block.raw_content[:50]}...")
```

### Enable Debug Logging

```bash
# Enable debug output
export WASSDEN_DEBUG=1
export USE_AST_VALIDATION=1

# Run validation with debug info
uv run wassden validate-requirements specs/requirements.md
```

## Contributing

When contributing to AST validation:

1. **Add tests**: All new validation rules require comprehensive tests
2. **Update docs**: Document new validation rules and patterns
3. **Maintain compatibility**: Ensure backward compatibility during migration
4. **Performance**: Keep validation fast (<50ms for typical documents)

## References

- [mistune v3 documentation](https://mistune.lepture.com/)
- [Validation Rules](./validation/)
- [Section Patterns](../wassden/lib/spec_ast/section_patterns.py)
- [Traceability Guide](./traceability.md)

---

**Note**: This is an active feature under rollout. For issues or questions, please check the [GitHub Issues](https://github.com/tokusumi/wassden-mcp/issues).
