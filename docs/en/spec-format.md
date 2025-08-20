# Specification Document Format Standards

This document defines the standard format for specification documents in wassden. All documents must follow these formats for proper traceability and validation.

## 📋 Requirements Document (requirements.md)

### Structure
```markdown
# requirements.md

## 0. Summary
- **Background/Purpose**: [Project background and objectives to achieve]
- **Target Users/Main Scenarios**: [Who will use it and how]

## 1. Glossary
- **Term**: Definition
- **MCP (Model Context Protocol)**: Definition

## 2. Scope
### In Scope
- [What to do]

### Out of Scope
- [What not to do]

## 3. Constraints
- Technical constraints
- Business constraints
- Environmental constraints

## 4. Non-Functional Requirements
- **NFR-01**: Performance requirements
- **NFR-02**: Security requirements
- **NFR-03**: Availability requirements
- **NFR-04**: Maintainability requirements
- **NFR-05**: Other requirements

## 5. KPIs / Acceptance Criteria
- **KPI-01**: Measurable success metric
- **KPI-02**: Measurable success metric

## 6. Functional Requirements
- **REQ-01** - <Requirement Title>: The system shall [action] when [condition]
  - Acceptance criterion 1
  - Acceptance criterion 2
- **REQ-02** - <Requirement Title>: The system shall [action] when [condition]
  - Acceptance criterion 1
  - Acceptance criterion 2

## 7. Testing Requirements
- **TR-01**: Test requirement description
- **TR-02**: Test requirement description
```

### Key Rules
- REQ-ID format: `REQ-\d{2}` (REQ-01 to REQ-99)
- NFR-ID format: `NFR-\d{2}` (NFR-01 to NFR-99)
- KPI-ID format: `KPI-\d{2}` (KPI-01 to KPI-99)
- TR-ID format: `TR-\d{2}` (TR-01 to TR-99)
- EARS format: "The system shall [action] when [condition]"

## 🏗️ Design Document (design.md)

### Structure
```markdown
# design.md

## 1. Architecture
- **Context/Dependencies/Constraints**: [System positioning and limitations]
- **Overall Diagram**: [Component/Data Flow/Sequence overview]
[Requirements: REQ-01, REQ-02, ...]

## 2. Component Design
- **component-a**:
  - **Role**: [Component responsibilities]
  - **Requirements**: [REQ-01, REQ-02]
  - **Input/Output**: [Interface definitions]
  - **Exception/Retry**: [Error handling policy]
  - **Observability**: [Logs, metrics, traces]

- **component-b**:
  - **Role**: [Component responsibilities]
  - **Requirements**: [REQ-03]
  - **Input/Output**: [Interface definitions]
  - **Exception/Retry**: [Error handling policy]
  - **Observability**: [Logs, metrics, traces]

## 3. Data
[Data structures and models]

## 4. API
- **tool_name**:
  - **Overview**: [Function description]
  - **Endpoint**: [URL/Path]
  - **Request/Response**: [Format and examples]
  - **Errors**: [Error codes and handling]
  - **Module Boundaries**: [Responsibility boundaries]

## 5. Non-Functional
- **Performance**: Details [NFR-01]
- **Security**: Details [NFR-02]
- **Availability**: Details [NFR-03]

## 6. Testing
- **Unit/Integration/E2E Role Division**: [Verification content at each level]
- **test-scenario**: [Important test cases]
  - **Test Data Policy**: [Test data preparation method]
  - **Observable Pass/Fail Criteria**: [Success/failure determination criteria]

## 7. Traceability (Required)
- REQ-XX ⇔ **component-name**
- TR-XX ⇔ **test-scenario**

## 8. Flow Design
- **Main Sequence**: [Normal flow processing]
- **State Transition**: [State management and transitions]
- **Backpressure/Queue Processing**: [Load control mechanisms]

## 9. Failure/Edge Cases
- **Fail Patterns**: [Expected failures]
- **Fallback**: [Alternative processing]
- **Timeout/Retry Policy**: [Time limits and retry strategies]

## 10. Security & Compliance
- **Authentication/Authorization**: [Access control methods]
- **Data Protection**: [Encryption, masking]
- **Audit Logs**: [Recording targets and retention periods]
- **Secret Management**: [Secret handling]

## 11. Risks and Mitigation (Optional)
- **Risk**: Description → Mitigation
```

### Key Rules
- Component format: `**component-name**` (bold, kebab-case)
- REQ references: `[REQ-01, REQ-02]` in brackets
- NFR references: `[NFR-01]` in brackets
- Component names must be consistent across documents

## 📝 Tasks Document (tasks.md)

