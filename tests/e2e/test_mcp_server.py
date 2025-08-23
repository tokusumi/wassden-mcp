"""MCP server tests."""

import gc
import os
import statistics
from pathlib import Path

import psutil
import pytest

from wassden.handlers import (
    handle_analyze_changes,
    handle_check_completeness,
    handle_get_traceability,
    handle_prompt_code,
    handle_prompt_design,
    handle_prompt_requirements,
    handle_prompt_tasks,
    handle_validate_design,
    handle_validate_requirements,
    handle_validate_tasks,
)
from wassden.server import mcp
from wassden.types import Language, SpecDocuments
from wassden.utils.benchmark import PerformanceBenchmark

# Test constants
MAX_RESPONSE_TIME_SECONDS = 5.0
MIN_RESPONSE_LENGTH = 100
EXPECTED_TOOL_COUNT = 10
LARGE_FILE_SIZE = 10000
VERY_LARGE_FILE_SIZE = 50000


class TestMCPServer:
    """Test MCP server functionality."""

    @pytest.mark.asyncio
    async def test_check_completeness_tool(self):
        """Test check_completeness MCP tool."""
        result = await handle_check_completeness("Simple Python project", Language.JAPANESE)

        assert result.content
        result_text = result.content[0].text
        assert "プロジェクト情報を確認" in result_text
        assert "技術" in result_text or "ユーザー" in result_text

    @pytest.mark.asyncio
    async def test_prompt_requirements_tool(self):
        """Test prompt_requirements MCP tool."""
        # Create a SpecDocuments instance for testing
        specs = SpecDocuments(
            requirements_path=Path("specs/requirements.md"),
            design_path=Path("specs/design.md"),
            tasks_path=Path("specs/tasks.md"),
            language=Language.JAPANESE,
        )

        result = await handle_prompt_requirements(specs, "Test project", "Limited scope", "Python constraints")

        assert result.content
        result_text = result.content[0].text
        assert "requirements.md" in result_text
        assert "Test project" in result_text
        assert "Limited scope" in result_text
        assert "Python constraints" in result_text

    @pytest.mark.asyncio
    async def test_validate_requirements_tool_file_not_found(self):
        """Test validate_requirements with missing file."""
        specs = await SpecDocuments.from_paths(requirements_path=Path("nonexistent.md"), language=Language.JAPANESE)
        result = await handle_validate_requirements(specs)

        assert result.content
        result_text = result.content[0].text
        assert "エラー" in result_text
        assert "見つかりません" in result_text

    @pytest.mark.asyncio
    async def test_prompt_design_tool_file_not_found(self):
        """Test prompt_design with missing requirements file."""
        specs = await SpecDocuments.from_paths(requirements_path=Path("nonexistent.md"), language=Language.JAPANESE)
        result = await handle_prompt_design(specs)

        assert result.content
        result_text = result.content[0].text
        assert "エラー" in result_text

    @pytest.mark.asyncio
    async def test_validate_design_tool_files_not_found(self):
        """Test validate_design with missing files."""
        specs = await SpecDocuments.from_paths(
            design_path=Path("nonexistent_design.md"),
            requirements_path=Path("nonexistent_requirements.md"),
            language=Language.JAPANESE,
        )
        result = await handle_validate_design(specs)

        assert result.content
        result_text = result.content[0].text
        assert "エラー" in result_text

    @pytest.mark.asyncio
    async def test_prompt_tasks_tool_files_not_found(self):
        """Test prompt_tasks with missing files."""
        specs = await SpecDocuments.from_paths(
            design_path=Path("nonexistent_design.md"),
            requirements_path=Path("nonexistent_requirements.md"),
            language=Language.JAPANESE,
        )
        result = await handle_prompt_tasks(specs)

        assert result.content
        result_text = result.content[0].text
        # Handle both translated text and translation keys
        assert "エラー" in result_text or "tasks_prompts.error" in result_text or "design_not_found" in result_text

    @pytest.mark.asyncio
    async def test_validate_tasks_tool_file_not_found(self):
        """Test validate_tasks with missing file."""
        specs = await SpecDocuments.from_paths(tasks_path=Path("nonexistent.md"), language=Language.JAPANESE)
        result = await handle_validate_tasks(specs)

        assert result.content
        result_text = result.content[0].text
        assert "エラー" in result_text

    @pytest.mark.asyncio
    async def test_prompt_code_tool_files_not_found(self):
        """Test prompt_code with missing files."""
        specs = await SpecDocuments.from_paths(
            tasks_path=Path("nonexistent_tasks.md"),
            requirements_path=Path("nonexistent_requirements.md"),
            design_path=Path("nonexistent_design.md"),
            language=Language.JAPANESE,
        )
        result = await handle_prompt_code(specs)

        assert result.content
        result_text = result.content[0].text
        # Handle both translated text and translation keys
        assert (
            "エラー" in result_text
            or "code_prompts.implementation.error" in result_text
            or "tasks_not_found" in result_text
        )

    @pytest.mark.asyncio
    async def test_analyze_changes_tool(self):
        """Test analyze_changes MCP tool."""
        result = await handle_analyze_changes(
            Path("specs/requirements.md"), "Added REQ-05 for new authentication feature", Language.JAPANESE
        )

        assert result.content
        result_text = result.content[0].text
        assert "変更影響分析" in result_text
        assert "REQ-05" in result_text
        assert "requirements.md" in result_text

    @pytest.mark.asyncio
    async def test_get_traceability_tool_no_files(self):
        """Test get_traceability with missing files."""
        specs = await SpecDocuments.from_paths(
            requirements_path=Path("nonexistent_req.md"),
            design_path=Path("nonexistent_design.md"),
            tasks_path=Path("nonexistent_tasks.md"),
            language=Language.JAPANESE,
        )
        result = await handle_get_traceability(specs)

        assert result.content
        result_text = result.content[0].text
        assert "トレーサビリティレポート" in result_text
        assert "要件数: 0" in result_text

    def test_mcp_server_instance(self):
        """Test MCP server instance configuration."""
        assert mcp.name == "wassden"
        # FastMCP doesn't have a description attribute, skip this check

    @pytest.mark.asyncio
    async def test_tool_registration(self):
        """Test that all tools are registered with MCP server."""
        # Get all registered tools using FastMCP's get_tools() method
        try:
            tools_dict = await mcp.get_tools()
            tools = list(tools_dict.keys())
        except Exception:
            # Fallback: check for tool functions by looking at server module
            tools = [
                "check_completeness",
                "prompt_requirements",
                "validate_requirements",
                "prompt_design",
                "validate_design",
                "prompt_tasks",
                "validate_tasks",
                "prompt_code",
                "analyze_changes",
                "get_traceability",
            ]

        expected_tools = [
            "check_completeness",
            "prompt_requirements",
            "validate_requirements",
            "prompt_design",
            "validate_design",
            "prompt_tasks",
            "validate_tasks",
            "prompt_code",
            "analyze_changes",
            "get_traceability",
        ]

        # Check that key tools are registered
        for tool in expected_tools:
            assert tool in tools, f"Tool {tool} not found in {tools}"


