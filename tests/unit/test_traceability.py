"""Unit tests for traceability functions."""

from wassden.lib import traceability
from wassden.lib.validation_common import check_tr_coverage, extract_test_scenarios, extract_tr_ids

# Test constants
MAX_COVERAGE_PERCENTAGE = 100


def test_extract_req_ids():
    """Test REQ-ID extraction."""
    content = "This is REQ-01 and REQ-02 but not REQ-001"
    ids = traceability.extract_req_ids(content)
    assert ids == {"REQ-01", "REQ-02"}

    # Test empty content
    assert traceability.extract_req_ids("") == set()
    assert traceability.extract_req_ids(None) == set()


def test_extract_task_ids():
    """Test TASK-ID extraction."""
    content = "Tasks: TASK-01-01, TASK-02-01-01, and TASK-03-02"
    ids = traceability.extract_task_ids(content)
    assert ids == {"TASK-01-01", "TASK-02-01-01", "TASK-03-02"}

    # Test empty content
    assert traceability.extract_task_ids("") == set()
    assert traceability.extract_task_ids(None) == set()


def test_extract_design_components():
    """Test design component extraction."""
    content = """
    ## Components
    - **input-handler**: Handles input
    - **output-processor**: Processes output
    ### data-store
    """
    components = traceability.extract_design_components(content)
    assert "input-handler" in components
    assert "output-processor" in components
    assert "data-store" in components


def test_extract_test_scenarios():
    """Test test scenario extraction."""
    content = """
    ## 6. テスト戦略
    - **単体/結合/E2E の役割分担**: 各レベルでの検証内容
    - **test-input-processing**: 入力処理の重要なテストケース
      - **テストデータ方針**: 正常系・異常系のテストデータ準備
      - **観測可能な合否基準**: 入力が正しく処理され出力される
    - **test-output-generation**: 出力処理のテストケース
      - **テストデータ方針**: 様々なデータパターンでのテスト

    ## 7. トレーサビリティ
    Other content
    """

    scenarios = extract_test_scenarios(content)
    assert "test-input-processing" in scenarios
    assert "test-output-generation" in scenarios

    # Test empty content
    assert extract_test_scenarios("") == set()

    # Test content without test strategy section
    no_test_content = "## 1. Architecture\nSome content"
    assert extract_test_scenarios(no_test_content) == set()


def test_extract_tr_ids():
    """Test TR-ID extraction."""
    content = "This has TR-01 and TR-02 but not TR-001"
    ids = extract_tr_ids(content)
    assert ids == {"TR-01", "TR-02"}

    # Test empty content
    assert extract_tr_ids("") == set()


def test_check_tr_coverage():
    """Test TR coverage checking."""
    all_trs = {"TR-01", "TR-02", "TR-03"}
    referenced_trs = {"TR-01", "TR-02"}

    errors = check_tr_coverage(all_trs, referenced_trs)
    assert len(errors) == 1
    assert "Missing references to test requirements: TR-03" in errors[0]

    # Test complete coverage
    complete_errors = check_tr_coverage(all_trs, all_trs)
    assert len(complete_errors) == 0


def test_build_traceability_matrix(sample_requirements, sample_design, sample_tasks):
    """Test traceability matrix building."""
    matrix = traceability.build_traceability_matrix(sample_requirements, sample_design, sample_tasks)

    assert "REQ-01" in matrix["requirements"]
    assert "REQ-02" in matrix["requirements"]
    assert "TR-01" in matrix["test_requirements"]
    assert "TR-02" in matrix["test_requirements"]
    assert "input-handler" in matrix["design_components"]
    assert "output-handler" in matrix["design_components"]
    assert "test-input-processing" in matrix["test_scenarios"]
    assert "test-output-generation" in matrix["test_scenarios"]
    assert "TASK-01-01" in matrix["tasks"]
    assert "TASK-01-02" in matrix["tasks"]
    assert "TASK-02-01" in matrix["tasks"]

    # Check mappings
    assert len(matrix["req_to_design"]) > 0
    assert len(matrix["tr_to_design"]) > 0
    # Task dependencies might be empty if not explicitly defined with colon
    assert "task_dependencies" in matrix


def test_check_circular_dependencies():
    """Test circular dependency detection."""
    # No circular dependencies
    deps = {
        "TASK-01": {"TASK-02"},
        "TASK-02": {"TASK-03"},
        "TASK-03": set(),
    }
    errors = traceability.check_circular_dependencies(deps)
    assert len(errors) == 0

    # With circular dependency
    deps_circular = {
        "TASK-01": {"TASK-02"},
        "TASK-02": {"TASK-03"},
        "TASK-03": {"TASK-01"},
    }
    errors = traceability.check_circular_dependencies(deps_circular)
    assert len(errors) > 0


def test_calculate_coverage_metrics(sample_requirements, sample_design, sample_tasks):
    """Test coverage metrics calculation."""
    matrix = traceability.build_traceability_matrix(sample_requirements, sample_design, sample_tasks)
    metrics = traceability.calculate_coverage_metrics(matrix)

    assert "requirement_coverage" in metrics
    assert "test_requirement_coverage" in metrics
    assert "design_coverage" in metrics
    assert "test_scenario_coverage" in metrics
    assert "task_coverage" in metrics
    assert all(0 <= v <= MAX_COVERAGE_PERCENTAGE for v in metrics.values())
