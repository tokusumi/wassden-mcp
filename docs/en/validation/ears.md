# Requirements Description Format and Validation

## Overview

Defines requirement description format and validation criteria for the wassden project.

## Requirements Description Format

In wassden, functional requirements are described in "The system shall..." format:

```
The system shall <action>
```

## OK Examples

```
The system shall provide user authentication functionality
The system shall return JSON format responses to API requests
The system shall display progress during file uploads
```

## NG Examples

```
❌ The system shall operate at high speed (missing "shall")
❌ User satisfaction features (subject is not "The system")
❌ Execute processing as needed (unclear action)
```

## ID Format

### Functional Requirements ID
- Format: `REQ-XX` (XX is 01-99)
- Examples: `REQ-01`, `REQ-02`, `REQ-15`
- 00 is invalid

### Non-Functional Requirements ID  
- Format: `NFR-XX` (XX is 01-99)
- Examples: `NFR-01`, `NFR-02`

### KPI ID
- Format: `KPI-XX` (XX is 01-99)  
- Examples: `KPI-01`, `KPI-02`

## Validation Criteria

1. **ID Format Check**: Must conform to regex `^REQ-\d{2}$`
2. **ID Duplication Check**: Prohibit duplicate ID usage
3. **Required Sections**: Summary, Glossary, Scope, Constraints, Non-Functional Requirements, KPI, Functional Requirements
4. **Document Structure**: Markdown format with section headers (## Section Name)
5. **100% Traceability**: All requirements must be referenced in design.md and tasks.md

## Regex Patterns

```regex
# Functional Requirements ID
^REQ-\d{2}$

# Non-Functional Requirements ID  
^NFR-\d{2}$

# KPI ID
^KPI-\d{2}$

# Section Headers
^## \d*\.?\s*Section Name
```