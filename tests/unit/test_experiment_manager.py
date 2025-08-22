"""Unit tests for experiment manager."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from wassden.lib.experiment import (
    ExperimentConfig,
    ExperimentStatus,
    ExperimentType,
    OutputFormat,
)
from wassden.lib.experiment_manager import (
    ConfigurationError,
    ExecutionError,
    ExperimentManager,
    ExperimentManagerError,
)

pytestmark = pytest.mark.dev


@pytest.mark.dev
class TestExperimentManagerExecution:
    """Test experiment execution management functionality."""

    def test_create_experiment_result(self):
        """Test creation of experiment result objects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            config = ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=150,
                output_format=[OutputFormat.JSON],
            )

            result = manager.create_experiment_result(config)

            # Verify result properties
            assert result.experiment_id is not None
            assert len(result.experiment_id) > 10  # UUID-like length
            assert result.config == config
            assert result.status == ExperimentStatus.PENDING
            assert result.duration_seconds == 0.0
            assert result.metadata == {}

    def test_update_experiment_status(self):
        """Test experiment status updates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            config = ExperimentConfig(
                experiment_type=ExperimentType.EARS_COVERAGE,
                timeout_seconds=120,
                memory_limit_mb=75,
                output_format=[OutputFormat.YAML],
            )

            result = manager.create_experiment_result(config)
            experiment_id = result.experiment_id

            # Test status progression
            manager.update_experiment_status(experiment_id, ExperimentStatus.RUNNING)
            updated_result = manager.get_experiment_result(experiment_id)
            assert updated_result.status == ExperimentStatus.RUNNING

            # Test completion with metadata
            test_metadata = {"results": {"accuracy": 0.95}, "time_taken": 2.5}
            manager.update_experiment_status(experiment_id, ExperimentStatus.COMPLETED, metadata=test_metadata)
            final_result = manager.get_experiment_result(experiment_id)
            assert final_result.status == ExperimentStatus.COMPLETED
            assert final_result.metadata == test_metadata
            assert final_result.duration_seconds > 0  # Should be automatically calculated

    def test_update_experiment_status_with_error(self):
        """Test experiment status update with error message."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            config = ExperimentConfig(
                experiment_type=ExperimentType.COMPARATIVE,
                timeout_seconds=180,
                memory_limit_mb=200,
                output_format=[OutputFormat.JSON],
            )

            result = manager.create_experiment_result(config)
            experiment_id = result.experiment_id

            # Test failure with error message
            error_message = "Input file not found"
            manager.update_experiment_status(experiment_id, ExperimentStatus.FAILED, error_message=error_message)

            failed_result = manager.get_experiment_result(experiment_id)
            assert failed_result.status == ExperimentStatus.FAILED
            assert failed_result.error_message == error_message

    """Test experiment manager exception classes."""

    def test_experiment_manager_error_inheritance(self):
        """Test ExperimentManagerError is base exception."""
        error = ExperimentManagerError("test message")
        assert str(error) == "test message"
        assert isinstance(error, Exception)

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inherits from ExperimentManagerError."""
        error = ConfigurationError("config error")
        assert str(error) == "config error"
        assert isinstance(error, ExperimentManagerError)

    def test_execution_error_inheritance(self):
        """Test ExecutionError inherits from ExperimentManagerError."""
        error = ExecutionError("execution error")
        assert str(error) == "execution error"
        assert isinstance(error, ExperimentManagerError)


@pytest.mark.dev
class TestExperimentManagerAdvanced:
    """Test advanced ExperimentManager functionality."""

    def test_list_active_experiments_and_cleanup(self):
        """Test active experiment listing and cleanup functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            # Create multiple experiments with different statuses
            configs = [
                ExperimentConfig(
                    experiment_type=ExperimentType.PERFORMANCE,
                    timeout_seconds=300,
                    memory_limit_mb=100,
                    output_format=[OutputFormat.JSON],
                ),
                ExperimentConfig(
                    experiment_type=ExperimentType.EARS_COVERAGE,
                    timeout_seconds=600,
                    memory_limit_mb=200,
                    output_format=[OutputFormat.CSV],
                ),
                ExperimentConfig(
                    experiment_type=ExperimentType.LANGUAGE_DETECTION,
                    timeout_seconds=450,
                    memory_limit_mb=150,
                    output_format=[OutputFormat.YAML],
                ),
            ]

            results = []
            for config in configs:
                result = manager.create_experiment_result(config)
                results.append(result)

            # Verify all experiments are initially active
            active_experiments = manager.list_active_experiments()
            assert len(active_experiments) == 3

            # Update statuses to different states
            manager.update_experiment_status(results[0].experiment_id, ExperimentStatus.COMPLETED)
            manager.update_experiment_status(
                results[1].experiment_id, ExperimentStatus.FAILED, error_message="Test error"
            )
            manager.update_experiment_status(results[2].experiment_id, ExperimentStatus.RUNNING)

            # Test cleanup - should remove completed and failed
            cleaned_count = manager.cleanup_completed_experiments()
            assert cleaned_count == 2  # Completed and failed experiments removed

            # Verify only running experiment remains
            remaining_experiments = manager.list_active_experiments()
            assert len(remaining_experiments) == 1
            assert remaining_experiments[0].status == ExperimentStatus.RUNNING
            assert remaining_experiments[0].experiment_id == results[2].experiment_id

    def test_experiment_not_found_error_handling(self):
        """Test error handling for non-existent experiments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            non_existent_id = "non-existent-experiment-id"

            # Test get_experiment_result with non-existent ID
            result = manager.get_experiment_result(non_existent_id)
            assert result is None

            # Test update_experiment_status with non-existent ID
            with pytest.raises(ExecutionError, match="Experiment .* not found"):
                manager.update_experiment_status(non_existent_id, ExperimentStatus.COMPLETED)

    def test_create_default_config_for_all_experiment_types(self):
        """Test default config creation for all experiment types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            # Test each experiment type
            experiment_types = [
                ExperimentType.PERFORMANCE,
                ExperimentType.EARS_COVERAGE,
                ExperimentType.LANGUAGE_DETECTION,
                ExperimentType.COMPARATIVE,
            ]

            for exp_type in experiment_types:
                config = manager.create_default_config(exp_type)

                # Verify basic properties
                assert config.experiment_type == exp_type
                assert config.timeout_seconds == 600  # Default value
                assert config.memory_limit_mb == 100  # Default value
                assert OutputFormat.JSON in config.output_format  # Default format
                assert isinstance(config.parameters, dict)

                # Test that config can be saved and loaded
                config_name = f"test_default_{exp_type.value}"
                saved_path = manager.save_config(config, config_name)
                assert saved_path.exists()

                loaded_config = manager.load_config(config_name)
                assert loaded_config.experiment_type == exp_type


