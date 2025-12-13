"""Unit tests for ID extractor."""

from wassden.lib.spec_ast.id_extractor import IDExtractor


class TestExtractReqIdFromText:
    """Tests for extracting requirement IDs from text."""

    def test_extract_req_id_strict_pattern(self) -> None:
        """Test extracting REQ-ID with strict pattern."""
        req_id, req_text, req_type = IDExtractor.extract_req_id_from_text("REQ-01: System shall validate input")
        assert req_id == "REQ-01"
        assert req_text == "System shall validate input"
        assert req_type == "REQ"

    def test_extract_nfr_id(self) -> None:
        """Test extracting NFR-ID."""
        req_id, req_text, req_type = IDExtractor.extract_req_id_from_text("NFR-02: Response time shall be < 100ms")
        assert req_id == "NFR-02"
        assert req_text == "Response time shall be < 100ms"
        assert req_type == "NFR"

    def test_extract_kpi_id(self) -> None:
        """Test extracting KPI-ID."""
        req_id, req_text, req_type = IDExtractor.extract_req_id_from_text("KPI-03: 95% user satisfaction")
        assert req_id == "KPI-03"
        assert req_text == "95% user satisfaction"
        assert req_type == "KPI"

    def test_extract_tr_id(self) -> None:
        """Test extracting TR-ID."""
        req_id, req_text, req_type = IDExtractor.extract_req_id_from_text("TR-04: Verify login flow")
        assert req_id == "TR-04"
        assert req_text == "Verify login flow"
        assert req_type == "TR"

    def test_extract_no_id(self) -> None:
        """Test extracting when no ID present."""
        req_id, req_text, req_type = IDExtractor.extract_req_id_from_text("Just some text without ID")
        assert req_id is None
        assert req_text == "Just some text without ID"
        assert req_type == "REQ"

    def test_extract_malformed_id(self) -> None:
        """Test extracting malformed ID (loose pattern)."""
        req_id, req_text, req_type = IDExtractor.extract_req_id_from_text("REQ-ABC: Malformed ID")
        assert req_id == "REQ-ABC"
        assert req_text == "Malformed ID"
        assert req_type == "REQ"


class TestExtractTaskIdFromText:
    """Tests for extracting task IDs from text."""

    def test_extract_task_id_two_levels(self) -> None:
        """Test extracting TASK-ID with two levels."""
        task_id, task_text = IDExtractor.extract_task_id_from_text("TASK-01-01: Implement login feature")
        assert task_id == "TASK-01-01"
        assert task_text == "Implement login feature"

    def test_extract_task_id_three_levels(self) -> None:
        """Test extracting TASK-ID with three levels."""
        task_id, task_text = IDExtractor.extract_task_id_from_text("TASK-02-03-05: Write unit tests")
        assert task_id == "TASK-02-03-05"
        assert task_text == "Write unit tests"

    def test_extract_no_task_id(self) -> None:
        """Test extracting when no task ID present."""
        task_id, task_text = IDExtractor.extract_task_id_from_text("Just task description")
        assert task_id is None
        assert task_text == "Just task description"

    def test_extract_malformed_task_id(self) -> None:
        """Test extracting malformed task ID."""
        task_id, task_text = IDExtractor.extract_task_id_from_text("TASK-XX: Invalid task")
        assert task_id == "TASK-XX"
        assert task_text == "Invalid task"


class TestExtractAllIds:
    """Tests for extracting all IDs from text."""

    def test_extract_all_req_ids(self) -> None:
        """Test extracting all requirement IDs."""
        text = "This implements REQ-01 and REQ-02, also covers NFR-03 and KPI-04"
        ids = IDExtractor.extract_all_req_ids(text)
        assert ids == {"REQ-01", "REQ-02", "NFR-03", "KPI-04"}

    def test_extract_all_task_ids(self) -> None:
        """Test extracting all task IDs."""
        text = "Depends on TASK-01-01 and TASK-02-03, also TASK-01-02-03"
        ids = IDExtractor.extract_all_task_ids(text)
        assert ids == {"TASK-01-01", "TASK-02-03", "TASK-01-02-03"}

    def test_extract_all_dc_refs(self) -> None:
        """Test extracting design component references."""
        text = "Uses DC-01 for authentication and DC-03 for database"
        refs = IDExtractor.extract_all_dc_refs(text)
        assert refs == {"DC-01", "DC-03"}

    def test_extract_from_empty_text(self) -> None:
        """Test extracting from empty text."""
        assert len(IDExtractor.extract_all_req_ids("")) == 0
        assert len(IDExtractor.extract_all_task_ids("")) == 0
        assert len(IDExtractor.extract_all_dc_refs("")) == 0


class TestExtractTaskDependencies:
    """Tests for extracting task dependencies."""

    def test_extract_depends_on_pattern(self) -> None:
        """Test extracting 'depends on' pattern."""
        text = "This task depends on TASK-01-01"
        deps = IDExtractor.extract_task_dependencies(text)
        assert deps == ["TASK-01-01"]

    def test_extract_requires_pattern(self) -> None:
        """Test extracting 'requires' pattern."""
        text = "Requires TASK-02-03 to be completed first"
        deps = IDExtractor.extract_task_dependencies(text)
        assert deps == ["TASK-02-03"]

    def test_extract_after_pattern(self) -> None:
        """Test extracting 'after' pattern."""
        text = "Execute after TASK-01-02"
        deps = IDExtractor.extract_task_dependencies(text)
        assert deps == ["TASK-01-02"]

    def test_extract_japanese_dependency(self) -> None:
        """Test extracting Japanese dependency pattern."""
        text = "依存: TASK-03-01"
        deps = IDExtractor.extract_task_dependencies(text)
        assert deps == ["TASK-03-01"]

    def test_extract_multiple_dependencies(self) -> None:
        """Test extracting multiple dependencies."""
        text = "Depends on TASK-01-01 and requires TASK-02-03"
        deps = IDExtractor.extract_task_dependencies(text)
        assert "TASK-01-01" in deps
        assert "TASK-02-03" in deps

    def test_extract_no_dependencies(self) -> None:
        """Test when no dependencies present."""
        text = "Task with no dependencies"
        deps = IDExtractor.extract_task_dependencies(text)
        assert len(deps) == 0


class TestIsAcceptanceCriteria:
    """Tests for acceptance criteria detection."""

    def test_japanese_acceptance_criteria(self) -> None:
        """Test detecting Japanese acceptance criteria."""
        assert IDExtractor.is_acceptance_criteria("受け入れ観点: テストケース") is True
        assert IDExtractor.is_acceptance_criteria("受入観点を確認") is True

    def test_english_acceptance_criteria(self) -> None:
        """Test detecting English acceptance criteria."""
        assert IDExtractor.is_acceptance_criteria("Acceptance criteria: user can login") is True

    def test_japanese_test_criteria(self) -> None:
        """Test detecting Japanese test criteria."""
        assert IDExtractor.is_acceptance_criteria("テスト観点: 正常系") is True

    def test_english_test_criteria(self) -> None:
        """Test detecting English test criteria."""
        assert IDExtractor.is_acceptance_criteria("Test criteria for validation") is True

    def test_not_acceptance_criteria(self) -> None:
        """Test text that is not acceptance criteria."""
        assert IDExtractor.is_acceptance_criteria("REQ-01: Normal requirement") is False
        assert IDExtractor.is_acceptance_criteria("システムは入力を検証すること") is False
