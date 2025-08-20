# design.md

## 1. Architecture

Agent-oriented Spec-Driven Development Support MCP Server

This system operates as a prompt generation engine, supporting Agents in creating high-quality Spec documents incrementally. It does not perform direct file generation but provides appropriate work instruction prompts to Agents at each stage and performs quality verification and feedback on generated files.

[Requirements: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10]

## 2. Component Design

- **prompt-generator**: Agent work instruction prompt generation engine [REQ-02, REQ-04, REQ-06, REQ-08]
- **question-generator**: User question generation engine for information insufficiency [REQ-01]
- **validator**: Deliverable quality verification and feedback generation engine [REQ-03, REQ-05, REQ-07]
- **traceability-manager**: Requirements-design-tasks relationship management [REQ-09, REQ-10]
- **change-analyzer**: Change impact analysis and modification prompt generation [REQ-09]
- **template-manager**: Prompt template management and versioning

## 3. Data

```python
from typing import Optional, Literal, Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PromptRequest:
    type: Literal[
        'requirements',
        'design', 
        'tasks',
        'code',
        'question',
        'validation'
    ]
    context: Dict[str, Optional[str]]
    options: Dict[str, bool]

@dataclass
class PromptResponse:
    type: Literal['instruction', 'question', 'validation_result', 'fix_instruction']
    content: str
    metadata: Dict[str, str]

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    coverage_stats: Dict[str, float]

@dataclass
class TraceabilityMatrix:
    req_to_design: Dict[str, List[str]]
    design_to_tasks: Dict[str, List[str]]
    orphaned_items: List[str]
    coverage_percentage: float
```

## 4. API

- **check_completeness**:
  - **Overview**: Analyze information sufficiency and generate user questions
  - **Endpoint**: MCP tool
  - **Request/Response**: UserInput → Question prompts
  - **Errors**: Invalid input format, analysis failure
  - **Module Boundaries**: Input analysis and question generation

- **prompt_requirements**:
  - **Overview**: Generate EARS format requirements.md creation prompts
  - **Endpoint**: MCP tool
  - **Request/Response**: UserInput → Requirements generation prompts
  - **Errors**: Insufficient information, template generation failure
  - **Module Boundaries**: Prompt generation and template management

- **validate_requirements**:
  - **Overview**: Verify requirements.md structure and content
  - **Endpoint**: MCP tool
  - **Request/Response**: Requirements path → Validation results
  - **Errors**: File not found, parsing errors, validation failures
  - **Module Boundaries**: Document parsing and validation logic

- **get_traceability**:
  - **Overview**: Provide current traceability status in report format
  - **Endpoint**: MCP tool
  - **Request/Response**: Specs directory → Traceability report
  - **Errors**: Directory access issues, parsing failures
  - **Module Boundaries**: Cross-document analysis and reporting

## 5. Non-functional

- **Performance**: Sub-second response times for all operations [NFR-01]
- **Security**: No sensitive data storage, stateless operations [NFR-02]
- **Availability**: Fault-tolerant MCP server operation [NFR-03]
- **Maintainability**: Modular design with clear separation of concerns [NFR-04]
- **Reliability**: Comprehensive error handling and graceful degradation [NFR-05]

## 6. Testing

- **Unit/Integration/E2E Role Division**: 
  - Unit: Individual component validation
  - Integration: MCP tool interaction testing
  - E2E: Complete workflow validation with real Agent interactions
- **prompt-validation-scenario**: Verify generated prompts contain expected instructions and precautions [TR-01]
  - **Test Data Policy**: Use representative user inputs and sample spec documents
  - **Observable Pass/Fail Criteria**: Prompt quality metrics and Agent feedback success rates
- **validation-accuracy-scenario**: Test validation precision for normal/abnormal cases [TR-02]
  - **Test Data Policy**: Curated valid/invalid spec documents
  - **Observable Pass/Fail Criteria**: 95% accuracy with minimal false positives/negatives
- **question-generation-scenario**: Test question generation quality [TR-03]
  - **Test Data Policy**: Incomplete user inputs and scenarios
  - **Observable Pass/Fail Criteria**: Appropriate question generation for missing information
- **traceability-completeness-scenario**: Verify relationship completeness and change impact analysis [TR-04]
  - **Test Data Policy**: Multi-document spec sets with known traceability patterns
  - **Observable Pass/Fail Criteria**: 100% coverage detection and accurate impact identification
- **performance-test-scenario**: Verify response time requirements [TR-05]
  - **Test Data Policy**: Representative document sizes and complexity
  - **Observable Pass/Fail Criteria**: Sub-second response times maintained
- **prompt-limit-scenario**: Test prompt character limits [TR-06]
  - **Test Data Policy**: Large specification documents
  - **Observable Pass/Fail Criteria**: All prompts within 10,000 character limit
- **agent-integration-scenario**: Real Agent interaction testing [TR-07]
  - **Test Data Policy**: Actual Agent workflows and responses
  - **Observable Pass/Fail Criteria**: Successful Agent task completion

## 7. Traceability

- REQ-01 ⇔ **question-generator**
- REQ-02 ⇔ **prompt-generator**
- REQ-03 ⇔ **validator**
- REQ-04 ⇔ **prompt-generator**
- REQ-05 ⇔ **validator**
- REQ-06 ⇔ **prompt-generator**
- REQ-07 ⇔ **validator**
- REQ-08 ⇔ **prompt-generator**
- REQ-09 ⇔ **change-analyzer**, **traceability-manager**
- REQ-10 ⇔ **traceability-manager**
- TR-01 ⇔ **prompt-validation-scenario**
- TR-02 ⇔ **validation-accuracy-scenario**
- TR-03 ⇔ **question-generation-scenario**
- TR-04 ⇔ **traceability-completeness-scenario**
- TR-05 ⇔ **performance-test-scenario**
- TR-06 ⇔ **prompt-limit-scenario**
- TR-07 ⇔ **agent-integration-scenario**

## 8. Flow Design

- **Main Sequence**: Agent request → Context analysis → Prompt generation → Response delivery
- **State Transition**: Stateless operation with context preservation per request
- **Backpressure/Queue Processing**: Async processing with request queuing for high load

## 9. Failure/Edge Cases

- **Fail Patterns**: Invalid file formats, incomplete documents, network failures
- **Fallback**: Graceful error messages with guidance for resolution
- **Timeout/Retry Policy**: 1-second timeout with single retry for file operations

## 10. Security & Compliance

- **Authentication/Authorization**: MCP-level security, no additional auth required
- **Data Protection**: No persistent data storage, in-memory processing only
- **Audit Logs**: Request/response logging for debugging and monitoring
- **Secret Management**: No secrets required, configuration-based operation

## 11. Risks and Mitigation

- **Risk**: Agent prompt quality degradation → Mitigation: Template versioning and validation
- **Risk**: Traceability accuracy issues → Mitigation: Comprehensive test coverage and validation rules
- **Risk**: Performance degradation with large specs → Mitigation: Optimized parsing and caching strategies