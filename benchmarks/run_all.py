#!/usr/bin/env python
"""Standalone performance benchmark script for reproducible measurements."""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pathlib import Path

from wassden.handlers import (
    handle_analyze_changes,
    handle_check_completeness,
    handle_get_traceability,
    handle_prompt_requirements,
)
from wassden.language_types import Language
from wassden.types import SpecDocuments
from wassden.utils.benchmark import PerformanceBenchmark


async def benchmark_all_handlers():
    """Run comprehensive benchmarks on all MCP handlers."""
    benchmark = PerformanceBenchmark(
        warmup_iterations=5,
        benchmark_iterations=50,
        gc_collect_interval=10,
        cpu_affinity=True,  # Pin to CPU for consistency
    )

    results = {}

    # Benchmark check_completeness
    print("Benchmarking check_completeness...")
    result = await benchmark.benchmark_async(
        handle_check_completeness,
        {"userInput": "Performance test project"},
        name="check_completeness",
    )
    results["check_completeness"] = {
        "mean_ms": result.mean * 1000,
        "median_ms": result.median * 1000,
        "p95_ms": result.p95 * 1000,
        "p99_ms": result.p99 * 1000,
        "std_dev_ms": result.std_dev * 1000,
    }
    print(result)

    # Benchmark analyze_changes
    print("\nBenchmarking analyze_changes...")
    result = await benchmark.benchmark_async(
        handle_analyze_changes,
        {"changedFile": "specs/requirements.md", "changeDescription": "Performance test change"},
        name="analyze_changes",
    )
    results["analyze_changes"] = {
        "mean_ms": result.mean * 1000,
        "median_ms": result.median * 1000,
        "p95_ms": result.p95 * 1000,
        "p99_ms": result.p99 * 1000,
        "std_dev_ms": result.std_dev * 1000,
    }
    print(result)

    # Benchmark get_traceability
    print("\nBenchmarking get_traceability...")
    result = await benchmark.benchmark_async(
        handle_get_traceability,
        {},
        name="get_traceability",
    )
    results["get_traceability"] = {
        "mean_ms": result.mean * 1000,
        "median_ms": result.median * 1000,
        "p95_ms": result.p95 * 1000,
        "p99_ms": result.p99 * 1000,
        "std_dev_ms": result.std_dev * 1000,
    }
    print(result)

    # Benchmark prompt_requirements
    print("\nBenchmarking prompt_requirements...")

    # Create SpecDocuments for benchmarking
    specs = SpecDocuments(
        requirements_path=Path("specs/requirements.md"),
        design_path=Path("specs/design.md"),
        tasks_path=Path("specs/tasks.md"),
        language=Language.JAPANESE,
    )

    result = await benchmark.benchmark_async(
        handle_prompt_requirements,
        specs=specs,
        project_description="Test project",
        scope="Limited scope",
        constraints="Python constraints",
        name="prompt_requirements",
    )
    results["prompt_requirements"] = {
        "mean_ms": result.mean * 1000,
        "median_ms": result.median * 1000,
        "p95_ms": result.p95 * 1000,
        "p99_ms": result.p99 * 1000,
        "std_dev_ms": result.std_dev * 1000,
    }
    print(result)

    # Benchmark concurrent execution
    print("\nBenchmarking concurrent execution...")

    async def concurrent_test():
        tasks = []
        for i in range(10):
            tasks.append(handle_check_completeness({"userInput": f"Concurrent test {i}"}))
            tasks.append(handle_analyze_changes({"changedFile": f"test{i}.md", "changeDescription": f"Change {i}"}))
        return await asyncio.gather(*tasks)

    result = await benchmark.benchmark_async(
        concurrent_test,
        name="concurrent_20_tools",
    )
    results["concurrent_20_tools"] = {
        "mean_ms": result.mean * 1000,
        "median_ms": result.median * 1000,
        "p95_ms": result.p95 * 1000,
        "p99_ms": result.p99 * 1000,
        "std_dev_ms": result.std_dev * 1000,
    }
    print(result)

    # Save results to JSON
    output_file = Path(__file__).parent / "results.json"
    with output_file.open("w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to {output_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    for handler, metrics in results.items():
        print(f"\n{handler}:")
        print(f"  Median: {metrics['median_ms']:.3f}ms")
        print(f"  P95: {metrics['p95_ms']:.3f}ms")
        print(f"  Std Dev: {metrics['std_dev_ms']:.3f}ms")

    # Check if performance meets <0.01ms target for simple operations
    performance_target_ms = 10.0
    fast_handlers = ["check_completeness", "analyze_changes", "get_traceability"]
    all_fast = all(results[h]["median_ms"] < performance_target_ms for h in fast_handlers if h in results)

    if all_fast:
        print(f"\n✅ All handlers meet <{performance_target_ms}ms median response time target!")
    else:
        print(f"\n⚠️ Some handlers exceed {performance_target_ms}ms median response time target")
        for h in fast_handlers:
            if h in results and results[h]["median_ms"] >= performance_target_ms:
                print(f"  - {h}: {results[h]['median_ms']:.3f}ms")


if __name__ == "__main__":
    print("Starting performance benchmarks...")
    print("This will take a few minutes to ensure statistical accuracy.\n")
    asyncio.run(benchmark_all_handlers())
