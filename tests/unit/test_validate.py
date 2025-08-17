"""Unit tests for validation functions."""

from wassden.lib import validate

# Test constants
EXPECTED_REQUIREMENTS_COUNT = 2
EXPECTED_NFRS_COUNT = 1
EXPECTED_KPIS_COUNT = 1
EXPECTED_SECTIONS_COUNT = 7
EXPECTED_REFERENCED_REQUIREMENTS = 2
EXPECTED_TASKS_COUNT = 3


def test_validate_req_id():
    """Test requirement ID validation."""
    assert validate.validate_req_id("REQ-01") is True
    assert validate.validate_req_id("REQ-99") is True
    assert validate.validate_req_id("REQ-001") is False
    assert validate.validate_req_id("REQ-1") is False
    assert validate.validate_req_id("REQ01") is False
    assert validate.validate_req_id("REQ") is False


def test_validate_task_id():
    """Test task ID validation."""
    assert validate.validate_task_id("TASK-01-01") is True
    assert validate.validate_task_id("TASK-01-01-01") is True
    assert validate.validate_task_id("TASK-99-99") is True
    assert validate.validate_task_id("TASK-01") is False
    assert validate.validate_task_id("TASK-01-01-01-01") is False
    assert validate.validate_task_id("TASK01-01") is False


def test_validate_requirements_structure(sample_requirements):
    """Test requirements structure validation."""
    errors = validate.validate_requirements_structure(sample_requirements)
    assert len(errors) == 0

    # Test missing section
    incomplete = sample_requirements.replace("## 1. 用語集", "")
    errors = validate.validate_requirements_structure(incomplete)
    assert any("用語集" in error for error in errors)

    # Test invalid REQ-ID
    invalid_req = sample_requirements.replace("REQ-01", "REQ-001")
    errors = validate.validate_requirements_structure(invalid_req)
    assert any("REQ-001" in error for error in errors)


def test_validate_design_structure(sample_design):
    """Test design structure validation."""
    errors = validate.validate_design_structure(sample_design)
    assert len(errors) == 0

    # Test missing REQ references
    no_refs = sample_design.replace("REQ-01", "").replace("REQ-02", "")
    errors = validate.validate_design_structure(no_refs)
    assert any("REQ-ID" in error for error in errors)


def test_validate_tasks_structure(sample_tasks):
    """Test tasks structure validation."""
    errors = validate.validate_tasks_structure(sample_tasks)
    assert len(errors) == 0

    # Test duplicate task IDs
    duplicate = sample_tasks + "\n- **TASK-01-01**: Duplicate task"
    errors = validate.validate_tasks_structure(duplicate)
    assert any("Duplicate" in error for error in errors)


def test_validate_requirements(sample_requirements):
    """Test complete requirements validation."""
    result = validate.validate_requirements(sample_requirements)
    assert result["isValid"] is True
    assert result["stats"]["totalRequirements"] == EXPECTED_REQUIREMENTS_COUNT
    assert result["stats"]["totalNFRs"] == EXPECTED_NFRS_COUNT
    assert result["stats"]["totalKPIs"] == EXPECTED_KPIS_COUNT
    assert len(result["foundSections"]) == EXPECTED_SECTIONS_COUNT


def test_validate_design(sample_design, sample_requirements):
    """Test complete design validation."""
    result = validate.validate_design(sample_design, sample_requirements)
    assert result["isValid"] is True
    assert result["stats"]["referencedRequirements"] == EXPECTED_REFERENCED_REQUIREMENTS
    assert len(result["stats"]["missingReferences"]) == 0


def test_validate_tasks(sample_tasks):
    """Test complete tasks validation."""
    result = validate.validate_tasks(sample_tasks)
    assert result["isValid"] is True
    assert result["stats"]["totalTasks"] == EXPECTED_TASKS_COUNT
    assert result["stats"]["dependencies"] >= 0
