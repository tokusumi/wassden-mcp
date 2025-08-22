# Experiment Framework Documentation

> **⚠️ EXPERIMENTAL FEATURE - EARLY DEVELOPMENT PHASE**
> 
> This feature is highly experimental and in active early development. APIs, commands, and functionality may change significantly without notice. Use at your own risk and expect breaking changes between versions.
>
> **This is strictly a developer-only feature for internal testing and validation purposes.**

## Overview

The Experiment Framework is a **development-mode-only** experimental feature designed for internal validation and benchmarking of the wassden toolkit. It provides testing capabilities to ensure the quality and performance of the validation framework itself.

**⚠️ IMPORTANT LIMITATIONS:**
- **Requires dev dependencies**: Must install with `uv sync` (not available in standard installation)
- **Unstable API**: Interfaces and commands may change without deprecation warnings
- **Early development**: Many features are incomplete or may not work as expected
- **Internal use only**: Not intended for production use or external validation
- **No stability guarantees**: May be removed or completely redesigned in future versions

## Installation

The experiment framework is only available when installed in development mode:

```bash
# Clone the repository
git clone https://github.com/tokusumi/wassden-mcp
cd wassden-mcp

# Install with dev dependencies
uv sync  # This installs all dependencies including dev extras
```

## Architecture

### Core Components

1. **ExperimentManager** (`wassden/lib/experiment_manager.py`)
   - Manages experiment lifecycle and configuration
   - Handles YAML config persistence
   - Tracks active experiments

2. **StatisticsEngine** (`wassden/lib/statistics_engine.py`)
   - Calculates statistical metrics (mean, variance, std deviation)
   - Computes 95% confidence intervals
   - Performs significance testing

3. **Analyzers**
   - **EARSAnalyzer**: Validates EARS pattern compliance (REQ-01)
   - **PerformanceProfiler**: Measures execution time and memory usage (REQ-02)
   - **LanguageDetectorAnalyzer**: Tests language detection accuracy (REQ-03)
   - **ComparativeAnalyzer**: Performs statistical comparisons (REQ-07)

4. **OutputFormatter** (`wassden/lib/output_formatter.py`)
   - Formats results in JSON/CSV (REQ-05)
   - Provides structured output for analysis

## Experiment Design

### Purpose and Goals

The experiment framework is designed to validate and benchmark the wassden toolkit itself through systematic testing. Each experiment type serves a specific validation purpose:

1. **Quality Assurance**: Ensure validation algorithms work correctly
2. **Performance Monitoring**: Track execution speed and resource usage
3. **Regression Detection**: Identify performance degradation or accuracy issues
4. **Comparative Analysis**: Compare different versions or configurations
5. **Continuous Improvement**: Data-driven optimization decisions

### Experiment Scenarios

#### Scenario 1: EARS Compliance Validation
**Goal**: Verify that EARS pattern detection works accurately across different requirement formats

```yaml
experiment_design:
  type: ears
  test_cases:
    - valid_ears_patterns:
        - "WHEN system starts THEN initialize database"
        - "IF user clicks button THEN show dialog"
        - "WHERE temperature > 100 THEN trigger alarm"
    - invalid_patterns:
        - "The system should initialize"
        - "User must be able to login"
    - edge_cases:
        - Mixed language documents
        - Nested conditional statements
        - Complex multi-line requirements
  expected_outcomes:
    - Detection accuracy > 95%
    - No false positives for valid patterns
    - Clear identification of non-compliant patterns
```

#### Scenario 2: Performance Benchmarking
**Goal**: Measure and optimize validation speed for large documents

```yaml
experiment_design:
  type: performance
  test_matrix:
    document_sizes: [1KB, 10KB, 100KB, 1MB]
    operation_types:
      - validate_requirements
      - validate_design
      - get_traceability
    iterations: 100
  performance_targets:
    - Sub-10ms for documents < 100KB
    - Linear scaling with document size
    - Memory usage < 10MB per operation
  stress_tests:
    - Concurrent validation of 10 documents
    - Rapid sequential operations (1000/second)
    - Memory leak detection over 1-hour run
```

