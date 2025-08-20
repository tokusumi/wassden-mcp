# Traceability Validation Rules

## Overview

Traceability validation ensures complete bidirectional relationships between requirements, design components, and tasks throughout the development lifecycle.

## Validation Criteria

### Requirements → Design Coverage
- Every REQ-XX must be referenced in design.md
- References must appear near component definitions
- Format: `[REQ-01, REQ-02]` in brackets
- No orphaned requirements allowed

### Design → Tasks Coverage  
- Every **component-name** must be referenced in tasks.md
- References via DC (Design Component) field
- Format: `**DC**: **component-name**`
- Consistent naming across documents required

### Test Requirements Coverage
- Every TR-XX must map to test scenarios in design.md
- Test scenarios must have corresponding tasks
- Format: `**DC**: **test-scenario**`

## Pattern Matching Rules

### Requirement IDs
```regex
# Functional Requirements
\bREQ-\d{2}\b

# Non-Functional Requirements  
\bNFR-\d{2}\b

# Test Requirements
\bTR-\d{2}\b

# KPI IDs
\bKPI-\d{2}\b
```

### Design Elements
```regex
# Components and Test Scenarios (bold format)
\*\*([a-zA-Z0-9_-]+)\*\*

# Component references in brackets
\[REQ-\d{2}(?:,\s*REQ-\d{2})*\]
```

### Task References
```regex
# Task IDs (WBS format)
\bTASK-\d{2}(?:-\d{2}){0,2}\b

# DC field references
\*\*DC\*\*:\s*\*\*([a-zA-Z0-9_-]+)\*\*
```

## Validation Process

### Step 1: Parse Documents
1. Extract all REQ-XX, NFR-XX, TR-XX from requirements.md
2. Extract all **component-name** and references from design.md
3. Extract all TASK-XX-XX and DC references from tasks.md

### Step 2: Build Traceability Matrix
1. Map requirements to design components
2. Map design components to tasks
3. Identify missing or orphaned elements

### Step 3: Coverage Analysis
1. Calculate coverage percentages
2. Generate detailed reports
3. Provide fix recommendations

## Coverage Requirements

### Minimum Thresholds
- Requirements → Design: 100% (all REQ-XX must be covered)
- Design → Tasks: 100% (all components must have tasks)
- Test Requirements: 100% (all TR-XX must be covered)

### Quality Metrics
- Zero orphaned requirements
- Zero orphaned components
- Valid dependency graph (no cycles)
- Consistent naming conventions

## Error Types and Solutions

### Missing Requirements Coverage
```
❌ REQ-03 not referenced in design.md
→ Add [REQ-03] reference near appropriate component
```

### Missing Component Tasks
```
❌ **auth-service** not referenced in tasks.md
→ Add task with **DC**: **auth-service**
```

### Inconsistent Naming
```
❌ **auth_service** (underscore) vs **auth-service** (hyphen)
→ Use consistent kebab-case format
```

### Circular Dependencies
```
❌ TASK-01-01 → TASK-01-02 → TASK-01-01
→ Restructure dependency chain
```

## Traceability Section Requirements

### In design.md (Section 7)
```markdown
## 7. Traceability
- REQ-01 ⇔ **auth-service**
- REQ-02 ⇔ **data-layer**
- TR-01 ⇔ **auth-test-scenario**
```

### Format Rules
- Use bidirectional arrow: ⇔
- Match exact component names
- Include all requirements and test requirements
- Group by requirement type

## Validation Commands

### Check Complete Traceability
```bash
uv run wassden get-traceability --specsDir specs/
```

### Validate Individual Documents
```bash
uv run wassden validate-design --designPath specs/design.md --requirementsPath specs/requirements.md
```

### Analyze Change Impact
```bash
uv run wassden analyze-changes --changedFile specs/requirements.md --allSpecs specs/
```

## Multi-Language Support

### Section Detection
- Japanese: "## 7. トレーサビリティ"
- English: "## 7. Traceability"
- Pattern-based detection for both languages

### Error Messages
- Localized validation error messages
- Language-specific fix recommendations
- Consistent terminology across languages

## Best Practices

### Requirements Phase
- Use sequential REQ-IDs (REQ-01, REQ-02, ...)
- Avoid gaps in numbering
- Include clear acceptance criteria
- Follow EARS format consistently

### Design Phase
- Use kebab-case for component names
- Reference requirements explicitly
- Include mandatory traceability section
- Define clear component boundaries

### Tasks Phase
- Reference all components via DC field
- Include requirement references via REQ field
- Define verifiable acceptance criteria
- Maintain valid dependency relationships

## Performance Considerations

- Parsing optimizations for large documents
- Efficient pattern matching algorithms
- Incremental validation for changed documents
- Caching strategies for repeated validations