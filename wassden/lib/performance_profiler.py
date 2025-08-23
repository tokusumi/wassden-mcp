"""Performance profiler component for measuring validation process performance.

This module provides functionality to measure execution time and memory usage
of validation processes for performance analysis and optimization.

Implements: REQ-02, TASK-02-02
"""

import asyncio
import gc
import inspect
import tempfile
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path
from typing import Any

import psutil

from wassden.language_types import Language
from wassden.lib.experiment import PerformanceDetail, PerformanceReport


class PerformanceProfilerError(Exception):
    """Base exception for performance profiler errors."""


class ProfilingError(PerformanceProfilerError):
    """Raised when performance profiling fails."""


class MemoryLimitExceededError(PerformanceProfilerError):
    """Raised when memory usage exceeds limits."""


class ExecutionTimeoutError(PerformanceProfilerError):
    """Raised when execution time exceeds timeout."""


class PerformanceProfiler:
    """Profiler for measuring validation process performance."""

    def __init__(self, memory_limit_mb: int = 100, timeout_seconds: int = 600) -> None:
        """Initialize performance profiler.

        Args:
            memory_limit_mb: Memory usage limit in megabytes
            timeout_seconds: Execution timeout in seconds
        """
        self.memory_limit_mb = memory_limit_mb
        self.timeout_seconds = timeout_seconds
        self._process = psutil.Process()

    async def measure_performance(
        self, validation_function: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> PerformanceReport:
        """Measure performance of a validation function.

        Args:
            validation_function: Function to profile
            *args: Arguments for the validation function
            **kwargs: Keyword arguments for the validation function

        Returns:
            Performance measurement report

        Raises:
            ProfilingError: If profiling fails
            MemoryLimitExceededError: If memory limit is exceeded
            ExecutionTimeoutError: If execution timeout is exceeded

        Implements: REQ-02 - パフォーマンス測定
        """
        # Start memory tracing
        tracemalloc.start()

        # Record initial memory usage
        initial_memory = self._get_memory_usage_mb()

        # Start timing
        start_time = time.perf_counter()
        start_process_time = time.process_time()

        try:
            # Execute the validation function with monitoring
            result = await self._execute_with_monitoring(validation_function, *args, **kwargs)

            # Record end timing
            end_time = time.perf_counter()
            end_process_time = time.process_time()

            # Get memory statistics
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            final_memory = self._get_memory_usage_mb()

            # Calculate metrics
            wall_time_ms = (end_time - start_time) * 1000
            cpu_time_ms = (end_process_time - start_process_time) * 1000
            memory_used_mb = final_memory - initial_memory
            peak_memory_mb = peak_memory / (1024 * 1024)  # Convert bytes to MB

            # Create performance details
            performance_detail = PerformanceDetail(
                wall_time_ms=wall_time_ms,
                cpu_time_ms=cpu_time_ms,
                memory_used_mb=memory_used_mb,
                peak_memory_mb=peak_memory_mb,
                function_name=validation_function.__name__
                if hasattr(validation_function, "__name__")
                else str(validation_function),
                success=True,
                error_message=None,
            )

            return PerformanceReport(
                total_executions=1,
                successful_executions=1,
                failed_executions=0,
                average_wall_time_ms=wall_time_ms,
                average_cpu_time_ms=cpu_time_ms,
                average_memory_mb=memory_used_mb,
                peak_memory_mb=peak_memory_mb,
                details=[performance_detail],
                result_data=result if isinstance(result, dict | list | str | int | float | bool) else str(result),
            )

        except Exception as e:
            end_time = time.perf_counter()
            end_process_time = time.process_time()

            # Calculate partial metrics
            wall_time_ms = (end_time - start_time) * 1000
            cpu_time_ms = (end_process_time - start_process_time) * 1000
            final_memory = self._get_memory_usage_mb()
            memory_used_mb = final_memory - initial_memory

            # Create failed performance details
            performance_detail = PerformanceDetail(
                wall_time_ms=wall_time_ms,
                cpu_time_ms=cpu_time_ms,
                memory_used_mb=memory_used_mb,
                peak_memory_mb=0.0,  # Cannot determine peak on failure
                function_name=validation_function.__name__
                if hasattr(validation_function, "__name__")
                else str(validation_function),
                success=False,
                error_message=str(e),
            )

            return PerformanceReport(
                total_executions=1,
                successful_executions=0,
                failed_executions=1,
                average_wall_time_ms=wall_time_ms,
                average_cpu_time_ms=cpu_time_ms,
                average_memory_mb=memory_used_mb,
                peak_memory_mb=0.0,
                details=[performance_detail],
                result_data=None,
            )

        finally:
            tracemalloc.stop()
            # Force garbage collection
            gc.collect()

    async def measure_multiple_executions(
        self, validation_function: Callable[..., Any], iterations: int = 5, *args: Any, **kwargs: Any
    ) -> PerformanceReport:
        """Measure performance across multiple executions for statistical accuracy.

        Args:
            validation_function: Function to profile
            iterations: Number of executions to perform
            *args: Arguments for the validation function
            **kwargs: Keyword arguments for the validation function

        Returns:
            Aggregated performance measurement report

        Implements: REQ-02 - 観点2: 複数実行での統計的測定
        """
        if iterations < 1:
            raise ProfilingError("At least 1 iteration is required")

        details = []
        successful_count = 0
        failed_count = 0
        total_wall_time = 0.0
        total_cpu_time = 0.0
        total_memory = 0.0
        max_peak_memory = 0.0

        for _ in range(iterations):
            try:
                report = await self.measure_performance(validation_function, *args, **kwargs)
                detail = report.details[0]
                details.append(detail)

                if detail.success:
                    successful_count += 1
                    total_wall_time += detail.wall_time_ms
                    total_cpu_time += detail.cpu_time_ms
                    total_memory += detail.memory_used_mb
                    max_peak_memory = max(max_peak_memory, detail.peak_memory_mb)
                else:
                    failed_count += 1

            except Exception as e:
                failed_count += 1
                error_detail = PerformanceDetail(
                    wall_time_ms=0.0,
                    cpu_time_ms=0.0,
                    memory_used_mb=0.0,
                    peak_memory_mb=0.0,
                    function_name=validation_function.__name__
                    if hasattr(validation_function, "__name__")
                    else str(validation_function),
                    success=False,
                    error_message=str(e),
                )
                details.append(error_detail)

        # Calculate averages
        avg_wall_time = total_wall_time / successful_count if successful_count > 0 else 0.0
        avg_cpu_time = total_cpu_time / successful_count if successful_count > 0 else 0.0
        avg_memory = total_memory / successful_count if successful_count > 0 else 0.0

        return PerformanceReport(
            total_executions=iterations,
            successful_executions=successful_count,
            failed_executions=failed_count,
            average_wall_time_ms=avg_wall_time,
            average_cpu_time_ms=avg_cpu_time,
            average_memory_mb=avg_memory,
            peak_memory_mb=max_peak_memory,
            details=details,
            result_data=None,  # Not applicable for multiple executions
        )

    async def _execute_with_monitoring(self, validation_function: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function with real-time monitoring for limits.

        Args:
            validation_function: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            Function result

        Raises:
            MemoryLimitExceededError: If memory limit is exceeded
            ExecutionTimeoutError: If execution timeout is exceeded
        """
        start_time = time.perf_counter()

        # Check if function is async

        if asyncio.iscoroutinefunction(validation_function):
            # Async function
            result = await validation_function(*args, **kwargs)
        elif inspect.iscoroutinefunction(validation_function):
            # Async function (alternative check)
            result = await validation_function(*args, **kwargs)
        else:
            # Sync function
            result = validation_function(*args, **kwargs)

        # Check timeout
        elapsed_time = time.perf_counter() - start_time
        if elapsed_time > self.timeout_seconds:
            raise ExecutionTimeoutError(f"Execution timeout exceeded: {elapsed_time:.2f}s > {self.timeout_seconds}s")

        # Check memory usage
        current_memory = self._get_memory_usage_mb()
        if current_memory > self.memory_limit_mb:
            raise MemoryLimitExceededError(f"Memory limit exceeded: {current_memory:.2f}MB > {self.memory_limit_mb}MB")

        return result

    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in megabytes.

        Returns:
            Current memory usage in MB
        """
        try:
            memory_info = self._process.memory_info()
            return float(memory_info.rss / (1024 * 1024))  # Convert bytes to MB
        except Exception:
            # Fallback method
            return 0.0

    def profile_validation_pipeline(
        self,
        document_paths: list[Path],
        validation_functions: list[Callable[..., Any]],
        language: Language = Language.JAPANESE,
    ) -> dict[str, PerformanceReport]:
        """Profile a complete validation pipeline with multiple functions.

        Args:
            document_paths: Paths to documents to validate
            validation_functions: List of validation functions to profile
            language: Language for validation

        Returns:
            Dictionary mapping function names to performance reports

        Implements: REQ-02 - パイプライン全体のプロファイリング
        """
        results = {}

        for func in validation_functions:
            func_name = func.__name__ if hasattr(func, "__name__") else str(func)
            try:
                # For validation functions that take document paths
                if len(document_paths) == 1:
                    report = asyncio.run(self.measure_performance(func, document_paths[0], language))
                else:
                    report = asyncio.run(self.measure_performance(func, document_paths, language))
                results[func_name] = report
            except Exception as e:
                # Create error report
                error_detail = PerformanceDetail(
                    wall_time_ms=0.0,
                    cpu_time_ms=0.0,
                    memory_used_mb=0.0,
                    peak_memory_mb=0.0,
                    function_name=func_name,
                    success=False,
                    error_message=str(e),
                )

                results[func_name] = PerformanceReport(
                    total_executions=1,
                    successful_executions=0,
                    failed_executions=1,
                    average_wall_time_ms=0.0,
                    average_cpu_time_ms=0.0,
                    average_memory_mb=0.0,
                    peak_memory_mb=0.0,
                    details=[error_detail],
                    result_data=None,
                )

        return results

    async def profile_operation(
        self,
        operation_name: str,
        rounds: int = 5,
        warmup: int = 2,
        memory_profiling: bool = True,
    ) -> PerformanceReport:
        """Profile a predefined operation by name.

        Args:
            operation_name: Name of predefined operation to profile
            rounds: Number of measurement rounds
            warmup: Number of warmup rounds
            memory_profiling: Whether to enable memory profiling

        Returns:
            Performance report for the operation

        Raises:
            ProfilingError: If operation not found or profiling fails

        Implements: REQ-02 - 名前指定による定義済み操作のプロファイリング
        """
        # Define predefined operations
        predefined_operations = {
            "default_operation": self._default_operation,
            "memory_allocation": self._memory_allocation_operation,
            "cpu_intensive": self._cpu_intensive_operation,
            "file_io": self._file_io_operation,
        }

        if operation_name not in predefined_operations:
            available_ops = list(predefined_operations.keys())
            raise ProfilingError(f"Unknown operation '{operation_name}'. Available: {available_ops}")

        operation = predefined_operations[operation_name]

        return await self.profile_custom_operation(
            operation,
            operation_name,
            rounds=rounds,
            warmup=warmup,
            memory_profiling=memory_profiling,
        )

    async def profile_custom_operation(
        self,
        operation: Callable[..., Any],
        _operation_name: str,
        rounds: int = 5,
        warmup: int = 2,
        memory_profiling: bool = True,
    ) -> PerformanceReport:
        """Profile a custom operation function.

        Args:
            operation: Custom operation function to profile
            operation_name: Name for the operation
            rounds: Number of measurement rounds
            warmup: Number of warmup rounds
            memory_profiling: Whether to enable memory profiling

        Returns:
            Performance report for the operation

        Raises:
            ProfilingError: If profiling fails

        Implements: REQ-02 - カスタム操作のプロファイリング
        """
        try:
            # Warmup rounds
            for _ in range(warmup):
                try:
                    if asyncio.iscoroutinefunction(operation):
                        await operation()
                    else:
                        operation()
                except Exception:
                    pass  # Ignore warmup errors

            # Force garbage collection before measurement
            gc.collect()

            # Measurement rounds
            return await self.measure_performance(
                operation,
                rounds=rounds,
                memory_profiling=memory_profiling,
            )

        except Exception as e:
            raise ProfilingError(f"Custom operation profiling failed: {e}") from e

    # Predefined operation implementations

    def _default_operation(self) -> str:
        """Default operation for testing."""
        time.sleep(0.001)  # 1ms delay
        return "default_operation_completed"

    def _memory_allocation_operation(self) -> list[int]:
        """Memory allocation test operation."""
        # Allocate approximately 1MB of memory
        return list(range(250000))  # ~1MB of integers

    def _cpu_intensive_operation(self) -> int:
        """CPU intensive test operation."""
        # Calculate sum of squares
        return sum(i * i for i in range(10000))

    def _file_io_operation(self) -> str:
        """File I/O test operation."""
        # Create temporary file and write/read data
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            data = "test data for file I/O operation\n" * 100
            tmp.write(data)
            tmp.seek(0)
            result = tmp.read()

        return result[:50]  # Return first 50 chars
