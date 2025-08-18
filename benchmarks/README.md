# Performance Benchmarks

Reproducible benchmark tools for wassden performance measurement.

## 🚀 Quick Start

```bash
# Run comprehensive benchmarks
python benchmarks/run_all.py

# Run performance tests
pytest tests/e2e/test_mcp_server.py::TestMCPServerPerformance -v
```

## 📊 Current Results

| Handler | Median | P95 |
|---------|--------|-----|
| check_completeness | 0.003ms | 0.014ms |
| analyze_changes | 0.013ms | 0.032ms |
| get_traceability | 0.013ms | 0.090ms |
| prompt_requirements | 0.001ms | 0.002ms |
| concurrent_20_tools | 0.11ms | 0.15ms |

**Target**: <10ms median ✅ All achieved

## 🔧 Custom Benchmarks

```python
from wassden.utils.benchmark import PerformanceBenchmark

benchmark = PerformanceBenchmark(
    warmup_iterations=5,
    benchmark_iterations=50,
)

result = await benchmark.benchmark_async(my_func, name="test")
print(result)
```

## 📚 Documentation

- 📊 [Performance Analysis](../docs/performance.md) - Detailed technical guide
- 🧪 [Test Coverage](../README.md#performance-metrics) - Performance overview