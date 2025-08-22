"""Debug test to investigate mock application in CI environment."""
# ruff: noqa: PLC0415

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest


def test_debug_environment_info():
    """Display environment information."""
    print("\n=== ENVIRONMENT DEBUG ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}")
    print(f"Python path: {sys.path[:3]}...")  # First 3 entries


def test_debug_module_import():
    """Debug module import and function location."""
    print("\n=== MODULE IMPORT DEBUG ===")

    # Import before patch
    from wassden.clis.experiment import _run_experiment_async

    print(f"Function before patch: {_run_experiment_async}")
    print(f"Function ID before patch: {id(_run_experiment_async)}")
    print(f"Function module: {_run_experiment_async.__module__}")
    print(f"Function file: {_run_experiment_async.__code__.co_filename}")

    # Test patch application
    with patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock) as mock:
        print(f"Mock object: {mock}")
        print(f"Mock ID: {id(mock)}")

        # Re-import to check if patched
        import importlib

        import wassden.clis.experiment

        importlib.reload(wassden.clis.experiment)

        from wassden.clis.experiment import _run_experiment_async as func_after_patch

        print(f"Function after patch: {func_after_patch}")
        print(f"Function ID after patch: {id(func_after_patch)}")
        print(f"Is function same as mock? {func_after_patch is mock}")
        print(f"Are IDs equal? {id(func_after_patch) == id(mock)}")


def test_debug_patch_timing():
    """Test different patch timing strategies."""
    print("\n=== PATCH TIMING DEBUG ===")

    # Strategy 1: Patch before import
    with patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock) as mock1:
        from wassden.clis.experiment import _run_experiment_async as func1

        result1 = func1 is mock1
        print(f"Strategy 1 (patch before import): {result1}")

    # Strategy 2: Import then patch

    with patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock) as mock2:
        from wassden.clis.experiment import _run_experiment_async as func2

        result2 = func2 is mock2
        print(f"Strategy 2 (import then patch): {result2}")

    # Strategy 3: Patch module attribute directly
    import wassden.clis.experiment

    original_func = wassden.clis.experiment._run_experiment_async
    mock3 = AsyncMock()
    wassden.clis.experiment._run_experiment_async = mock3

    from wassden.clis.experiment import _run_experiment_async as func3

    result3 = func3 is mock3
    print(f"Strategy 3 (direct attribute patch): {result3}")

    # Restore original
    wassden.clis.experiment._run_experiment_async = original_func


@pytest.mark.asyncio
async def test_debug_actual_test_scenario():
    """Replicate the actual failing test scenario with debug info."""
    print("\n=== ACTUAL TEST SCENARIO DEBUG ===")

    from datetime import datetime

    from wassden.lib.experiment import (
        ExperimentConfig,
        ExperimentResult,
        ExperimentStatus,
        ExperimentType,
    )

    # Create mock result
    mock_result = ExperimentResult(
        experiment_id="debug-test-123",
        timestamp=datetime.now(),
        config=ExperimentConfig(
            experiment_type=ExperimentType.PERFORMANCE,
            timeout_seconds=300,
            memory_limit_mb=256,
        ),
        status=ExperimentStatus.COMPLETED,
        duration_seconds=45.7,
    )

    # Apply patch
    with patch("wassden.clis.experiment.run_experiment", return_value=mock_result) as mock_run_exp:
        print(f"Applied patch to run_experiment: {mock_run_exp}")

        # Import and call function
        from wassden.clis.experiment import _run_experiment_async

        print(f"Calling _run_experiment_async: {_run_experiment_async}")

        try:
            result = await _run_experiment_async(
                experiment_type=ExperimentType.PERFORMANCE,
                output_format=None,
                timeout=300,
                memory_limit=256,
                config_path=Path("/tmp/debug_test"),
            )

            print(f"Result experiment_id: {result.experiment_id}")
            print("Expected: debug-test-123")
            print(f"Match: {result.experiment_id == 'debug-test-123'}")
            print(f"Mock called: {mock_run_exp.called}")
            print(f"Mock call count: {mock_run_exp.call_count}")

        except Exception as e:
            print(f"Exception occurred: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_debug_environment_info()
    test_debug_module_import()
    test_debug_patch_timing()