@pytest.mark.dev
class TestExperimentManagerInit:
    """Test ExperimentManager initialization."""

    def test_init_default_config_dir(self, tmp_path):
        """Test initialization with default config directory."""
        with patch("wassden.lib.experiment_manager.Path.cwd", return_value=tmp_path):
            manager = ExperimentManager()
            expected_dir = tmp_path / ".wassden" / "experiments"
            assert manager.config_dir == expected_dir
            assert manager.config_dir.exists()

    def test_init_custom_config_dir(self):
        """Test initialization with custom config directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "custom_experiments"
            manager = ExperimentManager(config_dir=custom_dir)
            assert manager.config_dir == custom_dir
            assert manager.config_dir.exists()

    def test_init_active_experiments_empty(self, tmp_path):
        """Test initialization with empty active experiments."""
        with patch("wassden.lib.experiment_manager.Path.cwd", return_value=tmp_path):
            manager = ExperimentManager()
            assert manager._active_experiments == {}


@pytest.mark.dev
class TestExperimentManagerSaveConfig:
    """Test save_config method with real file operations."""

    def test_save_config_success(self):
        """Test successful config saving with actual file verification."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            config = ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=150,
                output_format=[OutputFormat.JSON],
                parameters={"measurement_rounds": 5, "warmup": True},
            )

            config_path = manager.save_config(config, "test_config")

            # Verify file was created at correct location
            expected_path = manager.config_dir / "test_config.yaml"
            assert config_path == expected_path
            assert config_path.exists()
            assert config_path.is_file()

            # Verify content is valid YAML and matches configuration
            with config_path.open() as f:
                saved_data = yaml.safe_load(f)

            # Verify all fields are correctly saved
            assert saved_data["experiment_type"] == "performance"
            assert saved_data["timeout_seconds"] == 300
            assert saved_data["memory_limit_mb"] == 150
            assert saved_data["output_format"] == ["json"]
            assert saved_data["parameters"] == {"measurement_rounds": 5, "warmup": True}

            # Verify file can be loaded back into ExperimentConfig
            reloaded_config = ExperimentConfig(**saved_data)
            assert reloaded_config.experiment_type == config.experiment_type
            assert reloaded_config.parameters == config.parameters

    def test_save_config_file_permissions(self):
        """Test that saved config files have correct permissions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            config = ExperimentConfig(
                experiment_type=ExperimentType.EARS_COVERAGE,
                timeout_seconds=120,
                memory_limit_mb=75,
                output_format=[OutputFormat.YAML],
            )

            config_path = manager.save_config(config, "permission_test")

            # Verify file is readable and writable
            assert config_path.exists()
            assert config_path.stat().st_mode & 0o600  # Owner read/write

            # Verify content can be read
            content = config_path.read_text()
            assert "experiment_type: ears_coverage" in content

    def test_save_config_overwrites_existing(self):
        """Test that save_config overwrites existing config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            # Save first config
            config1 = ExperimentConfig(
                experiment_type=ExperimentType.EARS_COVERAGE,
                timeout_seconds=100,
                memory_limit_mb=50,
                output_format=[OutputFormat.YAML],
            )
            manager.save_config(config1, "duplicate_test")

            # Save second config with same name
            config2 = ExperimentConfig(
                experiment_type=ExperimentType.LANGUAGE_DETECTION,
                timeout_seconds=200,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
            )
            config_path = manager.save_config(config2, "duplicate_test")

            # Verify latest config was saved
            with config_path.open() as f:
                saved_data = yaml.safe_load(f)

            assert saved_data["experiment_type"] == "language_detection"
            assert saved_data["timeout_seconds"] == 200