### Structure (WBS Format - Recommended)
```markdown
# tasks.md

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
  - **Steps** (Optional):
    1. Step 1
    2. Step 2

- [ ] **TASK-01-02**: Task name
  - **REQ**: [TR-01]
  - **DC**: **test-scenario**
  - **Dependencies**: TASK-01-01
  - **Acceptance Criteria**:
    - Criterion 1: [Verifiable condition]

### Phase 2: Implementation
- [ ] **TASK-02-01**: Task name
  - **REQ**: [REQ-04]
  - **DC**: **component-a**, **component-b**
  - **Dependencies**: TASK-01-02
  - **Acceptance Criteria**:
    - Criterion 1: [Verifiable condition]

## 3. Dependencies
```
TASK-01-01 → TASK-01-02 → TASK-02-01
```

## 4. Milestones
- **M1**: Phase 1 completion (TASK-01-XX completed)
- **M2**: Phase 2 completion (TASK-02-XX completed)

## 5. Risks and Mitigation
- **Risk**: [Description]
  - Affected Tasks: TASK-XX-XX
  - Mitigation: [Mitigation strategy]
```

### Key Rules
- Task format: `- [ ] **TASK-\d{2}-\d{2}**: Task name`
- Task status: `- [x]` (completed) or `- [ ]` (pending)
- Component references: **DC**: `**component-name**` (must match design.md)
- REQ references: **REQ**: `[REQ-01]` in brackets
- Dependencies: `Dependencies: TASK-XX-XX` or `Dependencies: None`
- Acceptance criteria: `Acceptance Criteria` with verifiable conditions

## 🔗 Traceability Rules

### Requirements → Design
- Every REQ-XX must be referenced in design.md with format: `[REQ-01]`
- Every TR-XX must be referenced in design.md with format: `[TR-01]`
- References must appear near **component-name** or **test-scenario** definitions
- Check Traceability section (Section 7) for complete mapping
- Example: `REQ-01 authentication is handled by **auth-service**`
- Example: `TR-01 is covered by **test-scenario**`

### Design → Tasks  
- Every **component-name** must be referenced in tasks.md
- Every **test-scenario** must be referenced in tasks.md
- References must use exact same formatting via DC field
- Example: `**DC**: **auth-service**` or `**DC**: **test-scenario**`

### Pattern Matching
```python
# Requirements ID
r"\bREQ-\d{2}\b"  # REQ-01 to REQ-99

# Test Requirements ID  
r"\bTR-\d{2}\b"   # TR-01 to TR-99

# Design Components and Test Scenarios
r"\*\*([a-zA-Z0-9_-]+)\*\*"  # **component-name** or **test-scenario**

# Tasks (checkbox format)
r"- \[[x ]\] (\d+(?:\.\d+)*)"  # - [x] 1.0 or - [ ] 1.2.3

# Tasks (WBS format)
r"\bTASK-\d{2}(?:-\d{2}){0,2}\b"  # TASK-01 or TASK-01-01
```

## ✅ Validation Rules

### Requirements Validation
1. All sections (0-7) must be present
2. Summary must include Background/Purpose and Target Users/Main Scenarios
3. REQ-IDs must be unique and sequential with title
4. Each REQ must have acceptance criteria
5. EARS format must be followed for functional requirements
6. NFR/KPI/TR IDs must be unique

### Design Validation
1. All requirements must be referenced in components
2. Component names must use kebab-case format (**component-name**)
3. Each component must specify: Role, Requirements, Input/Output, Exception/Retry, Observability
4. APIs must define: Overview, Endpoint, Request/Response, Errors, Module Boundaries
5. Test strategy must include: Role Division, Main Scenarios, Test Data Policy, Pass/Fail Criteria
6. Traceability section (Section 7) is mandatory
7. Must include Flow Design, Failure/Edge Cases, Security sections

### Tasks Validation
1. Each task must specify: REQ, DC, Dependencies, Acceptance Criteria
2. All components from design must be referenced via DC field
3. Task IDs must follow format: TASK-XX-XX
4. Dependencies must form valid DAG (no circular references)
5. All tasks must reference requirements via REQ field
6. Acceptance criteria must be verifiable
7. Tasks must use checkbox format: `- [ ] **TASK-01-01**: Task name`

### Traceability Validation
1. 100% requirement coverage in design components (REQ-XX → **component-name**)
2. 100% test requirement coverage in design (TR-XX → **test-scenario**)
3. 100% component coverage in tasks (**component-name** → DC field)
4. 100% test scenario coverage in tasks (**test-scenario** → DC field)
5. Valid dependency DAG (no cycles)
6. Consistent naming across documents
7. Traceability section (Section 7) completeness verification

## 🔄 Change Management

When specifications change:
1. Update the changed document
2. Run `analyze-changes` to identify impacts
3. Update affected documents based on analysis
4. Validate all documents
5. Verify traceability completeness

## 📝 Examples

See `/docs/en/spec-example/` for complete examples:
- `requirements.md` - Full requirements example
- `design.md` - Full design example
- `tasks.md` - Full tasks example

These examples demonstrate proper formatting, cross-references, and traceability.