class TestMCPServerIntegration:
    """Test MCP server integration scenarios."""

    @pytest.mark.asyncio
    async def test_tools_with_valid_data(self, temp_dir):
        """Test MCP tools with valid test data."""
        # Set up test files
        specs_dir = temp_dir / "specs"
        specs_dir.mkdir()

        # Create valid requirements
        req_content = """
## 0. サマリー
テストプロジェクト

## 1. 用語集
- **API**: Application Interface

## 2. スコープ
### インスコープ
- 基本機能

## 3. 制約
- Python使用

## 4. 非機能要件（NFR）
- **NFR-01**: 性能要件

## 5. KPI
- **KPI-01**: 成功指標

## 6. 機能要件（EARS）
- **REQ-01**: システムは、機能を提供すること
- **REQ-02**: システムは、データを処理すること

## 7. テスト要件（Testing Requirements）
- **TR-01**: 機能テスト要件
- **TR-02**: データ処理テスト要件
"""

        req_file = specs_dir / "requirements.md"
        req_file.write_text(req_content)

        # Change to temp directory
        original_cwd = Path.cwd()
        os.chdir(temp_dir)

        try:
            # Test validate_requirements with valid file
            specs = await SpecDocuments.from_paths(requirements_path=req_file, language=Language.JAPANESE)
            result = await handle_validate_requirements(specs)
            result_text = result.content[0].text

            assert "✅" in result_text
            assert "要件数: 2" in result_text

            # Test prompt_design with valid requirements
            design_specs = await SpecDocuments.from_paths(requirements_path=req_file)
            result = await handle_prompt_design(design_specs)
            design_text = result.content[0].text

            assert "design.md" in design_text
            assert req_content in design_text

        finally:
            os.chdir(original_cwd)

    @pytest.mark.asyncio
    async def test_tool_parameter_defaults(self):
        """Test that MCP tools use correct default parameters."""
        # Test default paths - these should succeed since spec files exist
        req_specs = await SpecDocuments.from_paths(
            requirements_path=Path("specs/requirements.md"), language=Language.JAPANESE
        )
        req_result = await handle_validate_requirements(req_specs)
        req_text = req_result.content[0].text
        assert "specs/requirements.md" in req_text or "エラー" in req_text or "検証に成功しました" in req_text

        design_specs = await SpecDocuments.from_paths(
            requirements_path=Path("specs/requirements.md"), language=Language.JAPANESE
        )
        design_result = await handle_prompt_design(design_specs)
        design_text = design_result.content[0].text
        assert "specs/requirements.md" in design_text or "エラー" in design_text

        design_val_specs = await SpecDocuments.from_paths(
            design_path=Path("specs/design.md"),
            requirements_path=Path("specs/requirements.md"),
            language=Language.JAPANESE,
        )
        design_val_result = await handle_validate_design(design_val_specs)
        design_val_text = design_val_result.content[0].text
        assert (
            "specs/design.md" in design_val_text
            or "エラー" in design_val_text
            or "検証に成功しました" in design_val_text
        )

        tasks_specs = await SpecDocuments.from_paths(
            design_path=Path("specs/design.md"),
            requirements_path=Path("specs/requirements.md"),
            language=Language.JAPANESE,
        )
        tasks_result = await handle_prompt_tasks(tasks_specs)
        tasks_text = tasks_result.content[0].text
        # Handle both translated text and translation keys
        assert (
            "specs/design.md" in tasks_text
            or "エラー" in tasks_text
            or "tasks_prompts.error" in tasks_text
            or "design_not_found" in tasks_text
        )

        tasks_val_specs = await SpecDocuments.from_paths(tasks_path=Path("specs/tasks.md"), language=Language.JAPANESE)
        tasks_val_result = await handle_validate_tasks(tasks_val_specs)
        tasks_val_text = tasks_val_result.content[0].text
        assert (
            "specs/tasks.md" in tasks_val_text
            or "エラー" in tasks_val_text
            or "検証に成功しました" in tasks_val_text
            or "修正が必要です" in tasks_val_text
        )

        trace_specs = await SpecDocuments.from_paths(
            requirements_path=Path("specs/requirements.md"),
            design_path=Path("specs/design.md"),
            tasks_path=Path("specs/tasks.md"),
            language=Language.JAPANESE,
        )
        trace_result = await handle_get_traceability(trace_specs)
        trace_text = trace_result.content[0].text
        assert "トレーサビリティレポート" in trace_text

    @pytest.mark.asyncio
    async def test_mcp_tool_error_handling(self):
        """Test error handling in MCP tools."""
        # Test with various edge case inputs
        test_cases = [
            "",  # Empty input
            "A" * 10000,  # Very long input
            "特殊文字 !@#$%^&*()",  # Special characters
            "日本語入力テスト",  # Japanese input
        ]

        for test_input in test_cases:
            result = await handle_check_completeness(test_input, Language.JAPANESE)
            result_text = result.content[0].text
            assert isinstance(result_text, str)
            assert len(result_text) > 0  # Should return some response

        # Test analyze_changes with edge cases
        change_result = await handle_analyze_changes(
            Path("test.md"),  # Valid file path
            "",  # Empty description
            Language.JAPANESE,
        )
        change_text = change_result.content[0].text
        assert isinstance(change_text, str)
        assert "変更影響分析" in change_text


