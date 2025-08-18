"""Tests for benchmark utilities."""

import asyncio
import time
from unittest.mock import Mock, patch

import pytest

from wassden.utils.benchmark import (
    BenchmarkResult,
    PerformanceBenchmark,
    measure_async_performance,
    measure_sync_performance,
)


class TestBenchmarkResult:
    """Test BenchmarkResult dataclass."""

    def test_benchmark_result_str(self):
        """Test string representation of BenchmarkResult."""
        result = BenchmarkResult(
            name="test_benchmark",
            mean=0.001,
            median=0.0008,
            std_dev=0.0002,
            min=0.0005,
            max=0.002,
            p95=0.0015,
            p99=0.0018,
            iterations=50,
            samples=[0.001, 0.0008, 0.002],
        )

        str_result = str(result)
        assert "test_benchmark:" in str_result
        assert "Mean: 1.000ms" in str_result
        assert "Median: 0.800ms" in str_result
        assert "Std Dev: 0.200ms" in str_result
        assert "Min: 0.500ms" in str_result
        assert "Max: 2.000ms" in str_result
        assert "P95: 1.500ms" in str_result
        assert "P99: 1.800ms" in str_result
        assert "Iterations: 50" in str_result


class TestPerformanceBenchmark:
    """Test PerformanceBenchmark class."""

    def test_init_default_values(self):
        """Test PerformanceBenchmark initialization with default values."""
        benchmark = PerformanceBenchmark()
        assert benchmark.warmup_iterations == 5
        assert benchmark.benchmark_iterations == 100
        assert benchmark.gc_collect_interval == 10
        assert benchmark.cpu_affinity is False

    def test_init_custom_values(self):
        """Test PerformanceBenchmark initialization with custom values."""
        benchmark = PerformanceBenchmark(
            warmup_iterations=3,
            benchmark_iterations=20,
            gc_collect_interval=5,
            cpu_affinity=True,
        )
        assert benchmark.warmup_iterations == 3
        assert benchmark.benchmark_iterations == 20
        assert benchmark.gc_collect_interval == 5
        assert benchmark.cpu_affinity is True

    @patch("wassden.utils.benchmark.gc.collect")
    def test_setup_environment_basic(self, mock_gc):
        """Test basic environment setup without CPU affinity."""
        benchmark = PerformanceBenchmark(cpu_affinity=False)
        benchmark._setup_environment()

        # Should call gc.collect() 3 times
        assert mock_gc.call_count == 3

    @patch("wassden.utils.benchmark.gc.collect")
    @patch("wassden.utils.benchmark.psutil.Process")
    def test_setup_environment_with_cpu_affinity(self, mock_process_class, mock_gc):
        """Test environment setup with CPU affinity."""
        mock_process = Mock()
        mock_process.cpu_affinity.return_value = [0, 1, 2, 3]
        mock_process_class.return_value = mock_process

        benchmark = PerformanceBenchmark(cpu_affinity=True)
        benchmark._setup_environment()

        # Should call gc.collect() 3 times and set CPU affinity
        assert mock_gc.call_count == 3
        mock_process.cpu_affinity.assert_called_with([0])
        assert benchmark._original_affinity == [0, 1, 2, 3]

    @patch("wassden.utils.benchmark.psutil.Process")
    def test_setup_environment_cpu_affinity_error(self, mock_process_class):
        """Test environment setup when CPU affinity fails."""
        error_msg = "cpu_affinity not supported"
        mock_process_class.side_effect = AttributeError(error_msg)

        benchmark = PerformanceBenchmark(cpu_affinity=True)
        # Should not raise exception
        benchmark._setup_environment()

    @patch("wassden.utils.benchmark.psutil.Process")
    def test_restore_environment(self, mock_process_class):
        """Test environment restoration."""
        mock_process = Mock()
        mock_process_class.return_value = mock_process

        benchmark = PerformanceBenchmark()
        benchmark._original_affinity = [0, 1, 2, 3]
        benchmark._restore_environment()

        # Should restore original CPU affinity
        mock_process.cpu_affinity.assert_called_with([0, 1, 2, 3])

    def test_restore_environment_no_affinity(self):
        """Test environment restoration when no affinity was set."""
        benchmark = PerformanceBenchmark()
        benchmark._original_affinity = None
        # Should not raise exception
        benchmark._restore_environment()

    @patch("wassden.utils.benchmark.psutil.Process")
    def test_restore_environment_error(self, mock_process_class):
        """Test environment restoration when restore fails."""
        error_msg = "Permission denied"
        mock_process_class.side_effect = OSError(error_msg)

        benchmark = PerformanceBenchmark()
        benchmark._original_affinity = [0, 1]
        # Should not raise exception
        benchmark._restore_environment()

    @pytest.mark.asyncio
    async def test_benchmark_async_basic(self):
        """Test basic async benchmarking."""

        async def test_func():
            await asyncio.sleep(0.001)
            return "test"

        benchmark = PerformanceBenchmark(
            warmup_iterations=1,
            benchmark_iterations=3,
            gc_collect_interval=1,
        )

        result = await benchmark.benchmark_async(test_func, name="test")

        assert result.name == "test"
        assert result.iterations == 3
        assert len(result.samples) == 3
        assert result.mean > 0
        assert result.median > 0
        assert result.min <= result.median <= result.max

    @pytest.mark.asyncio
    async def test_benchmark_async_with_args(self):
        """Test async benchmarking with arguments."""

        async def test_func(x, y, z=None):
            await asyncio.sleep(0.001)
            return x + y + (z or 0)

        benchmark = PerformanceBenchmark(
            warmup_iterations=1,
            benchmark_iterations=2,
        )

        result = await benchmark.benchmark_async(test_func, 1, 2, z=3, name="test_with_args")

        assert result.name == "test_with_args"
        assert result.iterations == 2

    def test_benchmark_sync_basic(self):
        """Test basic sync benchmarking."""

        def test_func():
            time.sleep(0.001)
            return "test"

        benchmark = PerformanceBenchmark(
            warmup_iterations=1,
            benchmark_iterations=3,
            gc_collect_interval=1,
        )

        result = benchmark.benchmark_sync(test_func, name="sync_test")

        assert result.name == "sync_test"
        assert result.iterations == 3
        assert len(result.samples) == 3
        assert result.mean > 0
        assert result.median > 0

    def test_benchmark_sync_with_args(self):
        """Test sync benchmarking with arguments."""

        def test_func(x, y, z=None):
            time.sleep(0.001)
            return x + y + (z or 0)

        benchmark = PerformanceBenchmark(
            warmup_iterations=1,
            benchmark_iterations=2,
        )

        result = benchmark.benchmark_sync(test_func, 1, 2, z=3, name="sync_with_args")

        assert result.name == "sync_with_args"
        assert result.iterations == 2

    def test_statistical_calculations(self):
        """Test statistical calculations in benchmark results."""

        def test_func():
            # Variable execution time
            time.sleep(0.001 + (len(test_func.__name__) % 3) * 0.0001)

        benchmark = PerformanceBenchmark(
            warmup_iterations=1,
            benchmark_iterations=10,
        )

        result = benchmark.benchmark_sync(test_func, name="stats_test")

        # Verify statistical calculations
        assert result.min <= result.median <= result.max
        # Note: median may be greater than mean for normal distributions
        assert result.p95 >= result.median
        assert result.p99 >= result.p95
        assert result.std_dev >= 0

    def test_single_iteration_stats(self):
        """Test statistical calculations with single iteration."""

        def test_func():
            time.sleep(0.001)

        benchmark = PerformanceBenchmark(
            warmup_iterations=1,
            benchmark_iterations=1,
        )

        result = benchmark.benchmark_sync(test_func, name="single_test")

        # With single iteration, std_dev should be 0
        assert result.std_dev == 0.0
        assert result.min == result.max == result.median == result.mean


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_measure_async_performance(self):
        """Test measure_async_performance convenience function."""

        async def test_func():
            await asyncio.sleep(0.001)
            return "async_result"

        result = await measure_async_performance(
            test_func,
            iterations=3,
            warmup=1,
            name="convenience_async",
        )

        assert result.name == "convenience_async"
        assert result.iterations == 3

    def test_measure_sync_performance(self):
        """Test measure_sync_performance convenience function."""

        def test_func():
            time.sleep(0.001)
            return "sync_result"

        result = measure_sync_performance(
            test_func,
            iterations=3,
            warmup=1,
            name="convenience_sync",
        )

        assert result.name == "convenience_sync"
        assert result.iterations == 3

    @pytest.mark.asyncio
    async def test_measure_async_with_args(self):
        """Test async measurement with function arguments."""

        async def test_func(value, multiplier=2):
            await asyncio.sleep(0.001)
            return value * multiplier

        result = await measure_async_performance(
            test_func,
            10,
            multiplier=3,
            iterations=2,
            name="async_with_args",
        )

        assert result.name == "async_with_args"
        assert result.iterations == 2

    def test_measure_sync_with_args(self):
        """Test sync measurement with function arguments."""

        def test_func(value, multiplier=2):
            time.sleep(0.001)
            return value * multiplier

        result = measure_sync_performance(
            test_func,
            10,
            multiplier=3,
            iterations=2,
            name="sync_with_args",
        )

        assert result.name == "sync_with_args"
        assert result.iterations == 2


class TestBenchmarkEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_async_function_with_exception(self):
        """Test benchmarking function that raises exception."""

        async def failing_func():
            await asyncio.sleep(0.001)
            msg = "Test error"
            raise ValueError(msg)

        benchmark = PerformanceBenchmark(
            warmup_iterations=1,
            benchmark_iterations=1,
        )

        # Should propagate the exception
        with pytest.raises(ValueError, match="Test error"):
            await benchmark.benchmark_async(failing_func, name="failing")

    def test_sync_function_with_exception(self):
        """Test benchmarking sync function that raises exception."""

        def failing_func():
            time.sleep(0.001)
            msg = "Test error"
            raise ValueError(msg)

        benchmark = PerformanceBenchmark(
            warmup_iterations=1,
            benchmark_iterations=1,
        )

        # Should propagate the exception
        with pytest.raises(ValueError, match="Test error"):
            benchmark.benchmark_sync(failing_func, name="failing")

    @pytest.mark.asyncio
    async def test_zero_iterations(self):
        """Test benchmark with zero iterations raises error."""

        async def test_func():
            return "test"

        benchmark = PerformanceBenchmark(
            warmup_iterations=0,
            benchmark_iterations=0,
        )

        # Should raise StatisticsError for empty sample list
        with pytest.raises(Exception, match="mean requires at least one data point"):
            await benchmark.benchmark_async(test_func, name="zero")

    def test_percentile_edge_cases(self):
        """Test percentile calculations with edge cases."""

        def test_func():
            pass

        benchmark = PerformanceBenchmark(
            warmup_iterations=0,
            benchmark_iterations=2,  # Small sample size
        )

        result = benchmark.benchmark_sync(test_func, name="edge")

        # With small sample, P95 and P99 should be max value
        assert result.p95 <= result.max
        assert result.p99 <= result.max
