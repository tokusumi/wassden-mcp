"""Experiment management component for wassden validation framework.

This module provides experiment management functionality including configuration
management, experiment execution control, and result aggregation.
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from wassden.lib.experiment import (
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType,
    OutputFormat,
)


class ExperimentManagerError(Exception):
    """Base exception for experiment manager errors."""


class ConfigurationError(ExperimentManagerError):
    """Configuration-related errors."""


class ExecutionError(ExperimentManagerError):
    """Experiment execution errors."""


class ExperimentManager:
    """Manages experiment configuration and execution."""

    def __init__(self, config_dir: Path | None = None):
        """Initialize experiment manager.

        Args:
            config_dir: Directory for storing configuration files
        """
        self.config_dir = config_dir or Path.cwd() / ".wassden" / "experiments"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._active_experiments: dict[str, ExperimentResult] = {}

    def save_config(self, config: ExperimentConfig, name: str) -> Path:
        """Save experiment configuration to YAML file.

        Args:
            config: Experiment configuration to save
            name: Configuration name (used as filename)

        Returns:
            Path to saved configuration file

        Raises:
            ConfigurationError: If save operation fails
        """
        try:
            config_path = self.config_dir / f"{name}.yaml"

            # Convert pydantic model to dictionary for YAML serialization
            config_dict = config.model_dump(mode="json")

            with config_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(config_dict, f, default_flow_style=False, allow_unicode=True)

            return config_path

        except (OSError, yaml.YAMLError) as e:
            raise ConfigurationError(f"Failed to save configuration '{name}': {e}") from e

    def load_config(self, name: str) -> ExperimentConfig:
        """Load experiment configuration from YAML file.

        Args:
            name: Configuration name to load

        Returns:
            Loaded experiment configuration

        Raises:
            ConfigurationError: If load operation fails
        """
        try:
            config_path = self.config_dir / f"{name}.yaml"

            if not config_path.exists():
                raise ConfigurationError(f"Configuration '{name}' not found at {config_path}")

            with config_path.open(encoding="utf-8") as f:
                config_dict = yaml.safe_load(f)

            return ExperimentConfig(**config_dict)

        except (OSError, yaml.YAMLError) as e:
            raise ConfigurationError(f"Failed to load configuration '{name}': {e}") from e
        except ValidationError as e:
            raise ConfigurationError(f"Invalid configuration format in '{name}': {e}") from e

    def list_configs(self) -> list[str]:
        """List available configuration names.

        Returns:
            List of available configuration names
        """
        try:
            if not self.config_dir.exists():
                return []

            return [f.stem for f in self.config_dir.glob("*.yaml") if f.is_file()]
        except OSError:
            return []

    def create_experiment_result(self, config: ExperimentConfig) -> ExperimentResult:
        """Create initial experiment result with pending status.

        Args:
            config: Experiment configuration

        Returns:
            Initial experiment result
        """
        experiment_id = str(uuid.uuid4())

        result = ExperimentResult(
            experiment_id=experiment_id,
            timestamp=datetime.now(),
            config=config,
            status=ExperimentStatus.PENDING,
            duration_seconds=0.0,
        )

        self._active_experiments[experiment_id] = result
        return result

    def update_experiment_status(
        self,
        experiment_id: str,
        status: ExperimentStatus,
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Update experiment status.

        Args:
            experiment_id: Experiment identifier
            status: New status
            error_message: Error message if failed
            metadata: Additional metadata

        Raises:
            ExecutionError: If experiment not found
        """
        if experiment_id not in self._active_experiments:
            raise ExecutionError(f"Experiment {experiment_id} not found")

        result = self._active_experiments[experiment_id]
        result.status = status

        if error_message:
            result.error_message = error_message

        if metadata:
            result.metadata.update(metadata)

        # Calculate duration for completed/failed experiments
        if status in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED]:
            duration = (datetime.now() - result.timestamp).total_seconds()
            result.duration_seconds = duration

    def get_experiment_result(self, experiment_id: str) -> ExperimentResult | None:
        """Get experiment result by ID.

        Args:
            experiment_id: Experiment identifier

        Returns:
            Experiment result if found, None otherwise
        """
        return self._active_experiments.get(experiment_id)

    def list_active_experiments(self) -> list[ExperimentResult]:
        """List all active experiments.

        Returns:
            List of active experiment results
        """
        return list(self._active_experiments.values())

    def cleanup_completed_experiments(self) -> int:
        """Remove completed/failed experiments from active list.

        Returns:
            Number of experiments cleaned up
        """
        completed_statuses = {ExperimentStatus.COMPLETED, ExperimentStatus.FAILED}

        to_remove = [
            exp_id for exp_id, result in self._active_experiments.items() if result.status in completed_statuses
        ]

        for exp_id in to_remove:
            del self._active_experiments[exp_id]

        return len(to_remove)

    async def run_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        """Run experiment with given configuration.

        Args:
            config: Experiment configuration

        Returns:
            Completed experiment result

        Raises:
            ExecutionError: If experiment execution fails
        """
        result = self.create_experiment_result(config)

        try:
            self.update_experiment_status(result.experiment_id, ExperimentStatus.RUNNING)

            # Basic experiment execution - actual experiment logic is handled by experiment_api.py
            # This method provides the core experiment lifecycle management
            await asyncio.sleep(0.1)  # Minimal processing time

            # Mark as completed with metadata
            # Handle both enum and string cases for experiment_type
            exp_type_val = (
                config.experiment_type.value
                if hasattr(config.experiment_type, "value")
                else str(config.experiment_type)
            )

            metadata = {
                "experiment_type": exp_type_val,
                "parameters": config.parameters,
                "output_formats": [fmt.value if hasattr(fmt, "value") else str(fmt) for fmt in config.output_format],
            }

            self.update_experiment_status(result.experiment_id, ExperimentStatus.COMPLETED, metadata=metadata)

        except Exception as e:
            self.update_experiment_status(result.experiment_id, ExperimentStatus.FAILED, error_message=str(e))
            raise ExecutionError(f"Experiment execution failed: {e}") from e

        return self._active_experiments[result.experiment_id]

    def create_default_config(self, experiment_type: ExperimentType) -> ExperimentConfig:
        """Create default configuration for experiment type.

        Args:
            experiment_type: Type of experiment

        Returns:
            Default configuration for the experiment type
        """
        default_params: dict[ExperimentType, dict[str, Any]] = {
            ExperimentType.EARS_COVERAGE: {"input_paths": [], "output_detail_level": "summary"},
            ExperimentType.PERFORMANCE: {"measurement_rounds": 5, "warmup_rounds": 2, "memory_profiling": True},
            ExperimentType.LANGUAGE_DETECTION: {"test_documents": [], "confidence_threshold": 0.8},
            ExperimentType.COMPARATIVE: {"baseline_config": None, "comparison_metrics": ["mean", "std_dev"]},
        }

        params = default_params.get(experiment_type, {})
        return ExperimentConfig(
            experiment_type=experiment_type,
            parameters=params,
            output_format=[OutputFormat.JSON],
            timeout_seconds=600,
            memory_limit_mb=100,
        )