@pytest.mark.dev
class TestExperimentManagerLoadConfig:
    """Test load_config method."""

    def test_load_config_success(self):
        """Test successful config loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            # Create config file
            config_data = {
                "experiment_type": "comparative",
                "timeout_seconds": 400,
                "memory_limit_mb": 200,
                "output_format": ["json", "yaml"],
            }
            config_path = manager.config_dir / "load_test.yaml"
            with config_path.open("w") as f:
                yaml.dump(config_data, f)

            # Load config
            loaded_config = manager.load_config("load_test")

            assert loaded_config.experiment_type == ExperimentType.COMPARATIVE
            assert loaded_config.timeout_seconds == 400
            assert loaded_config.memory_limit_mb == 200
            # Note: ExperimentConfig.output_format only accepts one format at a time in a list
            assert OutputFormat.JSON in loaded_config.output_format

    def test_load_config_file_not_found(self):
        """Test loading non-existent config raises ConfigurationError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            with pytest.raises(ConfigurationError, match="Configuration file .* not found"):
                manager.load_config("nonexistent")


@pytest.mark.dev
class TestExperimentManagerCreateDefaultConfig:
    """Test create_default_config method."""

    def test_create_default_config_performance(self, tmp_path):
        """Test creating default performance config."""
        manager = ExperimentManager(config_dir=tmp_path)
        config = manager.create_default_config(ExperimentType.PERFORMANCE)

        assert config.experiment_type == ExperimentType.PERFORMANCE
        assert config.timeout_seconds == 600
        assert config.memory_limit_mb == 100
        assert OutputFormat.JSON in config.output_format

    def test_create_default_config_ears_coverage(self, tmp_path):
        """Test creating default EARS coverage config."""
        manager = ExperimentManager(config_dir=tmp_path)
        config = manager.create_default_config(ExperimentType.EARS_COVERAGE)

        assert config.experiment_type == ExperimentType.EARS_COVERAGE
        assert config.timeout_seconds == 600
        assert config.memory_limit_mb == 100
        assert OutputFormat.JSON in config.output_format

    def test_create_default_config_language_detection(self, tmp_path):
        """Test creating default language detection config."""
        manager = ExperimentManager(config_dir=tmp_path)
        config = manager.create_default_config(ExperimentType.LANGUAGE_DETECTION)

        assert config.experiment_type == ExperimentType.LANGUAGE_DETECTION
        assert config.timeout_seconds == 600
        assert config.memory_limit_mb == 100
        assert OutputFormat.JSON in config.output_format

    def test_create_default_config_comparative(self, tmp_path):
        """Test creating default comparative config."""
        manager = ExperimentManager(config_dir=tmp_path)
        config = manager.create_default_config(ExperimentType.COMPARATIVE)

        assert config.experiment_type == ExperimentType.COMPARATIVE
        assert config.timeout_seconds == 600
        assert config.memory_limit_mb == 100
        assert OutputFormat.JSON in config.output_format


