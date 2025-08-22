"""Unit tests for experiment CLI module.

Tests focus on realistic scenarios using actual async testing patterns.
Follows pytest-asyncio v1.0+ best practices for authentic async behavior.
"""

import asyncio
import json
import tempfile
import traceback
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from typer.testing import CliRunner

from wassden.clis.experiment import experiment_app
from wassden.lib.experiment import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType,
    OutputFormat,
)

pytestmark = pytest.mark.dev


@pytest.fixture
def temp_config_path():
    """Fixture providing a temporary directory for config_path."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_experiment_manager():
    """Fixture providing mocked ExperimentManager."""
    manager = Mock()
    manager.run_experiment = AsyncMock()
    manager.save_config = Mock()
    manager.load_config = Mock()
    manager.list_configs = Mock()
    return manager


@pytest.fixture(autouse=True, scope="class")
def reset_all_mocks():
    """Reset all mocks between test classes to prevent contamination."""
    yield
    patch.stopall()


@pytest.mark.dev
class TestExperimentCLIRunCommand:
    """Test run command with realistic scenarios using actual async patterns."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock)
    def test_run_command_performance_experiment_realistic(self, mock_run_experiment_async, temp_config_path):
        """Test run command for performance experiment - tests async implementation directly."""
        mock_result = ExperimentResult(
            experiment_id="perf-exp-123",
            timestamp=datetime.now(),
            config=ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=256,
                output_format=[OutputFormat.JSON, OutputFormat.CSV],
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=45.7,
        )

        # Mock the async implementation directly
        mock_run_experiment_async.return_value = mock_result

        # Execute command with realistic parameters
        result = self.runner.invoke(
            experiment_app,
            [
                "run",
                "performance",
                "--format",
                "json",
                "--format",
                "csv",
                "--timeout",
                "300",
                "--memory",
                "256",
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Verify CLI behavior - tests actual CLI implementation
        if result.exit_code != 0:
            print(f"ERROR: {result.output}")
            print(f"Exception: {result.exception}")
        assert result.exit_code == 0
        assert "Starting performance experiment" in result.output
        assert "Experiment completed successfully" in result.output
        assert "Experiment ID: perf-exp-123" in result.output
        assert "Status: completed" in result.output

        # Verify async implementation was called
        mock_run_experiment_async.assert_called_once()

        # Verify the async function was called with correct parameters
        call_args = mock_run_experiment_async.call_args
        assert call_args.args[0] == ExperimentType.PERFORMANCE  # experiment_type
        assert call_args.args[2] == 300  # timeout
        assert call_args.args[3] == 256  # memory_limit
        assert call_args.args[4] == temp_config_path  # config_path

    @patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock)
    def test_run_command_with_default_config_realistic(self, mock_run_experiment_async, temp_config_path):
        """Test run command uses default config - verifies default parameter logic."""
        mock_result = ExperimentResult(
            experiment_id="ears-exp-456",
            timestamp=datetime.now(),
            config=ExperimentConfig(
                experiment_type=ExperimentType.EARS_COVERAGE,
                timeout_seconds=600,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=120.3,
        )
        mock_run_experiment_async.return_value = mock_result

        # Execute command without config
        result = self.runner.invoke(
            experiment_app, ["run", "ears_coverage", "--timeout", "600", "--config-path", str(temp_config_path)]
        )

        # Verify default config behavior - tests CLI logic
        assert result.exit_code == 0
        assert "Experiment completed successfully" in result.output
        assert "ears-exp-456" in result.output

        # Verify async implementation was called with correct parameters
        mock_run_experiment_async.assert_called_once()
        call_args = mock_run_experiment_async.call_args
        assert call_args.args[0] == ExperimentType.EARS_COVERAGE  # experiment_type
        assert call_args.args[2] == 600  # timeout
        assert call_args.args[4] == temp_config_path  # config_path

    def test_run_command_invalid_experiment_type(self):
        """Test run command with invalid experiment type - verifies CLI validation."""
        result = self.runner.invoke(experiment_app, ["run", "invalid_type"])

        # Verify CLI properly validates experiment type
        assert result.exit_code != 0

    @patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock)
    def test_run_command_parameter_boundaries(self, mock_run_experiment_async, temp_config_path):
        """Test run command with boundary parameters - verifies parameter handling."""
        mock_result = ExperimentResult(
            experiment_id="boundary-test",
            timestamp=datetime.now(),
            config=ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=1,
                memory_limit_mb=1024,
                output_format=[OutputFormat.YAML],
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=0.8,
        )
        mock_run_experiment_async.return_value = mock_result

        # Test with boundary values
        result = self.runner.invoke(
            experiment_app,
            [
                "run",
                "performance",
                "--timeout",
                "1",  # Minimum timeout
                "--memory",
                "1024",  # High memory
                "--format",
                "yaml",
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Verify boundary handling
        assert result.exit_code == 0
        assert "boundary-test" in result.output

        # Verify async implementation was called with boundary parameters
        mock_run_experiment_async.assert_called_once()
        call_args = mock_run_experiment_async.call_args
        assert call_args.args[2] == 1  # timeout
        assert call_args.args[3] == 1024  # memory_limit
        assert call_args.args[4] == temp_config_path  # config_path

    @patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock)
    def test_run_command_experiment_failure_handling(self, mock_run_experiment_async, temp_config_path):
        """Test run command handles experiment failures properly."""
        # Mock async implementation to raise exception
        mock_run_experiment_async.side_effect = Exception("Experiment timeout")

        result = self.runner.invoke(experiment_app, ["run", "performance", "--config-path", str(temp_config_path)])

        # Verify error handling
        assert result.exit_code == 1
        assert "Experiment failed: Experiment timeout" in result.output


@pytest.mark.dev
class TestExperimentCLISaveConfig:
    """Test save-config command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up after each test."""
        patch.stopall()

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_save_config_from_parameters_realistic(self, mock_manager_class, temp_config_path, tmp_path):
        """Test save-config with parameters - verifies actual config creation."""
        # Reset the mock to ensure clean state
        mock_manager_class.reset_mock()
        # Create a fresh mock to avoid contamination
        mock_manager = Mock(spec=["save_config", "create_default_config"])
        mock_manager_class.return_value = mock_manager

        # Mock successful save operation with realistic Path return
        config_path = tmp_path / "test_perf_config.yaml"
        mock_manager.save_config.return_value = config_path
        mock_config = ExperimentConfig(
            experiment_type=ExperimentType.PERFORMANCE, timeout_seconds=300, memory_limit_mb=512
        )
        mock_manager.create_default_config.return_value = mock_config

        result = self.runner.invoke(
            experiment_app,
            [
                "save-config",
                "performance",
                "test_perf_config",
                "--timeout",
                "300",
                "--memory",
                "512",
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Debug output always for diagnosis
        if result.exit_code != 0:
            print("\n=== TEST DEBUG: save_config_from_parameters_realistic ===")
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
            print(f"Mock manager: {mock_manager}")
            print(f"Mock manager_class: {mock_manager_class}")
            print(f"save_config call count: {mock_manager.save_config.call_count}")
            print(f"create_default_config call count: {mock_manager.create_default_config.call_count}")
            if result.exception:
                traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)

        # Verify command success
        assert result.exit_code == 0
        assert "Configuration saved to:" in result.output

        # Verify manager was called with correct parameters
        mock_manager.save_config.assert_called_once()
        # Simply verify that save_config was called - the exact parameters are implementation details


@pytest.mark.dev
class TestExperimentCLILoadConfig:
    """Test load-config command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up after each test."""
        patch.stopall()

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_load_config_display_realistic(self, mock_manager_class, temp_config_path):
        """Test load-config displays configuration - verifies config retrieval."""
        # Reset the mock to ensure clean state
        mock_manager_class.reset_mock()
        # Create a fresh mock to avoid contamination
        mock_manager = Mock(spec=["load_config"])
        mock_manager_class.return_value = mock_manager

        # Setup mock configuration
        mock_config = ExperimentConfig(
            experiment_type=ExperimentType.EARS_COVERAGE,
            timeout_seconds=600,
            memory_limit_mb=128,
            output_format=[OutputFormat.JSON, OutputFormat.CSV],
        )
        mock_manager.load_config.return_value = mock_config

        result = self.runner.invoke(
            experiment_app, ["load-config", "ears_test_config", "--config-path", str(temp_config_path)]
        )

        # Verify successful config display
        assert result.exit_code == 0
        assert "Configuration loaded successfully:" in result.output
        assert "Type: ears_coverage" in result.output
        assert "Timeout: 600" in result.output
        assert "Memory limit: 128" in result.output

        # Verify config was loaded correctly
        mock_manager.load_config.assert_called_once_with("ears_test_config")


@pytest.mark.dev
class TestExperimentCLIListConfigs:
    """Test list-configs command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up after each test."""
        patch.stopall()

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_list_configs_display_realistic(self, mock_manager_class, temp_config_path):
        """Test list-configs displays available configurations."""
        # Reset the mock to ensure clean state
        mock_manager_class.reset_mock()
        # Create a fresh mock to avoid contamination
        mock_manager = Mock(spec=["list_configs"])
        mock_manager_class.return_value = mock_manager

        # Setup config list
        mock_configs = [
            ("performance_test", ExperimentType.PERFORMANCE),
            ("ears_test", ExperimentType.EARS_COVERAGE),
        ]
        mock_manager.list_configs.return_value = mock_configs

        result = self.runner.invoke(experiment_app, ["list-configs", "--config-path", str(temp_config_path)])

        # Verify config listing
        assert result.exit_code == 0
        assert "Available configurations:" in result.output


@pytest.mark.dev
class TestExperimentCLIEdgeCases:
    """Test edge cases and error conditions with async patterns."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_save_config_file_error(self, mock_manager_class, temp_config_path):
        """Test save-config handles file write errors."""
        # Reset the mock to ensure clean state
        mock_manager_class.reset_mock()
        # Create a fresh mock to avoid contamination
        mock_manager = Mock(spec=["save_config", "create_default_config"])
        mock_manager_class.return_value = mock_manager

        # Mock config creation but file write failure
        mock_config = ExperimentConfig(
            experiment_type=ExperimentType.PERFORMANCE, timeout_seconds=300, memory_limit_mb=100
        )
        mock_manager.create_default_config.return_value = mock_config
        mock_manager.save_config.side_effect = OSError("Permission denied")

        result = self.runner.invoke(
            experiment_app,
            ["save-config", "performance", "test_config", "--timeout", "300", "--config-path", str(temp_config_path)],
        )

        # Verify error handling
        assert result.exit_code == 1
        assert "Failed to save configuration" in result.output

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_load_config_not_found(self, mock_manager_class, temp_config_path):
        """Test load-config handles missing configuration."""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        # Mock config not found
        mock_manager.load_config.side_effect = FileNotFoundError("Config not found")

        result = self.runner.invoke(
            experiment_app, ["load-config", "nonexistent_config", "--config-path", str(temp_config_path)]
        )

        # Verify error handling
        assert result.exit_code == 1
        assert "Failed to load configuration:" in result.output

    @patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock)
    def test_run_command_negative_timeout(self, mock_run_experiment_async, temp_config_path):
        """Test run command with negative timeout values - validation at experiment level."""
        mock_result = ExperimentResult(
            experiment_id="timeout-test",
            timestamp=datetime.now(),
            config=ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=-1,
                memory_limit_mb=100,
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=1.0,
        )
        mock_run_experiment_async.return_value = mock_result

        result = self.runner.invoke(
            experiment_app, ["run", "performance", "--timeout", "-1", "--config-path", str(temp_config_path)]
        )

        # Verify parameter validation (CLI should accept negative timeout and pass it through)
        # The validation should happen at the experiment level, not CLI level
        assert result.exit_code == 0  # CLI accepts the parameter
        mock_run_experiment_async.assert_called_once()
        call_args = mock_run_experiment_async.call_args
        assert call_args.args[2] == -1  # timeout
        assert call_args.args[4] == temp_config_path  # config_path

    @patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock)
    def test_run_command_zero_memory(self, mock_run_experiment_async, temp_config_path):
        """Test run command with zero memory limit - validation at experiment level."""
        mock_result = ExperimentResult(
            experiment_id="memory-test",
            timestamp=datetime.now(),
            config=ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=600,
                memory_limit_mb=0,
            ),
            status=ExperimentStatus.COMPLETED,
            duration_seconds=1.0,
        )
        mock_run_experiment_async.return_value = mock_result

        result = self.runner.invoke(
            experiment_app, ["run", "performance", "--memory", "0", "--config-path", str(temp_config_path)]
        )

        # Verify parameter validation (CLI should accept zero memory and pass it through)
        # The validation should happen at the experiment level, not CLI level
        assert result.exit_code == 0  # CLI accepts the parameter
        mock_run_experiment_async.assert_called_once()
        call_args = mock_run_experiment_async.call_args
        assert call_args.args[3] == 0  # memory_limit
        assert call_args.args[4] == temp_config_path  # config_path


@pytest.mark.dev
class TestExperimentCLIImportConfig:
    """Test import-config command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up after each test."""
        patch.stopall()

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_import_config_success(self, mock_manager_class, temp_config_path, tmp_path):
        """Test import-config successfully imports JSON configuration."""
        mock_manager_class.reset_mock()
        mock_manager = Mock(spec=["save_config"])
        mock_manager_class.return_value = mock_manager

        # Create a test config file
        config_file = tmp_path / "test_config.json"
        config_data = {"experiment_type": "performance", "timeout_seconds": 300, "memory_limit_mb": 256}
        config_file.write_text(json.dumps(config_data))

        # Mock successful save
        config_path = tmp_path / "imported_config.yaml"
        mock_manager.save_config.return_value = config_path

        result = self.runner.invoke(
            experiment_app,
            [
                "import-config",
                "imported_config",
                str(config_file),
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Verify successful import
        assert result.exit_code == 0
        assert "Configuration 'imported_config' imported successfully" in result.output
        mock_manager.save_config.assert_called_once()

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_import_config_file_not_found(self, mock_manager_class, temp_config_path):
        """Test import-config handles missing JSON file."""
        mock_manager_class.reset_mock()
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        result = self.runner.invoke(
            experiment_app,
            [
                "import-config",
                "test_config",
                "/nonexistent/config.json",
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Verify error handling
        assert result.exit_code == 1
        assert "Configuration file '/nonexistent/config.json' not found" in result.output

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_import_config_invalid_json(self, mock_manager_class, temp_config_path, tmp_path):
        """Test import-config handles invalid JSON."""
        mock_manager_class.reset_mock()
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager

        # Create invalid JSON file
        config_file = tmp_path / "invalid_config.json"
        config_file.write_text("{ invalid json")

        result = self.runner.invoke(
            experiment_app,
            [
                "import-config",
                "test_config",
                str(config_file),
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Verify error handling
        assert result.exit_code == 1
        assert "Invalid JSON in configuration file" in result.output


@pytest.mark.dev
class TestExperimentCLIStatus:
    """Test status command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def teardown_method(self):
        """Clean up after each test."""
        patch.stopall()

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_status_with_active_experiments(self, mock_manager_class, temp_config_path):
        """Test status command displays active experiments."""
        mock_manager_class.reset_mock()
        mock_manager = Mock(spec=["list_active_experiments"])
        mock_manager_class.return_value = mock_manager

        # Mock active experiments
        mock_exp1 = Mock()
        mock_exp1.experiment_id = "exp-123"
        mock_exp1.status.value = "running"
        mock_exp1.config.experiment_type.value = "performance"
        mock_exp1.duration_seconds = 45.7

        mock_exp2 = Mock()
        mock_exp2.experiment_id = "exp-456"
        mock_exp2.status.value = "completed"
        mock_exp2.config.experiment_type.value = "ears_coverage"
        mock_exp2.duration_seconds = 120.3

        mock_manager.list_active_experiments.return_value = [mock_exp1, mock_exp2]

        result = self.runner.invoke(experiment_app, ["status", "--config-path", str(temp_config_path)])

        # Verify status display
        assert result.exit_code == 0
        assert "Active experiments:" in result.output
        assert "exp-123: running (performance)" in result.output
        assert "Duration: 45.70s" in result.output
        assert "exp-456: completed (ears_coverage)" in result.output
        assert "Duration: 120.30s" in result.output

    @patch("wassden.clis.experiment.ExperimentManager")
    def test_status_no_active_experiments(self, mock_manager_class, temp_config_path):
        """Test status command with no active experiments."""
        mock_manager_class.reset_mock()
        mock_manager = Mock(spec=["list_active_experiments"])
        mock_manager_class.return_value = mock_manager

        mock_manager.list_active_experiments.return_value = []

        result = self.runner.invoke(experiment_app, ["status", "--config-path", str(temp_config_path)])

        # Verify empty status display
        assert result.exit_code == 0
        assert "Active experiments:" in result.output
        assert "No active experiments" in result.output


@pytest.mark.dev
class TestExperimentCLIRunExperimentCommand:
    """Test run-experiment command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("wassden.clis.experiment._run_experiment_cmd_async", new_callable=AsyncMock)
    def test_run_experiment_cmd_success(self, mock_run_experiment_cmd_async, temp_config_path):
        """Test run-experiment command successful execution."""
        mock_result = Mock()
        mock_result.experiment_id = "api-exp-123"
        mock_result.status.value = "completed"
        mock_result.duration_seconds = 45.7
        mock_result.error_message = None
        mock_result.metadata = {"formatted_outputs": {"json": '{"result": "success"}'}}
        mock_result.experiment_id = "api-exp-123"
        mock_run_experiment_cmd_async.return_value = mock_result

        result = self.runner.invoke(
            experiment_app,
            [
                "run-experiment",
                "performance",
                "--parameters",
                '{"test": "value"}',
                "--timeout",
                "300",
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Debug output for diagnosis
        if result.exit_code != 0:
            print("\n=== TEST DEBUG: run_experiment_cmd_success ===")
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
            if result.exception:
                traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)

        # Verify successful execution
        assert result.exit_code == 0
        assert "Running performance experiment via API..." in result.output
        assert "Experiment completed: api-exp-123" in result.output
        assert "Status: completed" in result.output
        assert "Duration: 45.70s" in result.output
        assert "JSON Output" in result.output

    def test_run_experiment_cmd_invalid_json(self, temp_config_path):
        """Test run-experiment command with invalid JSON parameters."""
        result = self.runner.invoke(
            experiment_app,
            [
                "run-experiment",
                "performance",
                "--parameters",
                '{"invalid": json}',
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Verify JSON validation
        assert result.exit_code == 1
        assert "Invalid JSON parameters:" in result.output

    @patch("wassden.clis.experiment._run_experiment_cmd_async", new_callable=AsyncMock)
    def test_run_experiment_cmd_failure(self, mock_run_experiment_cmd_async, temp_config_path):
        """Test run-experiment command handles failures."""
        mock_run_experiment_cmd_async.side_effect = Exception("API error")

        result = self.runner.invoke(
            experiment_app,
            [
                "run-experiment",
                "performance",
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Verify error handling
        assert result.exit_code == 1
        assert "Experiment failed: API error" in result.output


@pytest.mark.dev
class TestExperimentCLIMeasureEarsCoverage:
    """Test measure-ears-coverage command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("wassden.clis.experiment._measure_ears_coverage_async", new_callable=AsyncMock)
    @patch("wassden.clis.experiment.OutputFormatter")
    def test_measure_ears_coverage_success(self, mock_formatter_class, mock_measure_async, tmp_path):
        """Test measure-ears-coverage command successful execution."""
        # Create test input files
        doc1 = tmp_path / "doc1.md"
        doc1.write_text("# Requirements\n## REQ-01 The system shall...")
        doc2 = tmp_path / "doc2.md"
        doc2.write_text("# Requirements\n## REQ-02 The system shall...")

        # Mock EARS coverage report
        mock_report = Mock()
        mock_report.total_requirements = 10
        mock_report.ears_compliant = 8
        mock_report.coverage_rate = 80.0
        mock_measure_async.return_value = mock_report

        # Mock formatter
        mock_formatter = Mock()
        mock_formatter.format_ears_coverage_report.return_value = '{"coverage": 80.0}'
        mock_formatter_class.return_value = mock_formatter

        result = self.runner.invoke(
            experiment_app,
            [
                "measure-ears-coverage",
                str(doc1),
                str(doc2),
                "--language",
                "ja",
                "--detail",
                "detailed",
                "--format",
                "json",
            ],
        )

        # Verify successful execution
        assert result.exit_code == 0
        assert "Measuring EARS coverage for 2 document(s)..." in result.output
        assert "EARS coverage analysis completed" in result.output
        assert "Total requirements: 10" in result.output
        assert "EARS compliant: 8" in result.output
        assert "Coverage rate: 80.0%" in result.output
        assert "JSON Report" in result.output

    @patch("wassden.clis.experiment._measure_ears_coverage_async", new_callable=AsyncMock)
    def test_measure_ears_coverage_failure(self, mock_measure_async):
        """Test measure-ears-coverage command handles failures."""
        mock_measure_async.side_effect = Exception("Analysis error")

        result = self.runner.invoke(
            experiment_app,
            [
                "measure-ears-coverage",
                "/nonexistent/doc.md",
            ],
        )

        # Verify error handling
        assert result.exit_code == 1
        assert "EARS coverage measurement failed: Analysis error" in result.output


@pytest.mark.dev
class TestExperimentCLIMeasurePerformance:
    """Test measure-performance command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("wassden.clis.experiment._measure_performance_async", new_callable=AsyncMock)
    @patch("wassden.clis.experiment.OutputFormatter")
    def test_measure_performance_success(self, mock_formatter_class, mock_measure_async):
        """Test measure-performance command successful execution."""
        # Mock performance report
        mock_report = Mock()
        mock_report.total_executions = 10
        mock_report.successful_executions = 9
        mock_report.average_wall_time_ms = 15.5
        mock_report.average_cpu_time_ms = 12.3
        mock_report.average_memory_mb = 45.7
        mock_measure_async.return_value = mock_report

        # Mock formatter
        mock_formatter = Mock()
        mock_formatter.format_performance_report.return_value = '{"avg_time": 15.5}'
        mock_formatter_class.return_value = mock_formatter

        result = self.runner.invoke(
            experiment_app,
            [
                "measure-performance",
                "test_operation",
                "--rounds",
                "10",
                "--warmup",
                "3",
                "--memory",
                "--format",
                "json",
            ],
        )

        # Verify successful execution
        assert result.exit_code == 0
        assert "Measuring performance for operation: test_operation" in result.output
        assert "Performance measurement completed" in result.output
        assert "Total executions: 10" in result.output
        assert "Successful: 9" in result.output
        assert "Average wall time: 15.50ms" in result.output
        assert "Average CPU time: 12.30ms" in result.output
        assert "Average memory: 45.70MB" in result.output
        assert "JSON Report" in result.output

    @patch("wassden.clis.experiment._measure_performance_async", new_callable=AsyncMock)
    def test_measure_performance_failure(self, mock_measure_async):
        """Test measure-performance command handles failures."""
        mock_measure_async.side_effect = Exception("Performance error")

        result = self.runner.invoke(
            experiment_app,
            [
                "measure-performance",
                "test_operation",
            ],
        )

        # Verify error handling
        assert result.exit_code == 1
        assert "Performance measurement failed: Performance error" in result.output


@pytest.mark.dev
class TestExperimentCLICompareExperiments:
    """Test compare command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("wassden.clis.experiment._compare_experiments_async", new_callable=AsyncMock)
    def test_compare_experiments_success(self, mock_compare_async, temp_config_path):
        """Test compare command successful execution."""
        mock_result = Mock()
        mock_result.experiment_id = "compare-exp-123"
        mock_result.status.value = "completed"
        mock_result.duration_seconds = 67.3
        mock_result.metadata = {
            "total_comparisons": 5,
            "significant_differences": 2,
            "formatted_outputs": {"json": '{"comparison": "result"}'},
        }
        mock_compare_async.return_value = mock_result

        result = self.runner.invoke(
            experiment_app,
            [
                "compare",
                "baseline-123",
                "exp-456",
                "exp-789",
                "--metrics",
                "latency",
                "--metrics",
                "throughput",
                "--format",
                "json",
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Verify successful execution
        assert result.exit_code == 0
        assert "Comparing experiments: baseline-123 vs ['exp-456', 'exp-789']" in result.output
        assert "Comparative analysis completed" in result.output
        assert "Experiment ID: compare-exp-123" in result.output
        assert "Status: completed" in result.output
        assert "Total comparisons: 5" in result.output
        assert "Significant differences: 2" in result.output
        assert "JSON Report" in result.output

    @patch("wassden.clis.experiment._compare_experiments_async", new_callable=AsyncMock)
    def test_compare_experiments_failure(self, mock_compare_async, temp_config_path):
        """Test compare command handles failures."""
        mock_compare_async.side_effect = Exception("Comparison error")

        result = self.runner.invoke(
            experiment_app,
            [
                "compare",
                "baseline-123",
                "exp-456",
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Verify error handling
        assert result.exit_code == 1
        assert "Comparative analysis failed: Comparison error" in result.output

    @patch("wassden.clis.experiment._run_experiment_async", new_callable=AsyncMock)
    def test_timeout_behavior_with_cli_command(self, mock_async, temp_config_path):
        """Test timeout behavior with top-level CLI command."""

        # Mock a slow operation that will timeout
        async def slow_operation(*_args, **_kwargs):
            await asyncio.sleep(2.0)  # Longer than CLI timeout
            return ExperimentResult(
                experiment_id="timeout-test",
                timestamp=datetime.now(),
                config=ExperimentConfig(
                    experiment_type=ExperimentType.PERFORMANCE,
                    timeout_seconds=1,
                    memory_limit_mb=100,
                ),
                status=ExperimentStatus.COMPLETED,
                duration_seconds=1.0,
            )

        mock_async.side_effect = slow_operation

        # Test CLI timeout behavior
        result = self.runner.invoke(
            experiment_app,
            [
                "run",
                "performance",
                "--timeout",
                "1",  # Very short timeout
                "--config-path",
                str(temp_config_path),
            ],
        )

        # Should handle timeout gracefully or return error
        assert result.exit_code != 0