#### Scenario 3: Language Detection Accuracy
**Goal**: Ensure correct language detection for multi-language support

```yaml
experiment_design:
  type: language
  test_corpus:
    japanese:
      - Technical specifications
      - User stories
      - Mixed English/Japanese text
    english:
      - Requirements documents
      - Design specifications
      - Code comments
  accuracy_targets:
    - Japanese detection: > 98%
    - English detection: > 98%
    - Mixed content handling: > 90%
  edge_cases:
    - Single word inputs
    - Romanized Japanese
    - Technical jargon
```

#### Scenario 4: Comprehensive Validation Suite
**Goal**: End-to-end validation of entire SDD workflow

```yaml
experiment_design:
  type: comprehensive
  workflow_stages:
    1_requirements:
      - Generate from user input
      - Validate EARS compliance
      - Check completeness
    2_design:
      - Create from requirements
      - Validate traceability
      - Check consistency
    3_tasks:
      - Generate from design
      - Validate dependencies
      - Check coverage
  validation_criteria:
    - 100% requirement coverage
    - No orphaned design elements
    - Complete task traceability
```

### Experiment Planning Template

Use this template to design your experiments:

```markdown
## Experiment: [Name]

### Objective
What are you trying to validate or measure?

### Hypothesis
What do you expect the results to show?

### Variables
- **Independent**: What will you change?
- **Dependent**: What will you measure?
- **Controlled**: What stays constant?

### Method
1. Setup conditions
2. Run experiment
3. Collect data
4. Analyze results

### Success Criteria
- Metric 1: Target value
- Metric 2: Target value

### Risk Mitigation
- Potential issue 1: Mitigation strategy
- Potential issue 2: Mitigation strategy
```

### Best Practices for Experiment Design

1. **Start Small**: Begin with simple experiments before complex scenarios
2. **Control Variables**: Change one variable at a time for clear results
3. **Repeat Tests**: Run multiple iterations for statistical significance
4. **Document Everything**: Record all parameters and environmental factors
5. **Set Clear Targets**: Define success criteria before running experiments
6. **Use Baselines**: Compare against known good configurations
7. **Automate Analysis**: Use comparative tools for objective assessment

## Experiment Types

### 1. EARS Validation (`ears`)
Tests EARS (Easy Approach to Requirements Syntax) pattern compliance in requirements documents.

```bash
uv run wassden experiment run ears --output-format json
```

**Metrics:**
- Pattern matching accuracy
- Requirement identifier extraction
- Compliance percentage

### 2. Performance Benchmarking (`performance`)
Measures execution time and memory usage of validation operations.

```bash
uv run wassden experiment run performance --timeout 600 --memory-limit 104857600
```

**Metrics:**
- Execution time (milliseconds)
- Memory usage (bytes)
- Resource efficiency

### 3. Language Detection (`language`)
Validates accuracy of automatic language detection.

```bash
uv run wassden experiment run language
```

**Metrics:**
- Detection accuracy percentage
- Confidence scores
- False positive/negative rates

### 4. Comprehensive Suite (`comprehensive`)
Runs all validation types in sequence.

```bash
uv run wassden experiment run comprehensive --output-format csv
```

## Configuration Management

### Default Configuration
Each experiment type has default parameters that can be customized:

```yaml
# Example configuration structure
experiment_type: performance
parameters:
  timeout: 600  # seconds
  memory_limit: 104857600  # bytes (100MB)
  iterations: 10
  target_paths:
    - specs/requirements.md
    - specs/design.md
```

### Saving Configurations
```bash
# Save current configuration
uv run wassden experiment save-config performance my-perf-config

# Creates: ~/.wassden/experiments/configs/my-perf-config.yaml
```

### Loading Configurations
```bash
# View saved configuration
uv run wassden experiment load-config my-perf-config

# List all configurations
uv run wassden experiment list-configs
```

### Importing JSON Configurations
```bash
# Import external configuration
uv run wassden experiment import-config external-config.json --name imported-config
```