@pytest.mark.dev
class TestExperimentManagerListConfigs:
    """Test list_configs method."""

    def test_list_configs_empty(self):
        """Test listing configs when directory is empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))
            configs = manager.list_configs()
            assert configs == []

    def test_list_configs_nonexistent_directory(self):
        """Test listing configs when config directory doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a non-existent subdirectory
            nonexistent_dir = Path(temp_dir) / "nonexistent"
            manager = ExperimentManager(config_dir=nonexistent_dir)
            configs = manager.list_configs()
            assert configs == []

    def test_list_configs_with_files(self):
        """Test listing configs with multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            # Create test config files
            config_names = ["config1", "config2", "config3"]
            for name in config_names:
                config = ExperimentConfig(
                    experiment_type=ExperimentType.PERFORMANCE,
                    timeout_seconds=300,
                    memory_limit_mb=100,
                    output_format=[OutputFormat.JSON],
                )
                manager.save_config(config, name)

            configs = manager.list_configs()
            assert len(configs) == 3
            assert all(name in configs for name in config_names)

    def test_list_configs_ignores_non_yaml(self):
        """Test that list_configs ignores non-YAML files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            # Create YAML config
            config = ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
            )
            manager.save_config(config, "valid_config")

            # Create non-YAML files
            (manager.config_dir / "readme.txt").write_text("Not a config")
            (manager.config_dir / "config.json").write_text("{}")

            configs = manager.list_configs()
            assert configs == ["valid_config"]


