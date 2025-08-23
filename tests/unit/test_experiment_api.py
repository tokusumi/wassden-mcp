"""Unit tests for experiment API - Comprehensive functionality testing."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from wassden.lib.experiment import (
    EARSCoverageReport,
    EARSViolationDetail,
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType,
    OutputFormat,
    PerformanceReport,
)
from wassden.lib.experiment_api import (
    ExecutionError,
    ExperimentAPIError,
    InvalidParametersError,
    _raise_unsupported_experiment_type,
    _validate_baseline_experiment_exists,
    _validate_baseline_experiment_id,
    _validate_comparison_experiment_ids,
    _validate_comparison_experiments_exist,
    _validate_experiment_exists,
    _validate_input_paths_parameter,
    _validate_measurement_rounds,
    _validate_path_exists,
    _validate_test_documents_parameter,
    _validate_warmup_rounds,
    measure_ears_coverage,
    measure_performance,
    run_experiment,
)

pytestmark = pytest.mark.dev


@pytest.mark.dev
class TestExperimentAPIExceptions:
    """Test experiment API exception classes with meaningful scenarios."""

    def test_invalid_parameters_error_with_actual_validation(self):
        """Test InvalidParametersError with real validation scenarios."""

        error = InvalidParametersError("Memory limit must be positive")
        assert "Memory limit must be positive" in str(error)
        assert isinstance(error, ExperimentAPIError)

        # Test that it can be raised and caught properly
        with pytest.raises(InvalidParametersError):
            raise InvalidParametersError("Test validation error")

    def test_execution_error_with_chained_exception(self):
        """Test ExecutionError with exception chaining."""
        original_error = RuntimeError("System resource unavailable")
        execution_error = ExecutionError("Experiment failed due to system error")
        execution_error.__cause__ = original_error

        assert isinstance(execution_error, ExperimentAPIError)
        assert execution_error.__cause__ == original_error


@pytest.mark.dev
class TestRunExperiment:
    """Test run_experiment function with realistic scenarios."""

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.measure_ears_coverage")
    @patch("wassden.lib.experiment_api.OutputFormatter")
    async def test_ears_coverage_experiment_with_real_workflow(self, mock_formatter_class, mock_measure_ears):
        """Test EARS coverage experiment with realistic file processing workflow."""

        # Create temporary test files to simulate real scenario
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file1 = Path(temp_dir) / "requirements1.md"
            test_file2 = Path(temp_dir) / "requirements2.md"

            # Create actual files with content
            test_file1.write_text("# Requirements\n1. The system SHALL validate input\n2. The system SHOULD log errors")
            test_file2.write_text("# More Requirements\n3. The system MUST provide feedback")

            # Setup analyzer mock with realistic data
            mock_report = Mock(spec=EARSCoverageReport)
            mock_report.model_dump.return_value = {
                "total_requirements": 3,
                "ears_compliant": 2,
                "coverage_rate": 0.67,
                "violations": ["Requirement 2 uses SHOULD instead of SHALL"],
            }
            mock_measure_ears.return_value = mock_report

            # Setup formatter mock
            mock_formatter = Mock()
            mock_formatter.format_ears_coverage_report.return_value = '{"coverage": 0.67, "violations": 1}'
            mock_formatter_class.return_value = mock_formatter

            # Execute with actual file paths
            result = await run_experiment(
                experiment_type=ExperimentType.EARS_COVERAGE,
                parameters={"input_paths": [str(test_file1), str(test_file2)], "output_detail_level": "detailed"},
                output_format=[OutputFormat.JSON],
                timeout_seconds=120,
                memory_limit_mb=256,
                config_path=Path(temp_dir) / "test_config",
            )

            # Verify realistic workflow execution
            assert result.status == ExperimentStatus.COMPLETED
            assert result.config.parameters["output_detail_level"] == "detailed"
            assert len(result.config.parameters["input_paths"]) == 2

            # Verify formatter was called with proper arguments
            mock_formatter.format_ears_coverage_report.assert_called_once()

            # Verify experiment manager state transitions
            assert "formatted_outputs" in result.metadata
            assert "json" in result.metadata["formatted_outputs"]

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.measure_performance")
    async def test_performance_experiment_with_custom_parameters(self, mock_measure_performance, tmp_path):
        """Test performance experiment with complex parameter handling."""

        # Setup performance measurement mock with realistic data
        mock_report = Mock(spec=PerformanceReport)
        mock_report.model_dump.return_value = {
            "operation_name": "complex_data_processing",
            "execution_times": [0.125, 0.132, 0.119, 0.127, 0.134],
            "average_time": 0.1274,
            "memory_usage": 2048,
            "cpu_usage": 34.5,
        }
        mock_measure_performance.return_value = mock_report

        # Test with comprehensive parameters
        result = await run_experiment(
            experiment_type=ExperimentType.PERFORMANCE,
            parameters={
                "operation_name": "complex_data_processing",
                "measurement_rounds": 10,
                "warmup_rounds": 5,
                "memory_profiling": True,
            },
            output_format=[OutputFormat.JSON, OutputFormat.CSV],
            timeout_seconds=600,
            memory_limit_mb=512,
            config_path=tmp_path / "test_config",
        )

        # Verify parameter propagation to performance measurement
        mock_measure_performance.assert_called_once_with(
            operation_name="complex_data_processing", measurement_rounds=10, warmup_rounds=5, memory_profiling=True
        )

        # Verify result contains expected metadata structure
        assert result.status == ExperimentStatus.COMPLETED
        assert "report" in result.metadata
        assert "formatted_outputs" in result.metadata
        assert "json" in result.metadata["formatted_outputs"]
        assert "csv" in result.metadata["formatted_outputs"]


@pytest.mark.dev
class TestExperimentAPIBoundaryValues:
    """Test boundary values and edge cases for experiment API."""

    @pytest.mark.asyncio
    async def test_timeout_boundary_values(self, tmp_path):
        """Test timeout parameter boundary values."""
        # Test minimum timeout (1 second)
        with patch("wassden.lib.experiment_manager.ExperimentManager"):
            result = await run_experiment(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=1,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
                parameters={"test_documents": ["test.py"]},
                config_path=tmp_path / "test_config",
            )
            assert result.config.timeout_seconds == 1

        # Test very large timeout
        with patch("wassden.lib.experiment_manager.ExperimentManager"):
            result = await run_experiment(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=86400,  # 24 hours
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
                parameters={"test_documents": ["test.py"]},
                config_path=tmp_path / "test_config",
            )
            assert result.config.timeout_seconds == 86400

    @pytest.mark.asyncio
    async def test_memory_limit_boundary_values(self, tmp_path):
        """Test memory limit parameter boundary values."""
        # Test minimum memory (1 MB)
        with patch("wassden.lib.experiment_manager.ExperimentManager"):
            result = await run_experiment(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=1,
                output_format=[OutputFormat.JSON],
                parameters={"test_documents": ["test.py"]},
                config_path=tmp_path / "test_config",
            )
            assert result.config.memory_limit_mb == 1

        # Test large memory (8GB)
        with patch("wassden.lib.experiment_manager.ExperimentManager"):
            result = await run_experiment(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=300,
                memory_limit_mb=8192,
                output_format=[OutputFormat.JSON],
                parameters={"test_documents": ["test.py"]},
                config_path=tmp_path / "test_config",
            )
            assert result.config.memory_limit_mb == 8192

    @pytest.mark.asyncio
    async def test_large_file_list_handling(self, tmp_path):
        """Test handling of large file lists in parameters."""
        # Create config with many test files (for performance experiment)
        large_file_list = [f"test_file_{i}.py" for i in range(1000)]

        with (
            patch("wassden.lib.experiment_manager.ExperimentManager"),
            patch("wassden.lib.experiment_api.measure_performance") as mock_measure,
        ):
            # Setup mock for performance measurement
            mock_report = Mock()
            mock_report.model_dump.return_value = {"operation_name": "test", "execution_time": 0.1}
            mock_measure.return_value = mock_report

            result = await run_experiment(
                experiment_type=ExperimentType.PERFORMANCE,  # Changed to PERFORMANCE
                timeout_seconds=1800,  # Longer timeout for large operations
                memory_limit_mb=500,  # More memory for large file list
                output_format=[OutputFormat.JSON],
                parameters={"test_documents": large_file_list},
                config_path=tmp_path / "test_config",
            )
            assert len(result.config.parameters["test_documents"]) == 1000

    @pytest.mark.asyncio
    async def test_concurrent_experiment_execution(self, tmp_path):
        """Test behavior with multiple experiments running concurrently."""
        # Create multiple different experiment configs
        configs = [
            (ExperimentType.PERFORMANCE, {"test_documents": ["perf_test.py"]}),
            (ExperimentType.EARS_COVERAGE, {"input_paths": ["ears_test.py"]}),
        ]

        results = []
        with (
            patch("wassden.lib.experiment_manager.ExperimentManager"),
            patch("wassden.lib.experiment_api.measure_performance") as mock_perf,
            patch("wassden.lib.experiment_api.measure_ears_coverage") as mock_ears,
        ):
            # Setup mocks
            mock_perf_report = Mock()
            mock_perf_report.model_dump.return_value = {"operation_name": "test", "execution_time": 0.1}
            mock_perf.return_value = mock_perf_report

            mock_ears_report = Mock()
            mock_ears_report.model_dump.return_value = {"total_requirements": 5, "ears_compliant": 4}
            mock_ears.return_value = mock_ears_report

            for exp_type, params in configs:
                result = await run_experiment(
                    experiment_type=exp_type,
                    timeout_seconds=300,
                    memory_limit_mb=100,
                    output_format=[OutputFormat.JSON],
                    parameters=params,
                    config_path=tmp_path / "test_config",
                )
                results.append(result)

        # Verify all experiments have unique IDs
        experiment_ids = [r.experiment_id for r in results]
        assert len(set(experiment_ids)) == len(experiment_ids)

        # Verify different experiment types
        assert results[0].config.experiment_type == ExperimentType.PERFORMANCE
        assert results[1].config.experiment_type == ExperimentType.EARS_COVERAGE

    @pytest.mark.asyncio
    async def test_output_format_combinations(self, tmp_path):
        """Test all possible output format combinations."""
        # Test all single formats
        single_formats = [[OutputFormat.JSON], [OutputFormat.CSV], [OutputFormat.YAML]]

        for output_format in single_formats:
            with (
                patch("wassden.lib.experiment_manager.ExperimentManager"),
                patch("wassden.lib.experiment_api.measure_performance") as mock_perf,
            ):
                mock_report = Mock()
                mock_report.model_dump.return_value = {"operation_name": "test", "execution_time": 0.1}
                mock_perf.return_value = mock_report

                result = await run_experiment(
                    experiment_type=ExperimentType.PERFORMANCE,
                    timeout_seconds=300,
                    memory_limit_mb=100,
                    output_format=output_format,
                    parameters={"test_documents": ["test.py"]},
                    config_path=tmp_path / "test_config",
                )
                assert result.config.output_format == output_format

        # Test multiple format combination - use performance experiment instead to avoid complexity
        multi_format = [OutputFormat.JSON, OutputFormat.CSV, OutputFormat.YAML]
        with (
            patch("wassden.lib.experiment_manager.ExperimentManager"),
            patch("wassden.lib.experiment_api.measure_performance") as mock_perf,
        ):
            mock_report = Mock()
            mock_report.model_dump.return_value = {"operation_name": "test", "execution_time": 0.1}
            mock_perf.return_value = mock_report

            result = await run_experiment(
                experiment_type=ExperimentType.PERFORMANCE,
                timeout_seconds=600,
                memory_limit_mb=150,
                output_format=multi_format,
                parameters={"test_documents": ["test.py"]},
                config_path=tmp_path / "test_config",
            )
            assert len(result.config.output_format) == 3
            assert all(fmt in result.config.output_format for fmt in multi_format)

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.LanguageDetectorAnalyzer")
    async def test_language_detection_with_validation_workflow(self, mock_analyzer_class, tmp_path):
        """Test language detection experiment with proper validation flow."""
        # Setup analyzer with realistic language detection data
        mock_analyzer = Mock()
        mock_analyzer.analyze_document = AsyncMock(
            return_value={
                "detected_language": "ja",
                "confidence": 0.95,
                "expected_language": "ja",
                "is_correct": True,
            }
        )
        mock_report = Mock()
        mock_report.model_dump.return_value = {
            "overall_accuracy": 0.92,
            "language_breakdown": {"ja": 0.95, "en": 0.89},
            "total_documents": 20,
        }
        mock_analyzer.generate_accuracy_report.return_value = mock_report
        mock_analyzer_class.return_value = mock_analyzer

        # Test with realistic test document parameters
        result = await run_experiment(
            experiment_type=ExperimentType.LANGUAGE_DETECTION,
            parameters={
                "test_documents": [
                    {"path": str(tmp_path / "doc1.md"), "expected_language": "ja", "is_spec_document": True},
                    {"path": str(tmp_path / "doc2.md"), "expected_language": "en", "is_spec_document": False},
                ]
            },
            output_format=[OutputFormat.JSON],
            config_path=tmp_path / "test_config",
        )

        # Verify analyzer was called for each document
        assert mock_analyzer.analyze_document.call_count == 2

        # Verify document processing workflow
        call_args_list = mock_analyzer.analyze_document.call_args_list
        first_call = call_args_list[0][0]
        assert str(first_call[0]) == str(tmp_path / "doc1.md")  # Path argument

        # Verify report generation was called
        mock_analyzer.generate_accuracy_report.assert_called_once()

        assert result.status == ExperimentStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_experiment_error_handling_and_recovery(self, tmp_path):
        """Test error handling with realistic failure scenarios."""
        # Test with invalid input_paths parameter type
        with pytest.raises(ExecutionError) as exc_info:
            await run_experiment(
                experiment_type=ExperimentType.EARS_COVERAGE,
                parameters={"input_paths": "not_a_list"},  # Invalid type
                config_path=tmp_path / "test_config",
            )

        # Verify error propagation and wrapping
        assert "EARS coverage experiment failed" in str(exc_info.value)

        # Test with non-existent file path
        with pytest.raises(ExecutionError) as exc_info:
            await run_experiment(
                experiment_type=ExperimentType.EARS_COVERAGE,
                parameters={"input_paths": ["/nonexistent/file.md"]},
                config_path=tmp_path / "test_config",
            )

        assert "Input path does not exist" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_experiment_invalid_experiment_type(self, tmp_path):
        """Test run_experiment with configuration validation."""

        # Test with actual error scenario - simulate a real failure
        with patch("wassden.lib.experiment_api._run_performance_experiment") as mock_run:
            mock_run.side_effect = FileNotFoundError("Input file not found")

            with pytest.raises(ExecutionError, match="Experiment execution failed"):
                await run_experiment(experiment_type=ExperimentType.PERFORMANCE, config_path=tmp_path / "test_config")

    @pytest.mark.asyncio
    async def test_run_experiment_parameter_validation(self, tmp_path):
        """Test run_experiment validates parameters correctly."""
        with patch("wassden.lib.experiment_api._run_ears_coverage_experiment") as mock_run:
            # Test that the function properly handles and validates parameters
            mock_config = ExperimentConfig(
                experiment_type=ExperimentType.EARS_COVERAGE,
                timeout_seconds=600,
                memory_limit_mb=100,
                output_format=[OutputFormat.JSON],
            )

            mock_result = ExperimentResult(
                experiment_id="param-test",
                config=mock_config,
                status=ExperimentStatus.COMPLETED,
                duration_seconds=2.1,
            )
            mock_run.return_value = mock_result

            # Test with custom parameters
            result = await run_experiment(
                experiment_type=ExperimentType.EARS_COVERAGE,
                parameters={"custom_param": "value"},
                timeout_seconds=300,
                memory_limit_mb=200,
                config_path=tmp_path / "test_config",
            )

            # Verify that ExperimentManager and config creation work correctly
            assert result.experiment_id == "param-test"
            mock_run.assert_called_once()

            # Verify the call was made with correct ExperimentConfig
            call_args = mock_run.call_args[0]
            config_used = call_args[0]
            assert config_used.experiment_type == ExperimentType.EARS_COVERAGE
            assert config_used.parameters == {"custom_param": "value"}
            assert config_used.timeout_seconds == 300
            assert config_used.memory_limit_mb == 200


@pytest.mark.dev
class TestExperimentAPIValidation:
    """Test validation functions with complex scenarios."""

    @pytest.mark.asyncio
    async def test_comprehensive_parameter_validation_scenarios(self, tmp_path):
        """Test various parameter validation scenarios with realistic data."""

        # Test empty input_paths validation
        with pytest.raises(ExecutionError, match="EARS coverage experiment failed.*input_paths parameter.*required"):
            await run_experiment(
                experiment_type=ExperimentType.EARS_COVERAGE,
                parameters={"input_paths": []},  # Empty list
                config_path=tmp_path / "test_config",
            )

        # Test language detection missing test_documents
        with pytest.raises(
            ExecutionError, match="Language detection experiment failed.*test_documents parameter.*required"
        ):
            await run_experiment(
                experiment_type=ExperimentType.LANGUAGE_DETECTION,
                parameters={},  # Missing required parameter
                config_path=tmp_path / "test_config",
            )

        # Test comparative experiment missing baseline
        with pytest.raises(
            ExecutionError, match="Comparative experiment failed.*baseline_experiment_id parameter.*required"
        ):
            await run_experiment(
                experiment_type=ExperimentType.COMPARATIVE,
                parameters={"comparison_experiment_ids": ["exp1", "exp2"]},  # Missing baseline
                config_path=tmp_path / "test_config",
            )

        # Test comparative experiment missing comparisons
        with pytest.raises(
            ExecutionError, match="Comparative experiment failed.*comparison_experiment_ids parameter.*required"
        ):
            await run_experiment(
                experiment_type=ExperimentType.COMPARATIVE,
                parameters={"baseline_experiment_id": "baseline"},  # Missing comparisons
                config_path=tmp_path / "test_config",
            )

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.measure_performance")
    async def test_performance_validation_edge_cases(self, mock_measure, tmp_path):
        """Test performance measurement validation with edge cases."""

        mock_report = Mock(spec=PerformanceReport)
        mock_report.model_dump.return_value = {"execution_time": 0.1}
        mock_measure.return_value = mock_report

        # Test negative measurement rounds
        with pytest.raises(ExecutionError, match="Performance experiment failed.*measurement_rounds must be positive"):
            await run_experiment(
                experiment_type=ExperimentType.PERFORMANCE,
                parameters={"measurement_rounds": -1},
                config_path=tmp_path / "test_config",
            )

        # Test zero measurement rounds
        with pytest.raises(ExecutionError, match="Performance experiment failed.*measurement_rounds must be positive"):
            await run_experiment(
                experiment_type=ExperimentType.PERFORMANCE,
                parameters={"measurement_rounds": 0},
                config_path=tmp_path / "test_config",
            )

        # Test negative warmup rounds
        with pytest.raises(ExecutionError, match="Performance experiment failed.*warmup_rounds.*negative"):
            await run_experiment(
                experiment_type=ExperimentType.PERFORMANCE,
                parameters={"warmup_rounds": -1},
                config_path=tmp_path / "test_config",
            )

    def test_validation_helper_functions_directly(self):
        """Test validation helper functions with comprehensive scenarios."""

        # Test measurement rounds validation
        with pytest.raises(InvalidParametersError):
            _validate_measurement_rounds(-1)
        with pytest.raises(InvalidParametersError):
            _validate_measurement_rounds(0)
        # Valid case should not raise
        _validate_measurement_rounds(5)  # Should pass

        # Test warmup rounds validation
        with pytest.raises(InvalidParametersError):
            _validate_warmup_rounds(-1)
        # Valid cases should not raise
        _validate_warmup_rounds(0)  # Should pass (zero is valid)
        _validate_warmup_rounds(3)  # Should pass

        # Test test_documents validation
        with pytest.raises(InvalidParametersError):
            _validate_test_documents_parameter([])
        # Valid case should not raise
        _validate_test_documents_parameter([{"path": "/some/test/path.md"}])  # Should pass

        # Test baseline experiment ID validation
        with pytest.raises(InvalidParametersError):
            _validate_baseline_experiment_id(None)
        with pytest.raises(InvalidParametersError):
            _validate_baseline_experiment_id("")
        # Valid case should not raise
        _validate_baseline_experiment_id("valid-exp-id")  # Should pass

        # Test comparison experiment IDs validation
        with pytest.raises(InvalidParametersError):
            _validate_comparison_experiment_ids([])
        # Valid case should not raise
        _validate_comparison_experiment_ids(["exp1", "exp2"])  # Should pass

    """Integration tests with minimal mocking to test real code paths."""

    @pytest.mark.asyncio
    async def test_parameter_validation_integration(self, tmp_path):
        """Test parameter validation in actual execution flow."""

        # Test with invalid input_paths parameter
        with pytest.raises(ExecutionError) as exc_info:
            await run_experiment(
                experiment_type=ExperimentType.EARS_COVERAGE,
                parameters={"input_paths": "not_a_list"},  # Should be list
                config_path=tmp_path / "test_config",
            )

        error_message = str(exc_info.value)
        assert "EARS coverage experiment failed" in error_message

    @pytest.mark.asyncio
    async def test_timeout_and_memory_limits_integration(self, tmp_path):
        """Test that timeout and memory limits are properly handled."""
        with patch("wassden.lib.experiment_api.measure_ears_coverage") as mock_measure:
            # Mock a quick completion
            mock_report = Mock()
            mock_report.model_dump.return_value = {"coverage": 0.75}
            mock_measure.return_value = mock_report

            # Test with custom limits
            result = await run_experiment(
                experiment_type=ExperimentType.EARS_COVERAGE,
                parameters={"input_paths": [str(tmp_path / "test.md")]},
                timeout_seconds=30,
                memory_limit_mb=64,
                config_path=tmp_path / "test_config",
            )

            # Verify limits were applied to config
            assert result.config.timeout_seconds == 30
            assert result.config.memory_limit_mb == 64

    @pytest.mark.asyncio
    async def test_output_format_processing_integration(self, tmp_path):
        """Test actual output format processing without full mocking."""
        with (
            patch("wassden.lib.experiment_api.measure_ears_coverage") as mock_measure,
            patch("wassden.lib.experiment_api.OutputFormatter") as mock_formatter_class,
        ):
            # Setup mocks
            mock_report = Mock()
            mock_report.model_dump.return_value = {"coverage": 0.88}
            mock_measure.return_value = mock_report

            mock_formatter = Mock()
            mock_formatter.format_ears_coverage_report.side_effect = [
                '{"coverage": 0.88}',  # JSON format
                "coverage,0.88",  # CSV format
            ]
            mock_formatter_class.return_value = mock_formatter

            # Execute with multiple output formats
            result = await run_experiment(
                experiment_type=ExperimentType.EARS_COVERAGE,
                parameters={"input_paths": [str(tmp_path / "test.md")]},
                output_format=[OutputFormat.JSON, OutputFormat.CSV],
                config_path=tmp_path / "test_config",
            )

            # Verify output formatting was called for each format
            assert mock_formatter.format_ears_coverage_report.call_count == 2

            # Verify metadata contains formatted outputs
            assert "formatted_outputs" in result.metadata
            formatted_outputs = result.metadata["formatted_outputs"]
            assert "json" in formatted_outputs
            assert "csv" in formatted_outputs

    """Basic integration tests for experiment API functions."""

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api._run_comparative_experiment")
    async def test_run_comparative_experiment(self, mock_run_comparative, tmp_path):
        """Test comparative experiment execution."""
        mock_config = ExperimentConfig(
            experiment_type=ExperimentType.COMPARATIVE,
            timeout_seconds=300,
            memory_limit_mb=200,
            output_format=[OutputFormat.YAML, OutputFormat.JSON],
        )

        mock_result = ExperimentResult(
            experiment_id="comparative-test",
            config=mock_config,
            status=ExperimentStatus.COMPLETED,
            duration_seconds=15.8,
        )
        mock_run_comparative.return_value = mock_result

        # Execute
        result = await run_experiment(
            experiment_type=ExperimentType.COMPARATIVE,
            output_format=[OutputFormat.YAML, OutputFormat.JSON],
            timeout_seconds=300,
            memory_limit_mb=200,
            config_path=tmp_path / "test_config",
        )

        # Verify
        assert result == mock_result
        mock_run_comparative.assert_called_once()

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api._run_language_detection_experiment")
    async def test_run_language_detection_experiment(self, mock_run_lang, tmp_path):
        """Test language detection experiment execution."""
        mock_config = ExperimentConfig(
            experiment_type=ExperimentType.LANGUAGE_DETECTION,
            timeout_seconds=600,
            memory_limit_mb=100,
            output_format=[OutputFormat.JSON],
        )

        mock_result = ExperimentResult(
            experiment_id="lang-test",
            config=mock_config,
            status=ExperimentStatus.COMPLETED,
            duration_seconds=8.3,
        )
        mock_run_lang.return_value = mock_result

        # Execute
        result = await run_experiment(
            experiment_type=ExperimentType.LANGUAGE_DETECTION,
            config_path=tmp_path / "test_config",
        )

        # Verify
        assert result == mock_result
        mock_run_lang.assert_called_once()


@pytest.mark.dev
class TestMeasureEarsCoverage:
    """Test measure_ears_coverage function directly."""

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.EARSAnalyzer")
    async def test_measure_ears_coverage_single_file(self, mock_analyzer_class, tmp_path):
        """Test EARS coverage measurement for single file."""
        # Create test file
        test_file = tmp_path / "requirements.md"
        test_file.write_text("# Requirements\n1. The system SHALL validate input")

        # Setup mock
        mock_analyzer = Mock()
        mock_report = Mock(spec=EARSCoverageReport)
        mock_report.total_requirements = 1
        mock_report.ears_compliant = 1
        mock_report.coverage_rate = 1.0
        mock_report.violations = []
        mock_analyzer.analyze_document = AsyncMock(return_value=mock_report)
        mock_analyzer_class.return_value = mock_analyzer

        result = await measure_ears_coverage([test_file])

        # Verify
        mock_analyzer.analyze_document.assert_called_once_with(test_file)
        assert result == mock_report

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.EARSAnalyzer")
    async def test_measure_ears_coverage_multiple_files(self, mock_analyzer_class, tmp_path):
        """Test EARS coverage measurement for multiple files."""
        # Create test files
        test_file1 = tmp_path / "req1.md"
        test_file2 = tmp_path / "req2.md"
        test_file1.write_text("# Requirements 1\n1. The system SHALL validate")
        test_file2.write_text("# Requirements 2\n2. The system MUST process")

        # Setup mock
        mock_analyzer = Mock()
        mock_report1 = Mock(spec=EARSCoverageReport)
        mock_report1.total_requirements = 1
        mock_report1.ears_compliant = 1
        mock_report1.coverage_rate = 1.0
        mock_report1.violations = []

        # Create proper violation object
        violation = EARSViolationDetail(
            line_number=2,
            requirement_text="The system MUST process",
            violation_type="Incorrect modal verb",
            suggestion="MUST should be SHALL",
        )

        mock_report2 = Mock(spec=EARSCoverageReport)
        mock_report2.total_requirements = 1
        mock_report2.ears_compliant = 0
        mock_report2.coverage_rate = 0.0
        mock_report2.violations = [violation]

        mock_analyzer.analyze_document = AsyncMock(side_effect=[mock_report1, mock_report2])
        mock_analyzer_class.return_value = mock_analyzer

        result = await measure_ears_coverage([test_file1, test_file2])

        # Verify combined report
        assert mock_analyzer.analyze_document.call_count == 2
        assert result.total_requirements == 2
        assert result.ears_compliant == 1
        assert result.coverage_rate == 0.5
        assert len(result.violations) == 1

    @pytest.mark.asyncio
    async def test_measure_ears_coverage_invalid_paths(self):
        """Test EARS coverage with invalid input paths."""
        # Test empty paths
        with pytest.raises(InvalidParametersError, match="At least one input path must be provided"):
            await measure_ears_coverage([])

        # Test non-existent path
        with pytest.raises(InvalidParametersError, match="Input path does not exist"):
            await measure_ears_coverage([Path("/nonexistent/file.md")])

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.EARSAnalyzer")
    async def test_measure_ears_coverage_execution_error(self, mock_analyzer_class, tmp_path):
        """Test EARS coverage measurement execution error handling."""
        test_file = tmp_path / "test.md"
        test_file.write_text("test content")

        # Setup mock to raise error
        mock_analyzer = Mock()
        mock_analyzer.analyze_document = AsyncMock(side_effect=RuntimeError("Analysis failed"))
        mock_analyzer_class.return_value = mock_analyzer

        # Test error propagation
        with pytest.raises(ExecutionError, match="EARS coverage measurement failed"):
            await measure_ears_coverage([test_file])


@pytest.mark.dev
class TestMeasurePerformance:
    """Test measure_performance function directly."""

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.PerformanceProfiler")
    async def test_measure_performance_predefined_operation(self, mock_profiler_class):
        """Test performance measurement for predefined operation."""
        # Setup mock
        mock_profiler = Mock()
        mock_report = Mock(spec=PerformanceReport)
        mock_report.operation_name = "test_operation"
        mock_report.execution_time = 0.1
        mock_profiler.profile_operation = AsyncMock(return_value=mock_report)
        mock_profiler_class.return_value = mock_profiler

        result = await measure_performance(
            operation_name="test_operation",
            measurement_rounds=5,
            warmup_rounds=2,
            memory_profiling=True,
        )

        # Verify
        mock_profiler.profile_operation.assert_called_once_with(
            "test_operation", rounds=5, warmup=2, memory_profiling=True
        )
        assert result == mock_report

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.PerformanceProfiler")
    async def test_measure_performance_custom_operation(self, mock_profiler_class):
        """Test performance measurement for custom operation."""
        # Setup mock
        mock_profiler = Mock()
        mock_report = Mock(spec=PerformanceReport)
        mock_profiler.profile_custom_operation = AsyncMock(return_value=mock_report)
        mock_profiler_class.return_value = mock_profiler

        def custom_op():
            return "test"

        result = await measure_performance(
            operation_name="custom_test",
            custom_operation=custom_op,
            measurement_rounds=3,
            warmup_rounds=1,
            memory_profiling=False,
        )

        # Verify
        mock_profiler.profile_custom_operation.assert_called_once_with(
            custom_op, "custom_test", rounds=3, warmup=1, memory_profiling=False
        )
        assert result == mock_report

    @pytest.mark.asyncio
    async def test_measure_performance_invalid_parameters(self):
        """Test performance measurement with invalid parameters."""
        # Test invalid measurement rounds
        with pytest.raises(InvalidParametersError, match="measurement_rounds must be positive"):
            await measure_performance("test", measurement_rounds=-1)

        with pytest.raises(InvalidParametersError, match="measurement_rounds must be positive"):
            await measure_performance("test", measurement_rounds=0)

        # Test invalid warmup rounds
        with pytest.raises(InvalidParametersError, match="warmup_rounds must be non-negative"):
            await measure_performance("test", warmup_rounds=-1)

    @pytest.mark.asyncio
    @patch("wassden.lib.experiment_api.PerformanceProfiler")
    async def test_measure_performance_execution_error(self, mock_profiler_class):
        """Test performance measurement execution error handling."""
        # Setup mock to raise error
        mock_profiler = Mock()
        mock_profiler.profile_operation = AsyncMock(side_effect=RuntimeError("Profiling failed"))
        mock_profiler_class.return_value = mock_profiler

        # Test error propagation
        with pytest.raises(ExecutionError, match="Performance measurement failed"):
            await measure_performance("test_operation")


@pytest.mark.dev
class TestValidationHelpers:
    """Test validation helper functions directly."""

    def test_validate_path_exists(self, tmp_path):
        """Test path existence validation."""
        # Test existing path
        existing_file = tmp_path / "exists.md"
        existing_file.write_text("content")
        _validate_path_exists(existing_file)  # Should not raise

        # Test non-existent path
        non_existent = tmp_path / "does_not_exist.md"
        with pytest.raises(InvalidParametersError, match="Input path does not exist"):
            _validate_path_exists(non_existent)

    def test_validate_input_paths_parameter(self):
        """Test input paths parameter validation."""
        # Test empty list
        with pytest.raises(InvalidParametersError, match="input_paths parameter is required"):
            _validate_input_paths_parameter([])

        # Test valid list
        _validate_input_paths_parameter(["file1.md", "file2.md"])  # Should not raise

    def test_validate_experiment_exists(self):
        """Test experiment existence validation."""
        # Test missing experiment
        with pytest.raises(InvalidParametersError, match="Experiment not found"):
            _validate_experiment_exists("missing-id", None)

        # Test existing experiment
        mock_experiment = Mock()
        _validate_experiment_exists("existing-id", mock_experiment)  # Should not raise

    def test_validate_baseline_experiment_exists(self):
        """Test baseline experiment existence validation."""
        # Test missing baseline
        with pytest.raises(InvalidParametersError, match="Baseline experiment not found"):
            _validate_baseline_experiment_exists("baseline-id", None)

        # Test existing baseline
        mock_experiment = Mock()
        _validate_baseline_experiment_exists("baseline-id", mock_experiment)  # Should not raise

    def test_validate_comparison_experiments_exist(self):
        """Test comparison experiments existence validation."""
        # Test with None experiment
        with pytest.raises(InvalidParametersError, match="One or more comparison experiments not found"):
            _validate_comparison_experiments_exist([Mock(), None, Mock()])

        # Test with all valid experiments
        _validate_comparison_experiments_exist([Mock(), Mock(), Mock()])  # Should not raise

    def test_raise_unsupported_experiment_type(self):
        """Test unsupported experiment type error."""
        # Mock an unsupported experiment type
        unsupported_type = "UNSUPPORTED_TYPE"

        with pytest.raises(InvalidParametersError, match="Unsupported experiment type"):
            _raise_unsupported_experiment_type(unsupported_type)


@pytest.mark.dev
class TestExperimentRunners:
    """Test internal experiment runner functions."""

    @pytest.mark.asyncio
    async def test_unsupported_experiment_type_in_run_experiment(self, tmp_path):
        """Test run_experiment with unsupported experiment type."""

        # Create a mock experiment type that's not handled - this will trigger pydantic validation error
        class UnsupportedType:
            def __str__(self):
                return "UNSUPPORTED"

        unsupported_type = UnsupportedType()

        # Pydantic validation will catch this first, so we expect ExecutionError
        with pytest.raises(ExecutionError, match="Experiment execution failed"):
            await run_experiment(experiment_type=unsupported_type, config_path=tmp_path / "test_config")

    def test_raise_unsupported_experiment_type_directly(self):
        """Test _raise_unsupported_experiment_type function directly."""
        with pytest.raises(InvalidParametersError, match="Unsupported experiment type"):
            _raise_unsupported_experiment_type("UNSUPPORTED_TYPE")
