"""Concurrent and timeout testing patterns for experiment CLI module.

Demonstrates pytest-asyncio v1.0+ best practices for:
- Multiple experiment execution testing
- Timeout behavior validation
- Exception handling in concurrent-like scenarios
- Proper async patterns without complex threading
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from wassden.clis.experiment import experiment_app
from wassden.lib.experiment import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType,
)


class TestExperimentCLIConcurrentPatterns:
    """Test multiple experiment execution and error handling patterns."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock)
    def test_multiple_experiment_execution(self, mock_run_experiment_async):
        """Test multiple experiment execution patterns."""
        # Mock multiple experiment results
        results = [
            ExperimentResult(
                experiment_id=f"multi-exp-{i}",
                timestamp=datetime.now(),
                config=ExperimentConfig(
                    experiment_type=ExperimentType.PERFORMANCE,
                    timeout_seconds=300,
                    memory_limit_mb=128,
                ),
                status=ExperimentStatus.COMPLETED,
                duration_seconds=45.0 + i,
            )
            for i in range(3)
        ]

        # Mock async implementation to return results sequentially
        mock_run_experiment_async.side_effect = results

        # Run multiple experiments
        experiment_results = []
        for _i in range(3):
            result = self.runner.invoke(experiment_app, ["run", "performance", "--timeout", "300", "--memory", "128"])
            experiment_results.append(result)

        # Verify all experiments completed successfully
        for result in experiment_results:
            assert result.exit_code == 0
            assert "Experiment completed successfully" in result.output

        # Verify async implementation was called multiple times
        assert mock_run_experiment_async.call_count == 3

    @patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock)
    def test_experiment_failure_handling(self, mock_run_experiment_async):
        """Test experiment failure handling patterns."""
        # Mock one success and one failure
        success_result = ExperimentResult(
            experiment_id="success-exp",
            timestamp=datetime.now(),
            config=ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=100,
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=1.0,
        )

        # First call succeeds, second fails
        mock_run_experiment_async.side_effect = [success_result, Exception("Experiment failed")]

        # Run successful experiment
        success_result = self.runner.invoke(experiment_app, ["run", "performance"])
        assert success_result.exit_code == 0
        assert "Experiment completed successfully" in success_result.output

        # Run failing experiment
        failure_result = self.runner.invoke(experiment_app, ["run", "performance"])
        assert failure_result.exit_code == 1
        assert "Experiment failed: Experiment failed" in failure_result.output

        # Verify both calls were made
        assert mock_run_experiment_async.call_count == 2

    @pytest.mark.asyncio(loop_scope="function")
    async def test_async_context_simulation(self):
        """Test async context behavior simulation."""

        # Create a simple async function to test patterns
        async def simulate_experiment_task():
            """Simulate an experiment task."""
            await asyncio.sleep(0.01)  # Very short delay
            return {"experiment_id": "async-test", "status": "completed", "duration": 0.01}

        # Test asyncio.gather pattern for multiple tasks
        tasks = [simulate_experiment_task() for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all tasks completed
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
            assert result["status"] == "completed"

    @pytest.mark.asyncio(loop_scope="function")
    async def test_timeout_pattern_simulation(self):
        """Test timeout behavior patterns with asyncio.wait_for."""

        # Simulate a long-running task
        async def slow_task():
            await asyncio.sleep(1.0)
            return "completed"

        # Test that timeout is properly raised
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(slow_task(), timeout=0.1)

    @pytest.mark.asyncio(loop_scope="function")
    async def test_event_based_coordination(self):
        """Test event-based task coordination patterns."""
        # Create coordination events
        start_event = asyncio.Event()
        completion_events = [asyncio.Event() for _ in range(2)]

        async def coordinated_task(task_id):
            """Task that waits for coordination."""
            await start_event.wait()  # Wait for start signal
            await asyncio.sleep(0.01)  # Simulate work
            completion_events[task_id].set()  # Signal completion
            return f"task-{task_id}-completed"

        # Start tasks
        tasks = [asyncio.create_task(coordinated_task(0)), asyncio.create_task(coordinated_task(1))]

        # Brief delay to let tasks start waiting
        await asyncio.sleep(0.01)

        # Signal all tasks to start
        start_event.set()

        # Wait for completion
        results = await asyncio.gather(*tasks)

        # Verify coordination worked
        assert len(results) == 2
        assert all("completed" in result for result in results)
        assert all(event.is_set() for event in completion_events)
