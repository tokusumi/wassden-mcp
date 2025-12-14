"""Unit tests for performance profiler module.

Tests for TASK-02-02 performance measurement functionality.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from wassden.lib.experiment import PerformanceDetail, PerformanceReport
from wassden.lib.performance_profiler import (
    PerformanceProfiler,
    ProfilingError,
)

pytestmark = pytest.mark.dev


@pytest.mark.dev
class TestPerformanceProfiler:
    """Test cases for PerformanceProfiler."""

    @pytest.fixture
    def profiler(self):
        """Create PerformanceProfiler instance."""
        return PerformanceProfiler(memory_limit_mb=500, timeout_seconds=10)

    @pytest.fixture
    def sample_sync_function(self):
        """Create a sample synchronous function for testing."""

        def test_function(x: int = 5) -> int:
            """Simple test function that returns double the input."""
            return x * 2

        return test_function

    @pytest.fixture
    def sample_async_function(self):
        """Create a sample asynchronous function for testing."""

        async def test_async_function(x: int = 5) -> int:
            """Simple async test function that returns double the input."""
            await asyncio.sleep(0.001)  # Small delay to simulate async work
            return x * 2

        return test_async_function

    @pytest.mark.asyncio
    async def test_measure_performance_sync_success(self, profiler, sample_sync_function):
        """Test successful performance measurement of synchronous function.

        Implements: REQ-02 - 観点1: ミリ秒単位での実行時間測定
        """
        result = await profiler.measure_performance(sample_sync_function, 10)

        # Verify report structure
        assert isinstance(result, PerformanceReport)
        assert result.total_executions == 1
        assert result.successful_executions == 1
        assert result.failed_executions == 0

        # Verify timing measurements (should be positive and reasonable)
        assert result.average_wall_time_ms >= 0
        assert result.average_cpu_time_ms >= 0
        assert result.average_wall_time_ms < 1000  # Should complete quickly

        # Verify memory measurements
        assert result.average_memory_mb >= 0
        assert result.peak_memory_mb >= 0

        # Verify details
        assert len(result.details) == 1
        detail = result.details[0]
        assert isinstance(detail, PerformanceDetail)
        assert detail.success is True
        assert detail.function_name == "test_function"
        assert detail.error_message is None

        # Verify result data
        assert result.result_data == 20  # 10 * 2

    @pytest.mark.asyncio
    async def test_measure_performance_async_success(self, profiler, sample_async_function):
        """Test successful performance measurement of asynchronous function.

        Implements: REQ-02 - 観点2: バイト単位でのメモリ使用量測定
        """
        result = await profiler.measure_performance(sample_async_function, 15)

        # Verify report structure
        assert isinstance(result, PerformanceReport)
        assert result.total_executions == 1
        assert result.successful_executions == 1
        assert result.failed_executions == 0

        # Verify timing measurements
        assert result.average_wall_time_ms >= 1  # Should be at least 1ms due to sleep
        assert result.average_cpu_time_ms >= 0

        # Verify memory measurements
        assert result.average_memory_mb >= 0
        assert result.peak_memory_mb >= 0

        # Verify details
        detail = result.details[0]
        assert detail.success is True
        assert detail.function_name == "test_async_function"
        assert result.result_data == 30  # 15 * 2

    @pytest.mark.asyncio
    async def test_measure_performance_function_failure(self, profiler):
        """Test performance measurement when function fails."""

        def failing_function():
            raise ValueError("Test error")

        result = await profiler.measure_performance(failing_function)

        # Verify error handling
        assert result.total_executions == 1
        assert result.successful_executions == 0
        assert result.failed_executions == 1

        # Timing should still be recorded
        assert result.average_wall_time_ms >= 0
        assert result.average_cpu_time_ms >= 0

        # Verify error details
        detail = result.details[0]
        assert detail.success is False
        assert detail.error_message == "Test error"
        assert result.result_data is None

    @pytest.mark.asyncio
    async def test_measure_performance_memory_limit_exceeded(self):
        """Test memory limit exceeded handling."""
        # Create profiler with low memory limit for this test
        profiler = PerformanceProfiler(memory_limit_mb=200, timeout_seconds=10)

        def memory_intensive_function():
            return "result"

        # Mock the memory check to simulate exceeding the limit
        # Need enough values for: initial_memory, monitoring_check, final_memory
        with patch.object(profiler, "_get_memory_usage_mb", side_effect=[50.0, 600.0, 600.0]):
            result = await profiler.measure_performance(memory_intensive_function)

            # Should handle the memory exceeded error gracefully
            assert result.failed_executions == 1
            assert "Memory limit exceeded" in result.details[0].error_message

    @pytest.mark.asyncio
    async def test_measure_performance_timeout(self):
        """Test timeout handling."""
        profiler = PerformanceProfiler(memory_limit_mb=50, timeout_seconds=0.001)  # Very short timeout

        async def slow_function():
            await asyncio.sleep(0.1)  # Longer than timeout
            return "result"

        result = await profiler.measure_performance(slow_function)

        # Should handle timeout gracefully
        assert result.failed_executions == 1
        assert "timeout" in result.details[0].error_message.lower()

    @pytest.mark.asyncio
    async def test_measure_multiple_executions_success(self, profiler, sample_sync_function):
        """Test multiple execution measurement for statistical accuracy."""
        iterations = 3
        result = await profiler.measure_multiple_executions(sample_sync_function, iterations, 7)

        # Verify aggregated results
        assert result.total_executions == iterations
        assert result.successful_executions == iterations
        assert result.failed_executions == 0

        # Verify details
        assert len(result.details) == iterations
        for detail in result.details:
            assert detail.success is True
            assert detail.function_name == "test_function"

        # Verify averages are reasonable
        assert result.average_wall_time_ms >= 0
        assert result.average_cpu_time_ms >= 0
        assert result.average_memory_mb >= 0

        # Result data should be None for multiple executions
        assert result.result_data is None

    @pytest.mark.asyncio
    async def test_measure_multiple_executions_mixed_results(self, profiler):
        """Test multiple executions with mixed success/failure results."""
        call_count = 0

        def sometimes_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Fail on second call
                raise RuntimeError("Second call fails")
            return call_count

        iterations = 3
        result = await profiler.measure_multiple_executions(sometimes_failing_function, iterations)

        # Should have mixed results
        assert result.total_executions == iterations
        assert result.successful_executions == 2
        assert result.failed_executions == 1

        # Check individual results
        assert len(result.details) == iterations
        assert result.details[0].success is True
        assert result.details[1].success is False
        assert result.details[2].success is True

        # Averages should be calculated from successful executions only
        assert result.average_wall_time_ms >= 0
        assert result.average_cpu_time_ms >= 0

    @pytest.mark.asyncio
    async def test_measure_multiple_executions_invalid_iterations(self, profiler, sample_sync_function):
        """Test multiple executions with invalid iteration count."""
        with pytest.raises(ProfilingError, match="At least 1 iteration is required"):
            await profiler.measure_multiple_executions(sample_sync_function, 0)

    def test_profile_validation_pipeline(self, profiler):
        """Test validation pipeline profiling."""
        # Create sample documents
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f1:
            f1.write("# Test Document 1\n\nSome content.")
            doc1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f2:
            f2.write("# Test Document 2\n\nMore content.")
            doc2 = Path(f2.name)

        try:
            # Define mock validation functions
            def validate_function1(path, language):
                return f"validated {path} in {language}"

            async def validate_function2(path, language):
                await asyncio.sleep(0.001)
                return f"async validated {path} in {language}"

            functions = [validate_function1, validate_function2]

            # Profile the pipeline
            results = profiler.profile_validation_pipeline([doc1, doc2], functions)

            # Verify results
            assert len(results) == 2
            assert "validate_function1" in results
            assert "validate_function2" in results

            # Each should be a performance report
            for report in results.values():
                assert isinstance(report, PerformanceReport)
                assert report.total_executions == 1

        finally:
            # Clean up
            doc1.unlink()
            doc2.unlink()

    def test_profile_validation_pipeline_with_errors(self, profiler):
        """Test validation pipeline profiling with function errors."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Document\n\nContent.")
            doc = Path(f.name)

        try:

            def failing_function(_path, _language):
                raise ValueError("Validation failed")

            results = profiler.profile_validation_pipeline([doc], [failing_function])

            # Should have error report
            assert len(results) == 1
            assert "failing_function" in results

            report = results["failing_function"]
            assert report.failed_executions == 1
            assert report.successful_executions == 0
            assert report.details[0].success is False

        finally:
            doc.unlink()

    def test_get_memory_usage_mb(self, profiler):
        """Test memory usage measurement."""
        memory_usage = profiler._get_memory_usage_mb()

        # Should return a reasonable value
        assert memory_usage >= 0
        assert memory_usage < 1000  # Should be less than 1GB for test

    @pytest.mark.asyncio
    async def test_execute_with_monitoring_sync_function(self, profiler, sample_sync_function):
        """Test function execution monitoring for sync functions."""
        result = await profiler._execute_with_monitoring(sample_sync_function, 8)

        assert result == 16  # 8 * 2

    @pytest.mark.asyncio
    async def test_execute_with_monitoring_async_function(self, profiler, sample_async_function):
        """Test function execution monitoring for async functions."""
        result = await profiler._execute_with_monitoring(sample_async_function, 12)

        assert result == 24  # 12 * 2

    def test_profiler_initialization(self):
        """Test profiler initialization with custom limits."""
        profiler = PerformanceProfiler(memory_limit_mb=200, timeout_seconds=300)

        assert profiler.memory_limit_mb == 200
        assert profiler.timeout_seconds == 300
        assert profiler._process is not None

    def test_profiler_default_initialization(self):
        """Test profiler initialization with default values."""
        profiler = PerformanceProfiler()

        assert profiler.memory_limit_mb == 100
        assert profiler.timeout_seconds == 600
