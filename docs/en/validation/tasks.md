# Tasks Validation Rules

## Overview

Tasks validation ensures proper WBS (Work Breakdown Structure) format, dependency management, and traceability to design components and requirements.

## Document Structure Requirements

### Required Sections
1. **Overview**: Project approach and WBS explanation
2. **Task List**: Organized by phases with proper formatting
3. **Dependencies**: Visual dependency graph
4. **Milestones**: Phase completion markers
5. **Risks and Mitigation** (Optional): Risk management strategies

### Section Format
```markdown
## 1. Overview
[WBS overview and project approach]

## 2. Task List
### Phase 1: Foundation
- [ ] **TASK-01-01**: Task name
  - **REQ**: [REQ-01, REQ-02]
  - **DC**: **component-name**
  - **Dependencies**: None
  - **Acceptance Criteria**:
    - Criterion 1: [Verifiable condition]
    - Criterion 2: [Verifiable condition]

## 3. Dependencies
```
TASK-01-01 → TASK-01-02 → TASK-02-01
```

## 4. Milestones
- **M1**: Phase 1 completion (TASK-01-XX completed)
```

## Task Format Requirements

### Task ID Format
- Pattern: `**TASK-\d{2}-\d{2}**`
- Examples: `**TASK-01-01**`, `**TASK-02-03**`
- Sequential within phases: 01-01, 01-02, 01-03...
- No gaps in numbering

### Task Status Format
- Pending: `- [ ] **TASK-01-01**: Task name`
- Completed: `- [x] **TASK-01-01**: Task name`
- Clear checkbox format required

### Required Fields
1. **REQ**: Requirement references in brackets
2. **DC**: Design component references (bold format)
3. **Dependencies**: Task dependencies or "None"
4. **Acceptance Criteria**: Verifiable conditions

### Field Format Examples
```markdown
- **REQ**: [REQ-01, REQ-02]           # Multiple requirements
- **REQ**: [TR-01]                    # Test requirement
- **DC**: **auth-service**            # Single component
- **DC**: **auth-service**, **data-layer**  # Multiple components
- **Dependencies**: TASK-01-01        # Single dependency
- **Dependencies**: TASK-01-01, TASK-01-02  # Multiple dependencies
- **Dependencies**: None              # No dependencies
```

## Validation Rules

### Task ID Validation
1. **Unique IDs**: No duplicate TASK-XX-XX
2. **Sequential Numbering**: No gaps in sequence
3. **Proper Format**: Exact pattern match required
4. **Phase Organization**: Tasks grouped by phases

### Requirement Coverage
1. **All Tasks Reference Requirements**: Via REQ field
2. **Valid Requirement IDs**: Must exist in requirements.md
3. **Proper Format**: [REQ-XX] in brackets
4. **Test Requirements**: [TR-XX] format supported

### Design Component Coverage
1. **All Components Covered**: From design.md via DC field
2. **Exact Name Matching**: **component-name** format
3. **Consistent Naming**: Match design.md exactly
4. **Test Scenarios**: **test-scenario** format supported

### Dependency Validation
1. **Valid References**: Dependencies must reference existing tasks
2. **No Circular Dependencies**: DAG (Directed Acyclic Graph) required
3. **Proper Format**: TASK-XX-XX references
4. **Logical Order**: Dependencies respect phase boundaries

### Acceptance Criteria
1. **Verifiable Conditions**: Each criterion must be testable
2. **Clear Language**: Unambiguous success conditions
3. **Measurable Outcomes**: Objective pass/fail criteria
4. **Complete Coverage**: All task aspects covered

## Error Types and Solutions

### Invalid Task ID
```
❌ **TASK-1-1**: Invalid format
→ Use **TASK-01-01**: Proper zero-padding required
```

### Missing Required Field
```
❌ Task missing **REQ** field
→ Add **REQ**: [REQ-XX] with appropriate requirement references
```

### Orphaned Component
```
❌ **auth-service** from design.md not found in any task
→ Add task with **DC**: **auth-service**
```

### Circular Dependency
```
❌ TASK-01-01 → TASK-01-02 → TASK-01-01
→ Restructure dependencies to form valid DAG
```

### Unverifiable Acceptance Criteria
```
❌ "System works well"
→ "System responds within 1 second to authentication requests"
```

## Pattern Matching

### Task IDs
```regex
\bTASK-\d{2}-\d{2}\b
```

### Task Checkboxes
```regex
- \[[x ]\] \*\*TASK-\d{2}-\d{2}\*\*: .+
```

### REQ Field
```regex
\*\*REQ\*\*: \[(REQ|TR|NFR|KPI)-\d{2}(?:,\s*(REQ|TR|NFR|KPI)-\d{2})*\]
```

### DC Field
```regex
\*\*DC\*\*: \*\*[a-zA-Z0-9_-]+\*\*(?:,\s*\*\*[a-zA-Z0-9_-]+\*\*)*
```

### Dependencies Field
```regex
\*\*Dependencies\*\*: (None|TASK-\d{2}-\d{2}(?:,\s*TASK-\d{2}-\d{2})*)
```

## Phase Organization

### Recommended Phases
1. **Foundation**: Core infrastructure and basic components
2. **Implementation**: Main feature development
3. **Integration**: Component integration and testing
4. **Validation**: Testing, quality assurance, deployment

### Phase Numbering
- Phase 1: TASK-01-XX
- Phase 2: TASK-02-XX
- Phase 3: TASK-03-XX
- Phase 4: TASK-04-XX

## Milestone Format

### Required Elements
```markdown
- **M1**: Phase 1 completion (TASK-01-XX completed)
- **M2**: Implementation completion (TASK-02-XX completed)
```

### Validation Rules
- Clear milestone names
- Associated task ranges
- Logical progression
- Completion criteria

## Multi-Language Support

### Section Headers
- Japanese: "## 2. タスク一覧", "## 3. 依存関係"
- English: "## 2. Task List", "## 3. Dependencies"
- Pattern-based detection

### Field Labels
- Japanese: "依存", "受け入れ観点"
- English: "Dependencies", "Acceptance Criteria"
- Consistent terminology

## Validation Commands

### Validate Tasks Document
```bash
uv run wassden validate-tasks --tasksPath specs/tasks.md --designPath specs/design.md --requirementsPath specs/requirements.md
```

### Check Traceability
```bash
uv run wassden get-traceability --specsDir specs/
```

## Best Practices

### Task Definition
- Clear, actionable task names
- Appropriate granularity (not too big/small)
- Logical grouping by phases
- Realistic effort estimates

### Dependency Management
- Minimize dependencies where possible
- Clear dependency rationale
- Avoid tight coupling between phases
- Plan for parallel execution

### Acceptance Criteria
- Specific and measurable
- Test-focused criteria
- Clear pass/fail conditions
- Complete coverage of task scope

### Risk Management
- Identify task-specific risks
- Mitigation strategies for each risk
- Impact assessment on dependencies
- Contingency planning