## Running Experiments

### Basic Execution
```bash
# Run with defaults
uv run wassden experiment run ears

# Run with custom output format
uv run wassden experiment run performance --output-format csv

# Run with resource limits
uv run wassden experiment run language --timeout 300 --memory-limit 52428800
```

### From Configuration
```bash
# Execute saved configuration
uv run wassden experiment run-experiment my-perf-config
```

### Monitoring Active Experiments
```bash
# Show status of running experiments
uv run wassden experiment status
```

## Comparative Analysis

Compare results between experiments to identify improvements or regressions:

```bash
# Compare two experiments
uv run wassden experiment compare exp-001 exp-002

# With specific output format
uv run wassden experiment compare exp-001 exp-002 --output-format json
```

**Statistical Analysis Includes:**
- Mean comparison
- Variance analysis
- Standard deviation
- 95% confidence intervals
- Statistical significance testing (p-value)

## Output Formats

### JSON Format
```json
{
  "experiment_id": "exp-20241225-001",
  "experiment_type": "performance",
  "status": "completed",
  "start_time": "2024-12-25T10:00:00Z",
  "end_time": "2024-12-25T10:05:00Z",
  "results": {
    "execution_time_ms": 45.2,
    "memory_usage_bytes": 1048576
  },
  "statistics": {
    "mean": 45.2,
    "variance": 2.1,
    "std_deviation": 1.45,
    "confidence_interval": [43.75, 46.65]
  }
}
```

### CSV Format
```csv
experiment_id,type,status,metric,value
exp-20241225-001,performance,completed,execution_time_ms,45.2
exp-20241225-001,performance,completed,memory_usage_bytes,1048576
```

## Resource Constraints

The framework enforces strict resource limits per NFR requirements:

- **Timeout**: Maximum 10 minutes (600 seconds) per experiment
- **Memory**: Maximum 100MB (104857600 bytes) usage
- **Concurrency**: Supports parallel experiment execution

## API Usage

For programmatic access:

```python
from wassden.lib.experiment_api import (
    run_experiment,
    measure_ears_coverage,
    measure_performance
)

# Run experiment
result = await run_experiment(
    experiment_type=ExperimentType.PERFORMANCE,
    config_path="./config.yaml",
    output_format=OutputFormat.JSON
)

# Measure specific metrics
ears_coverage = await measure_ears_coverage(
    requirements_path="specs/requirements.md"
)

performance_metrics = await measure_performance(
    operation="validate",
    target_path="specs/design.md"
)
```

## Best Practices

1. **Use Configuration Files**: Store experiment parameters for reproducibility
2. **Set Resource Limits**: Always specify timeout and memory limits
3. **Compare Results**: Use comparative analysis to track improvements
4. **Automate Testing**: Integrate experiments into CI/CD pipelines
5. **Monitor Resources**: Check memory and CPU usage during experiments

## Troubleshooting

### Dev Mode Not Detected
```bash
# Verify dev dependencies are installed
python -c "import pandas, rich, scipy; print('Dev mode available')"

# Reinstall with dev extras
uv sync
```

### Experiment Timeout
- Reduce iteration count in configuration
- Increase timeout limit (max 600 seconds)
- Check for infinite loops in test data

### Memory Limit Exceeded
- Reduce dataset size
- Enable incremental processing
- Check for memory leaks in analyzers

## Known Issues and Limitations

**⚠️ As this is an early experimental feature, expect the following:**

- Performance metrics may be inconsistent across different environments
- Statistical calculations are basic and may not be suitable for rigorous analysis
- Memory profiling is approximate and platform-dependent
- Some experiment types may fail unexpectedly
- Configuration format may change between versions
- Limited error handling and recovery mechanisms
- No backward compatibility guarantees

## Disclaimer

This experimental feature is provided "as-is" for development and testing purposes only. It is not covered by any stability guarantees and should not be used for critical validation or benchmarking tasks. The feature may be removed, redesigned, or significantly changed in any future version without notice.
