"""Performance benchmarking utilities for reproducible measurements."""

import asyncio
import gc
import statistics
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import psutil


@dataclass
class BenchmarkResult:
    """Container for benchmark results with statistical analysis."""

    name: str
    mean: float
    median: float
    std_dev: float
    min: float
    max: float
    p95: float
    p99: float
    iterations: int
    samples: list[float]

    def __str__(self) -> str:
        """Format benchmark results for display."""
        return (
            f"{self.name}:\n"
            f"  Mean: {self.mean * 1000:.3f}ms\n"
            f"  Median: {self.median * 1000:.3f}ms\n"
            f"  Std Dev: {self.std_dev * 1000:.3f}ms\n"
            f"  Min: {self.min * 1000:.3f}ms\n"
            f"  Max: {self.max * 1000:.3f}ms\n"
            f"  P95: {self.p95 * 1000:.3f}ms\n"
            f"  P99: {self.p99 * 1000:.3f}ms\n"
            f"  Iterations: {self.iterations}"
        )


class PerformanceBenchmark:
    """Reproducible performance benchmarking utility."""

    def __init__(
        self,
        warmup_iterations: int = 5,
        benchmark_iterations: int = 100,
        gc_collect_interval: int = 10,
        cpu_affinity: bool = False,
    ):
        """Initialize benchmark configuration.

        Args:
            warmup_iterations: Number of warmup runs before measurement
            benchmark_iterations: Number of measurement iterations
            gc_collect_interval: Run garbage collection every N iterations
            cpu_affinity: Whether to pin process to specific CPU cores
        """
        self.warmup_iterations = warmup_iterations
        self.benchmark_iterations = benchmark_iterations
        self.gc_collect_interval = gc_collect_interval
        self.cpu_affinity = cpu_affinity
        self._original_affinity: list[int] | None = None

    def _setup_environment(self) -> None:
        """Prepare environment for reproducible measurements."""
        # Force garbage collection before starting
        gc.collect()
        gc.collect()
        gc.collect()

        # Set CPU affinity if requested (Linux/Unix only)
        if self.cpu_affinity:
            try:
                process = psutil.Process()
                if hasattr(process, "cpu_affinity"):
                    self._original_affinity = process.cpu_affinity()
                    # Pin to first CPU core for consistency
                    if self._original_affinity:
                        process.cpu_affinity([self._original_affinity[0]])
            except (AttributeError, OSError):
                # CPU affinity not supported on this platform
                pass

    def _restore_environment(self) -> None:
        """Restore original environment settings."""
        if self._original_affinity is not None:
            try:
                process = psutil.Process()
                if hasattr(process, "cpu_affinity"):
                    process.cpu_affinity(self._original_affinity)
            except (AttributeError, OSError):
                pass

    async def benchmark_async(
        self,
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        name: str = "Benchmark",
        **kwargs: Any,
    ) -> BenchmarkResult:
        """Benchmark an async function with statistical analysis.

        Args:
            func: Async function to benchmark
            *args: Positional arguments for the function
            name: Name for the benchmark
            **kwargs: Keyword arguments for the function

        Returns:
            BenchmarkResult with statistical analysis
        """
        self._setup_environment()

        try:
            # Warmup phase
            for _ in range(self.warmup_iterations):
                await func(*args, **kwargs)
                gc.collect()

            # Measurement phase
            samples: list[float] = []
            for i in range(self.benchmark_iterations):
                # Periodic garbage collection
                if i % self.gc_collect_interval == 0:
                    gc.collect()
                    await asyncio.sleep(0)  # Yield control

                # High-precision timing using perf_counter
                start = time.perf_counter()
                await func(*args, **kwargs)
                end = time.perf_counter()

                samples.append(end - start)

            # Calculate statistics
            samples.sort()
            mean = statistics.mean(samples)
            median = statistics.median(samples)
            std_dev = statistics.stdev(samples) if len(samples) > 1 else 0.0
            p95_index = int(len(samples) * 0.95)
            p99_index = int(len(samples) * 0.99)

            return BenchmarkResult(
                name=name,
                mean=mean,
                median=median,
                std_dev=std_dev,
                min=min(samples),
                max=max(samples),
                p95=samples[p95_index] if p95_index < len(samples) else max(samples),
                p99=samples[p99_index] if p99_index < len(samples) else max(samples),
                iterations=self.benchmark_iterations,
                samples=samples,
            )

        finally:
            self._restore_environment()

    def benchmark_sync(
        self,
        func: Callable[..., Any],
        *args: Any,
        name: str = "Benchmark",
        **kwargs: Any,
    ) -> BenchmarkResult:
        """Benchmark a synchronous function with statistical analysis.

        Args:
            func: Function to benchmark
            *args: Positional arguments for the function
            name: Name for the benchmark
            **kwargs: Keyword arguments for the function

        Returns:
            BenchmarkResult with statistical analysis
        """
        self._setup_environment()

        try:
            # Warmup phase
            for _ in range(self.warmup_iterations):
                func(*args, **kwargs)
                gc.collect()

            # Measurement phase
            samples: list[float] = []
            for i in range(self.benchmark_iterations):
                # Periodic garbage collection
                if i % self.gc_collect_interval == 0:
                    gc.collect()

                # High-precision timing using perf_counter
                start = time.perf_counter()
                func(*args, **kwargs)
                end = time.perf_counter()

                samples.append(end - start)

            # Calculate statistics
            samples.sort()
            mean = statistics.mean(samples)
            median = statistics.median(samples)
            std_dev = statistics.stdev(samples) if len(samples) > 1 else 0.0
            p95_index = int(len(samples) * 0.95)
            p99_index = int(len(samples) * 0.99)

            return BenchmarkResult(
                name=name,
                mean=mean,
                median=median,
                std_dev=std_dev,
                min=min(samples),
                max=max(samples),
                p95=samples[p95_index] if p95_index < len(samples) else max(samples),
                p99=samples[p99_index] if p99_index < len(samples) else max(samples),
                iterations=self.benchmark_iterations,
                samples=samples,
            )

        finally:
            self._restore_environment()


async def measure_async_performance(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    iterations: int = 100,
    warmup: int = 5,
    name: str = "Performance Test",
    **kwargs: Any,
) -> BenchmarkResult:
    """Convenience function for quick async performance measurements.

    Args:
        func: Async function to measure
        *args: Positional arguments for the function
        iterations: Number of measurement iterations
        warmup: Number of warmup iterations
        name: Name for the measurement
        **kwargs: Keyword arguments for the function

    Returns:
        BenchmarkResult with statistical analysis
    """
    benchmark = PerformanceBenchmark(
        warmup_iterations=warmup,
        benchmark_iterations=iterations,
    )
    return await benchmark.benchmark_async(func, *args, name=name, **kwargs)


def measure_sync_performance(
    func: Callable[..., Any],
    *args: Any,
    iterations: int = 100,
    warmup: int = 5,
    name: str = "Performance Test",
    **kwargs: Any,
) -> BenchmarkResult:
    """Convenience function for quick synchronous performance measurements.

    Args:
        func: Function to measure
        *args: Positional arguments for the function
        iterations: Number of measurement iterations
        warmup: Number of warmup iterations
        name: Name for the measurement
        **kwargs: Keyword arguments for the function

    Returns:
        BenchmarkResult with statistical analysis
    """
    benchmark = PerformanceBenchmark(
        warmup_iterations=warmup,
        benchmark_iterations=iterations,
    )
    return benchmark.benchmark_sync(func, *args, name=name, **kwargs)