@pytest.mark.dev
class TestExperimentManagerBasicFunctionality:
    """Test basic experiment manager functionality that is implemented."""

    def test_save_and_load_config_integration(self):
        """Test saving and loading config integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            # Create and save config
            config = manager.create_default_config(ExperimentType.PERFORMANCE)
            config.timeout_seconds = 300
            config.memory_limit_mb = 150

            manager.save_config(config, "integration_test")

            # Load and verify
            loaded_config = manager.load_config("integration_test")
            assert loaded_config.experiment_type == ExperimentType.PERFORMANCE
            assert loaded_config.timeout_seconds == 300
            assert loaded_config.memory_limit_mb == 150


@pytest.mark.dev
class TestExperimentManagerAsyncExecution:
    """Test asynchronous experiment execution functionality."""

    @pytest.mark.asyncio
    async def test_run_experiment_basic_workflow(self):
        """Test basic run_experiment workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            config = ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
                parameters={"test_documents": ["test.py"]},
            )

            # Execute experiment
            result = await manager.run_experiment(config)

            # Verify complete workflow
            assert result.status == ExperimentStatus.COMPLETED
            assert result.experiment_id in manager._active_experiments
            assert "experiment_type" in result.metadata
            assert result.metadata["experiment_type"] == "performance"
            assert "parameters" in result.metadata
            assert result.metadata["parameters"] == config.parameters
            assert "output_formats" in result.metadata
            assert result.metadata["output_formats"] == ["json"]

    @pytest.mark.asyncio
    async def test_run_experiment_all_types(self):
        """Test run_experiment with all experiment types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            test_cases = [
                (ExperimentType.PERFORMANCE, {"test_documents": ["perf.py"]}),
                (ExperimentType.EARS_COVERAGE, {"test_documents": ["ears.py"]}),
                (ExperimentType.LANGUAGE_DETECTION, {"test_documents": ["lang.py"]}),
                (ExperimentType.COMPARATIVE, {"test_documents": ["comp.py"], "baseline_experiment_id": "baseline-123"}),
            ]

            for exp_type, params in test_cases:
                config = ExperimentConfig(
                    experiment_type=exp_type,
                    timeout_seconds=300,
                    memory_limit_mb=100,
                    output_format=[OutputFormat.JSON],
                    parameters=params,
                )

                result = await manager.run_experiment(config)

                assert result.status == ExperimentStatus.COMPLETED
                assert result.metadata["experiment_type"] == exp_type.value
                assert result.metadata["parameters"] == params

    @pytest.mark.asyncio
    async def test_run_experiment_multiple_output_formats(self):
        """Test run_experiment with multiple output formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            config = ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON, OutputFormat.CSV, OutputFormat.YAML],
                parameters={"test_documents": ["test.py"]},
            )

            result = await manager.run_experiment(config)

            assert result.status == ExperimentStatus.COMPLETED
            expected_formats = ["json", "csv", "yaml"]
            assert result.metadata["output_formats"] == expected_formats

    @pytest.mark.asyncio
    async def test_run_experiment_error_handling(self):
        """Test run_experiment error handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            config = ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
                parameters={"test_documents": ["test.py"]},
            )

            # Mock update_experiment_status to raise an exception
            original_update = manager.update_experiment_status
            call_count = 0

            def mock_update(exp_id, status, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 2:  # Second call (COMPLETED status)
                    raise RuntimeError("Simulated update error")
                return original_update(exp_id, status, **kwargs)

            manager.update_experiment_status = mock_update

            with pytest.raises(ExecutionError, match="Experiment execution failed"):
                await manager.run_experiment(config)

            # Verify experiment was marked as failed
            experiment_id = next(iter(manager._active_experiments.keys()))
            failed_result = manager._active_experiments[experiment_id]
            assert failed_result.status == ExperimentStatus.FAILED
            assert "Simulated update error" in failed_result.error_message

    @pytest.mark.asyncio
    async def test_run_experiment_status_transitions(self):
        """Test experiment status transitions during execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            config = ExperimentConfig(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
                parameters={"test_documents": ["test.py"]},
            )

            # Track status changes
            status_changes = []
            original_update = manager.update_experiment_status

            def track_status(exp_id, status, **kwargs):
                status_changes.append((exp_id, status))
                return original_update(exp_id, status, **kwargs)

            manager.update_experiment_status = track_status

            result = await manager.run_experiment(config)

            # Verify status transition: PENDING -> RUNNING -> COMPLETED
            assert len(status_changes) == 2
            assert status_changes[0][1] == ExperimentStatus.RUNNING
            assert status_changes[1][1] == ExperimentStatus.COMPLETED
            assert result.status == ExperimentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_run_experiment_concurrent_execution(self):
        """Test multiple concurrent experiment executions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ExperimentManager(config_dir=Path(temp_dir))

            configs = [
                ExperimentConfig(
                    experiment_type=ExperimentType.PERFORMANCE,
                    timeout_seconds=300,
                    memory_limit_mb=100,
                    output_format=[OutputFormat.JSON],
                    parameters={"test_documents": [f"test{i}.py"]},
                )
                for i in range(3)
            ]

            # Execute all experiments concurrently
            tasks = [manager.run_experiment(config) for config in configs]
            results = await asyncio.gather(*tasks)

            # Verify all experiments completed successfully
            assert len(results) == 3
            for result in results:
                assert result.status == ExperimentStatus.COMPLETED

            # Verify all have unique IDs
            experiment_ids = [result.experiment_id for result in results]
            assert len(set(experiment_ids)) == 3

            # Verify all are tracked in manager
            assert len(manager._active_experiments) == 3
