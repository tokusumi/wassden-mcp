# Traceability Management

## Overview

Traceability ensures bidirectional relationships between requirements, design, and tasks, enabling impact analysis and change management throughout the development lifecycle.

## Traceability Matrix

### Requirements → Design
Every REQ-XX must be referenced in design.md:
- Requirements are mapped to specific components
- Component responsibilities trace back to requirements
- Test requirements (TR-XX) map to test scenarios

### Design → Tasks
Every component and test scenario must be referenced in tasks.md:
- Components map to implementation tasks
- Test scenarios map to testing tasks
- Design elements have corresponding deliverables

### Complete Traceability Flow
```
REQ-01 → **auth-component** → TASK-01-01
REQ-02 → **data-layer** → TASK-01-02
TR-01 → **auth-test-scenario** → TASK-02-01
```

## Validation Rules

### Requirements Coverage
- 100% REQ-XX coverage in design components
- 100% TR-XX coverage in test scenarios
- No orphaned requirements without design mapping

### Design Coverage
- 100% component coverage in tasks
- 100% test scenario coverage in tasks
- Consistent component naming across documents

### Task Coverage
- All tasks reference requirements via REQ field
- All tasks reference design elements via DC field
- Valid dependency graph (no circular references)

## Pattern Matching

### Requirements IDs
```regex
\bREQ-\d{2}\b     # REQ-01 to REQ-99
\bNFR-\d{2}\b     # NFR-01 to NFR-99
\bKPI-\d{2}\b     # KPI-01 to KPI-99
\bTR-\d{2}\b      # TR-01 to TR-99
```

### Design Elements
```regex
\*\*([a-zA-Z0-9_-]+)\*\*  # **component-name** or **test-scenario**
```

### Task References
```regex
\bTASK-\d{2}(?:-\d{2}){0,2}\b  # TASK-01 or TASK-01-01
```

## Traceability Reports

### Coverage Analysis
```
Requirements Coverage: 95% (19/20)
- REQ-01 → **auth-service** ✓
- REQ-02 → **data-layer** ✓
- REQ-20 → Missing mapping ❌

Design Coverage: 100% (5/5)
- **auth-service** → TASK-01-01 ✓
- **data-layer** → TASK-01-02 ✓

Task Coverage: 90% (18/20)
- TASK-01-01 → REQ-01 ✓
- TASK-03-01 → Missing REQ ❌
```

### Impact Analysis
When requirements change:
1. Identify affected design components
2. Find related tasks and dependencies
3. Generate update recommendations
4. Verify traceability completeness

## Change Management

### Workflow
1. **Change Detection**: Identify modified requirements
2. **Impact Analysis**: Find affected design and tasks
3. **Update Guidance**: Generate modification prompts
4. **Validation**: Verify updated traceability
5. **Report**: Provide completion status

### Example Impact Analysis
```
REQ-01 Modified: "User authentication"
↓
Affected Components:
- **auth-service** (design.md:45)
- **security-layer** (design.md:78)
↓
Affected Tasks:
- TASK-01-01: Implement authentication
- TASK-01-03: Security testing
- TASK-02-01: Integration testing
```

## Best Practices

### Requirements Phase
- Use unique, sequential REQ-IDs
- Follow EARS format consistently
- Include acceptance criteria for each requirement
- Maintain clear requirement boundaries

### Design Phase
- Use kebab-case component names
- Reference requirements explicitly: [REQ-01, REQ-02]
- Include mandatory traceability section
- Map all requirements to components

### Tasks Phase
- Reference design components via DC field
- Include requirement references via REQ field
- Define clear acceptance criteria
- Maintain valid dependency relationships

## Validation Commands

### Check Traceability
```bash
uv run wassden get-traceability --specsDir specs/
```

### Analyze Changes
```bash
uv run wassden analyze-changes --changedFile specs/requirements.md --allSpecs specs/
```

### Validate Individual Documents
```bash
uv run wassden validate-requirements --requirementsPath specs/requirements.md
uv run wassden validate-design --designPath specs/design.md --requirementsPath specs/requirements.md
uv run wassden validate-tasks --tasksPath specs/tasks.md --designPath specs/design.md --requirementsPath specs/requirements.md
```

## Multi-Language Support

Traceability works across languages:
- Japanese: "## トレーサビリティ" section
- English: "## Traceability" section
- Automatic detection of section patterns
- Consistent validation across languages

## Performance

- Real-time traceability validation (< 1 second)
- Efficient pattern matching algorithms
- Optimized for large specification documents
- Batch processing for multi-document analysis