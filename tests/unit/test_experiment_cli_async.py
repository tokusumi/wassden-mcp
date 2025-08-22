"""Async tests for experiment CLI async implementations.

Tests the actual async implementations directly following pytest-asyncio v1.0+ best practices.
This demonstrates proper async testing without mocking asyncio.run().
"""

import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from wassden.clis.experiment import (
    _compare_experiments_async,
    _measure_ears_coverage_async,
    _measure_performance_async,
    _run_experiment_async,
    _run_experiment_cmd_async,
)
from wassden.lib.experiment import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType,
    OutputFormat,
)
from wassden.types import Language

pytestmark = pytest.mark.dev


@pytest.mark.dev
class TestExperimentAsyncImplementations:
    """Test async implementations directly using proper async testing patterns."""

    @pytest.mark.asyncio
    @patch("wassden.clis.experiment.run_experiment")
    async def test_run_experiment_async_implementation(self, mock_run_experiment, tmp_path):
        """Test _run_experiment_async directly with real async behavior."""
        # Setup mock result
        mock_result = ExperimentResult(
            experiment_id="async-test-123",
            timestamp=datetime.now(),
            config=ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=256,
                output_format=[OutputFormat.JSON],
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=45.7,
        )

        # Mock the underlying async function
        mock_run_experiment.return_value = mock_result

        # Test the async implementation directly
        result = await _run_experiment_async(
            experiment_type=ExperimentType.PERFORMANCE,
            output_format=[OutputFormat.JSON],
            timeout=300,
            memory_limit=256,
            config_path=tmp_path / "test_config",
        )

        # Verify result
        assert result.experiment_id == "async-test-123"
        assert result.status == ExperimentStatus.COMPLETED
        assert result.duration_seconds == 45.7

        # Verify the underlying function was called correctly
        mock_run_experiment.assert_called_once()
        call_kwargs = mock_run_experiment.call_args.kwargs
        assert call_kwargs["experiment_type"] == ExperimentType.PERFORMANCE
        assert call_kwargs["timeout_seconds"] == 300
        assert call_kwargs["memory_limit_mb"] == 256
        assert call_kwargs["config_path"] == tmp_path / "test_config"

    @pytest.mark.asyncio
    @patch("wassden.clis.experiment.run_experiment")
    async def test_run_experiment_cmd_async_implementation(self, mock_run_experiment, tmp_path):
        """Test _run_experiment_cmd_async directly with real async behavior."""
        # Setup mock result
        mock_result = ExperimentResult(
            experiment_id="cmd-async-test",
            timestamp=datetime.now(),
            config=ExperimentConfig(
                experiment_type=ExperimentType.EARS_COVERAGE,
                timeout_seconds=600,
                memory_limit_mb=128,
                output_format=[OutputFormat.JSON],
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=120.5,
        )

        mock_run_experiment.return_value = mock_result

        # Test parameters
        parsed_params = {"test_param": "value"}
        output_format = [OutputFormat.JSON]

        # Test the async implementation directly
        result = await _run_experiment_cmd_async(
            experiment_type=ExperimentType.EARS_COVERAGE,
            parsed_params=parsed_params,
            output_format=output_format,
            timeout=600,
            memory_limit=128,
            config_path=tmp_path / "test_config",
        )

        # Verify result
        assert result.experiment_id == "cmd-async-test"
        assert result.status == ExperimentStatus.COMPLETED

        # Verify the underlying function was called correctly
        mock_run_experiment.assert_called_once()
        call_kwargs = mock_run_experiment.call_args.kwargs
        assert call_kwargs["experiment_type"] == ExperimentType.EARS_COVERAGE
        assert call_kwargs["parameters"] == parsed_params
        assert call_kwargs["output_format"] == output_format
        assert call_kwargs["config_path"] == tmp_path / "test_config"

    @pytest.mark.asyncio
    @patch("wassden.clis.experiment.measure_ears_coverage")
    async def test_measure_ears_coverage_async_implementation(self, mock_measure_ears):
        """Test _measure_ears_coverage_async directly with real async behavior."""

        # Setup mock report
        mock_report = type("MockReport", (), {"total_requirements": 10, "ears_compliant": 8, "coverage_rate": 80.0})()

        mock_measure_ears.return_value = mock_report

        # Test parameters
        input_paths = [Path("test1.md"), Path("test2.md")]
        language = Language.ENGLISH
        detail_level = "summary"

        # Test the async implementation directly
        result = await _measure_ears_coverage_async(
            input_paths=input_paths,
            language=language,
            detail_level=detail_level,
        )

        # Verify result
        assert result.total_requirements == 10
        assert result.ears_compliant == 8
        assert result.coverage_rate == 80.0

        # Verify the underlying function was called correctly
        mock_measure_ears.assert_called_once()
        call_kwargs = mock_measure_ears.call_args.kwargs
        assert call_kwargs["input_paths"] == input_paths
        assert call_kwargs["_language"] == language
        assert call_kwargs["_output_detail_level"] == detail_level

    @pytest.mark.asyncio
    @patch("wassden.clis.experiment.measure_performance")
    async def test_measure_performance_async_implementation(self, mock_measure_perf):
        """Test _measure_performance_async directly with real async behavior."""
        # Setup mock report
        mock_report = type(
            "MockReport",
            (),
            {
                "total_executions": 100,
                "successful_executions": 98,
                "average_wall_time_ms": 15.5,
                "average_cpu_time_ms": 12.3,
                "average_memory_mb": 64.2,
            },
        )()

        mock_measure_perf.return_value = mock_report

        # Test parameters
        operation_name = "test_operation"
        rounds = 10
        warmup = 3
        memory_profiling = True

        # Test the async implementation directly
        result = await _measure_performance_async(
            operation_name=operation_name,
            rounds=rounds,
            warmup=warmup,
            memory_profiling=memory_profiling,
        )

        # Verify result
        assert result.total_executions == 100
        assert result.successful_executions == 98
        assert result.average_wall_time_ms == 15.5
        assert result.average_memory_mb == 64.2

        # Verify the underlying function was called correctly
        mock_measure_perf.assert_called_once()
        call_kwargs = mock_measure_perf.call_args.kwargs
        assert call_kwargs["operation_name"] == operation_name
        assert call_kwargs["measurement_rounds"] == rounds
        assert call_kwargs["warmup_rounds"] == warmup
        assert call_kwargs["memory_profiling"] == memory_profiling

    @pytest.mark.asyncio
    @patch("wassden.clis.experiment.run_experiment")
    async def test_compare_experiments_async_implementation(self, mock_run_experiment, tmp_path):
        """Test _compare_experiments_async directly with real async behavior."""
        # Setup mock result
        mock_result = ExperimentResult(
            experiment_id="compare-async-test",
            timestamp=datetime.now(),
            config=ExperimentConfig(
                experiment_type=ExperimentType.COMPARATIVE,
                timeout_seconds=600,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=200.0,
            metadata={
                "total_comparisons": 5,
                "significant_differences": 2,
                "formatted_outputs": {"json": "comparison_data"},
            },
        )

        mock_run_experiment.return_value = mock_result

        # Test parameters
        baseline_id = "baseline-exp-1"
        comparison_ids = ["comp-exp-1", "comp-exp-2"]
        metrics = ["performance", "memory"]
        output_format = OutputFormat.JSON

        # Test the async implementation directly
        result = await _compare_experiments_async(
            baseline_id=baseline_id,
            comparison_ids=comparison_ids,
            metrics=metrics,
            output_format=output_format,
            config_path=tmp_path / "test_config",
        )

        # Verify result
        assert result.experiment_id == "compare-async-test"
        assert result.status == ExperimentStatus.COMPLETED
        assert result.metadata["total_comparisons"] == 5
        assert result.metadata["significant_differences"] == 2

        # Verify the underlying function was called correctly
        mock_run_experiment.assert_called_once()
        call_kwargs = mock_run_experiment.call_args.kwargs
        assert call_kwargs["experiment_type"] == ExperimentType.COMPARATIVE
        assert call_kwargs["output_format"] == [output_format]

        # Verify parameters were constructed correctly
        parameters = call_kwargs["parameters"]
        assert parameters["baseline_experiment_id"] == baseline_id
        assert parameters["comparison_experiment_ids"] == comparison_ids
        assert parameters["metrics_to_compare"] == metrics

    @pytest.mark.asyncio
    async def test_concurrent_async_operations(self, tmp_path):
        """Test multiple async operations running concurrently."""
        with patch("wassden.clis.experiment.run_experiment") as mock_run_experiment:
            # Setup different mock results for concurrent operations
            mock_results = [
                ExperimentResult(
                    experiment_id=f"concurrent-{i}",
                    timestamp=datetime.now(),
                    config=ExperimentConfig(
                        experiment_type=ExperimentType.PERFORMANCE,
                        timeout_seconds=300,
                        memory_limit_mb=100,
                    ),
                    status=ExperimentStatus.COMPLETED,
                    duration_seconds=10.0 + i,
                )
                for i in range(3)
            ]

            mock_run_experiment.side_effect = mock_results

            # Run multiple async operations concurrently
            tasks = [
                _run_experiment_async(
                    experiment_type=ExperimentType.PERFORMANCE,
                    output_format=[OutputFormat.JSON],
                    timeout=300,
                    memory_limit=100,
                    config_path=tmp_path / f"config_{i}",
                )
                for i in range(3)
            ]

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Verify all tasks completed successfully
            assert len(results) == 3
            for i, result in enumerate(results):
                assert not isinstance(result, Exception)
                assert result.experiment_id == f"concurrent-{i}"
                assert result.status == ExperimentStatus.COMPLETED
                assert result.duration_seconds == 10.0 + i

            # Verify all calls were made
            assert mock_run_experiment.call_count == 3

    @pytest.mark.asyncio
    async def test_timeout_behavior_with_async_implementation(self, tmp_path):
        """Test timeout behavior with async implementations."""
        with patch("wassden.clis.experiment.run_experiment") as mock_run_experiment:
            # Create a slow async operation
            async def slow_operation(*_args, **_kwargs):
                await asyncio.sleep(1.0)
                return ExperimentResult(
                    experiment_id="timeout-test",
                    timestamp=datetime.now(),
                    config=ExperimentConfig(
                        experiment_type=ExperimentType.PERFORMANCE,
                        timeout_seconds=300,
                        memory_limit_mb=100,
                    ),
                    status=ExperimentStatus.COMPLETED,
                    duration_seconds=1.0,
                )

            mock_run_experiment.side_effect = slow_operation

            # Test that timeout is properly raised
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    _run_experiment_async(
                        experiment_type=ExperimentType.PERFORMANCE,
                        output_format=[OutputFormat.JSON],
                        timeout=300,
                        memory_limit=100,
                        config_path=tmp_path / "timeout_config",
                    ),
                    timeout=0.1,  # Very short timeout
                )