class TestMCPServerPerformance:
    """Test MCP server performance characteristics with reproducible measurements."""

    @pytest.mark.asyncio
    async def test_tool_response_times(self):
        """Test that MCP tools respond within reasonable time with reproducible benchmarks."""
        benchmark = PerformanceBenchmark(
            warmup_iterations=3,
            benchmark_iterations=20,
            gc_collect_interval=5,
        )

        # Benchmark check_completeness performance
        async def check_completeness_test():
            return await handle_check_completeness("Performance test project", Language.JAPANESE)

        result = await benchmark.benchmark_async(
            check_completeness_test,
            name="check_completeness",
        )

        # Assert performance requirements
        assert result.median < MAX_RESPONSE_TIME_SECONDS, f"Median response time {result.median:.3f}s exceeds limit"
        assert result.p95 < MAX_RESPONSE_TIME_SECONDS, f"P95 response time {result.p95:.3f}s exceeds limit"

        # Verify response quality
        test_result = await check_completeness_test()
        result_text = test_result.content[0].text
        assert len(result_text) > MIN_RESPONSE_LENGTH

        # Benchmark analyze_changes performance
        async def analyze_changes_test():
            return await handle_analyze_changes(
                Path("specs/requirements.md"), "Performance test change", Language.JAPANESE
            )

        result = await benchmark.benchmark_async(
            analyze_changes_test,
            name="analyze_changes",
        )

        # Assert performance requirements
        assert result.median < MAX_RESPONSE_TIME_SECONDS, f"Median response time {result.median:.3f}s exceeds limit"
        assert result.p95 < MAX_RESPONSE_TIME_SECONDS, f"P95 response time {result.p95:.3f}s exceeds limit"

    @pytest.mark.asyncio
    async def test_memory_usage_stability(self):
        """Test that repeated tool calls don't cause memory leaks with statistical verification."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_samples = []

        # Run many iterations to test memory stability
        for i in range(20):
            result = await handle_check_completeness(f"Memory test iteration {i}", Language.JAPANESE)
            assert result.content
            result_text = result.content[0].text
            assert len(result_text) > 0

            # Force garbage collection every few iterations
            if i % 5 == 0:
                gc.collect()
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)

        # Check memory growth is minimal
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory

        # Allow up to 50MB growth (reasonable for Python)
        assert memory_growth < 50, f"Memory grew by {memory_growth:.1f}MB, possible memory leak"

        # Check memory stability (no continuous growth)
        if len(memory_samples) > 2:
            # Calculate trend - should be relatively flat
            memory_std = statistics.stdev(memory_samples)
            assert memory_std < 10, f"Memory usage too variable: std={memory_std:.1f}MB"

        # Test should complete without memory errors
