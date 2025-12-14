# Complete AST Validation Migration

This PR completes the migration from legacy validation to AST-based validation system, removing all legacy code and establishing a loosely coupled architecture.

## Overview

This is a major refactoring that:
- ✅ Removes 1,417 lines of legacy code
- ✅ Completes migration to AST-based validation
- ✅ Simplifies codebase with single validation path
- ✅ Improves maintainability with loosely coupled architecture
- ✅ All 788 tests passing with 91% coverage

## Changes

### 1. Complete AST Validation Migration (Commit 1: bd73b96)

**Breaking Changes:**
- Removed `USE_AST_VALIDATION` feature flag - AST validation is now the default
- All validation functions (`validate_requirements`, `validate_design`, `validate_tasks`) now use AST validation exclusively

**New Features:**
- Implemented i18n support in structure validation rules
- Section display names now localized based on Language parameter
- Legacy validation functions preserved as `validate_*_legacy()` for backward compatibility

**Technical Details:**
- Removed `os` module dependency from `validate.py`
- Refactored `_get_section_display_name` to use section patterns with i18n
- Updated tests to explicitly specify language for consistent assertions
- 172 AST validation tests passing
- 184 total validation-related tests passing

### 2. Remove All Legacy Validation Functions (Commit 2: e83524f)

**Deleted Functions:**
- `validate_requirements_structure` and all helpers
- `validate_design_structure` and all helpers
- `validate_tasks_structure` and all helpers
- `validate_requirements_legacy`
- `validate_design_legacy`
- `validate_tasks_legacy`
- `validate_spec_structure`
- All internal helper functions (_check_required_sections, _validate_requirement_ids, etc.)

**Preserved Functions:**
- `validate_req_id` - Public API for ID format validation
- `validate_task_id` - Public API for ID format validation
- `validate_requirements` - Now uses AST validation exclusively
- `validate_design` - Now uses AST validation exclusively
- `validate_tasks` - Now uses AST validation exclusively

**Test Cleanup:**
- Removed 819 lines of legacy validation tests
- Deleted `test_validate_comprehensive.py` (387 lines)
- Deleted `test_validate_detailed.py` (432 lines)
- Removed legacy structure tests from `test_validate.py`

**Results:**
- 1,417 lines of code deleted
- 652 tests passing with AST validation
- Simplified codebase with single validation path

### 3. Chore: Add Coverage Temp Files to .gitignore (Commit 3: 5eb56ef)

- Added `.coverage.*` pattern to `.gitignore` to exclude pytest coverage temporary files

## Test Results

### Before Migration
- Multiple validation paths (legacy + AST)
- Complex test suite with duplicate coverage
- Higher maintenance burden

### After Migration
- **788 tests passing** ✅
- **91% code coverage** ✅
- **172 comprehensive AST validation tests**
- Single, clean validation path
- Improved maintainability

## Migration Path

```
Legacy Validation (with feature flag)
  ↓
AST Validation (default, legacy preserved)
  ↓
AST Validation (legacy removed) ← This PR
```

## Architecture Improvements

### Loosely Coupled Design
- **Parser** (`SpecMarkdownParser`) - Independent markdown parsing
- **Validation Engine** - Orchestrates validation rules
- **Validation Rules** - Modular, testable rules
- **Compatibility Layer** - Maintains existing API

### Benefits
1. **Maintainability**: Single validation implementation
2. **Testability**: 172 focused AST tests
3. **Extensibility**: Easy to add new validation rules
4. **Clarity**: Clear separation of concerns
5. **I18n Support**: Built-in multi-language support

## Breaking Changes

⚠️ **These functions have been removed:**
- `validate_requirements_structure()`
- `validate_design_structure()`
- `validate_tasks_structure()`
- `validate_spec_structure()`
- `validate_*_legacy()` functions

**Migration Guide:**
```python
# Before
from wassden.lib.validate import validate_requirements_structure
errors = validate_requirements_structure(content)

# After (use main validation functions)
from wassden.lib.validate import validate_requirements
result = validate_requirements(content)
errors = result["issues"]
```

## Verification

All checks passing:
- ✅ Format: `ruff format --check` (102 files)
- ✅ Lint: `ruff check` (all checks passed)
- ✅ Type: `mypy wassden` (53 files, no issues)
- ✅ Tests: `pytest --cov=wassden` (788 passed, 91% coverage)
- ✅ Pre-commit hooks: All hooks passing

## Related Issues

Closes the migration from tightly coupled validation to loosely coupled AST-based system.
