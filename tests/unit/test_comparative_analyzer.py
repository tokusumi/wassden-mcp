"""Unit tests for comparative analyzer module.

Tests for TASK-02-06 comparative experiment functionality and TR-04 numerical precision requirements.
"""

from unittest.mock import Mock

import pytest

from wassden.lib.comparative_analyzer import (
    ComparativeAnalyzer,
    IncompatibleExperimentsError,
    InsufficientDataError,
)
from wassden.lib.experiment import (
    ComparativeExperimentReport,
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType,
    PerformanceDetail,
    PerformanceReport,
    StatisticalComparison,
)


class TestComparativeAnalyzer:
    """Test cases for ComparativeAnalyzer with numerical precision focus."""

    @pytest.fixture
    def analyzer(self):
        """Create ComparativeAnalyzer instance."""
        return ComparativeAnalyzer()

    @pytest.fixture
    def sample_experiment_config(self):
        """Create sample experiment configuration."""
        return ExperimentConfig(
            experiment_type=ExperimentType.PERFORMANCE,
            parameters={"operation_name": "test_operation"},
            timeout_seconds=300,
        )

    @pytest.fixture
    def baseline_performance_experiment(self, sample_experiment_config):
        """Create baseline performance experiment result."""
        performance_report = PerformanceReport(
            total_executions=5,
            successful_executions=5,
            failed_executions=0,
            average_wall_time_ms=100.0,
            average_cpu_time_ms=90.0,
            average_memory_mb=50.0,
            peak_memory_mb=55.0,
            details=[
                PerformanceDetail(
                    wall_time_ms=95.0,
                    cpu_time_ms=85.0,
                    memory_used_mb=48.0,
                    peak_memory_mb=52.0,
                    function_name="test_func",
                    success=True,
                ),
                PerformanceDetail(
                    wall_time_ms=105.0,
                    cpu_time_ms=95.0,
                    memory_used_mb=52.0,
                    peak_memory_mb=58.0,
                    function_name="test_func",
                    success=True,
                ),
            ],
        )

        return ExperimentResult(
            experiment_id="baseline_perf_001",
            config=sample_experiment_config,
            status=ExperimentStatus.COMPLETED,
            duration_seconds=1.5,
            performance_report=performance_report,
        )

    @pytest.fixture
    def comparison_performance_experiment(self, sample_experiment_config):
        """Create comparison performance experiment result."""
        performance_report = PerformanceReport(
            total_executions=5,
            successful_executions=5,
            failed_executions=0,
            average_wall_time_ms=80.0,  # Improved performance
            average_cpu_time_ms=75.0,
            average_memory_mb=45.0,
            peak_memory_mb=50.0,
            details=[
                PerformanceDetail(
                    wall_time_ms=75.0,
                    cpu_time_ms=70.0,
                    memory_used_mb=43.0,
                    peak_memory_mb=47.0,
                    function_name="test_func",
                    success=True,
                ),
                PerformanceDetail(
                    wall_time_ms=85.0,
                    cpu_time_ms=80.0,
                    memory_used_mb=47.0,
                    peak_memory_mb=53.0,
                    function_name="test_func",
                    success=True,
                ),
            ],
        )

        return ExperimentResult(
            experiment_id="comparison_perf_001",
            config=sample_experiment_config,
            status=ExperimentStatus.COMPLETED,
            duration_seconds=1.2,
            performance_report=performance_report,
        )

    def test_compare_experiments_basic(
        self, analyzer, baseline_performance_experiment, comparison_performance_experiment
    ):
        """Test basic experiment comparison functionality.

        Implements: TR-04 - Statistical comparison numerical precision
        """
        baseline = baseline_performance_experiment
        comparisons = [comparison_performance_experiment]

        result = analyzer.compare_experiments(
            baseline_experiment=baseline,
            comparison_experiments=comparisons,
            metrics_to_compare=["average_wall_time_ms"],
        )

        assert isinstance(result, ComparativeExperimentReport)
        assert len(result.comparisons) == 1

        comparison = result.comparisons[0]
        assert comparison.metric_name == "average_wall_time_ms"
        assert comparison.baseline_experiment_id == "baseline_perf_001"
        assert comparison.comparison_experiment_id == "comparison_perf_001"

        # Verify improvement percentage calculation precision
        expected_improvement = ((80.0 - 100.0) / 100.0) * 100.0  # -20%
        assert abs(comparison.improvement_percentage - expected_improvement) < 1e-10

    def test_statistical_comparison_precision(
        self, analyzer, baseline_performance_experiment, comparison_performance_experiment
    ):
        """Test statistical comparison numerical precision.

        Implements: TR-04 - Numerical precision requirements
        """
        # Create experiments with known statistical properties
        baseline_values = [95.0, 105.0, 100.0, 98.0, 102.0]
        comparison_values = [75.0, 85.0, 80.0, 78.0, 82.0]

        # Mock the _extract_metric_values method to return our test data
        analyzer._extract_performance_values = Mock()
        analyzer._extract_performance_values.side_effect = [baseline_values, comparison_values]

        result = analyzer.compare_experiments(
            baseline_experiment=baseline_performance_experiment,
            comparison_experiments=[comparison_performance_experiment],
            metrics_to_compare=["average_wall_time_ms"],
        )

        stat_comparison = result.comparisons[0].statistical_comparison

        # Verify statistical calculations with high precision
        expected_baseline_mean = sum(baseline_values) / len(baseline_values)  # 100.0
        expected_comparison_mean = sum(comparison_values) / len(comparison_values)  # 80.0

        assert abs(stat_comparison.baseline_mean - expected_baseline_mean) < 1e-10
        assert abs(stat_comparison.comparison_mean - expected_comparison_mean) < 1e-10

        # Verify that p-value is within valid range
        assert 0.0 <= stat_comparison.p_value <= 1.0

        # Verify effect size (Cohen's d) calculation
        assert isinstance(stat_comparison.effect_size, float)

        # Verify confidence interval bounds
        assert stat_comparison.confidence_interval_lower <= stat_comparison.confidence_interval_upper

    def test_insufficient_data_error(self, analyzer):
        """Test error handling for insufficient comparison data."""
        with pytest.raises(InsufficientDataError, match="At least one comparison experiment is required"):
            analyzer.compare_experiments(
                baseline_experiment=Mock(),
                comparison_experiments=[],
                metrics_to_compare=["test_metric"],
            )

    def test_incompatible_experiments_error(self, analyzer, baseline_performance_experiment):
        """Test error handling for incompatible experiment types."""
        # Create experiment with different type
        incompatible_config = ExperimentConfig(
            experiment_type=ExperimentType.EARS_COVERAGE,  # Different type
            parameters={"input_paths": ["test.md"]},
        )

        incompatible_experiment = ExperimentResult(
            experiment_id="incompatible_001",
            config=incompatible_config,
            status=ExperimentStatus.COMPLETED,
            duration_seconds=1.0,
        )

        with pytest.raises(IncompatibleExperimentsError, match="Experiment types don't match"):
            analyzer.compare_experiments(
                baseline_experiment=baseline_performance_experiment,
                comparison_experiments=[incompatible_experiment],
                metrics_to_compare=["average_wall_time_ms"],
            )

    def test_improvement_percentage_calculation_precision(self, analyzer):
        """Test improvement percentage calculation with edge cases.

        Implements: TR-04 - Numerical precision for percentage calculations
        """
        # Test zero baseline (edge case)
        result = analyzer._calculate_improvement_percentage(0.0, 10.0)
        assert result == 0.0  # Should handle zero baseline gracefully

        # Test normal case with high precision
        baseline_mean = 123.456789
        comparison_mean = 98.765432
        result = analyzer._calculate_improvement_percentage(baseline_mean, comparison_mean)

        expected = ((comparison_mean - baseline_mean) / baseline_mean) * 100.0
        assert abs(result - expected) < 1e-10

        # Test negative improvement (degradation)
        baseline_mean = 50.0
        comparison_mean = 75.0
        result = analyzer._calculate_improvement_percentage(baseline_mean, comparison_mean)

        assert result == 50.0  # 50% increase (positive improvement)

    def test_generate_recommendations_logic(
        self, analyzer, baseline_performance_experiment, comparison_performance_experiment
    ):
        """Test recommendation generation logic."""
        result = analyzer.compare_experiments(
            baseline_experiment=baseline_performance_experiment,
            comparison_experiments=[comparison_performance_experiment],
            metrics_to_compare=["average_wall_time_ms"],
        )

        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0

        # Should contain meaningful recommendations
        recommendations_text = " ".join(result.recommendations)
        assert isinstance(recommendations_text, str)

    def test_summary_statistics_calculation(
        self, analyzer, baseline_performance_experiment, comparison_performance_experiment
    ):
        """Test summary statistics calculation accuracy.

        Implements: TR-04 - Statistical summary precision
        """
        result = analyzer.compare_experiments(
            baseline_experiment=baseline_performance_experiment,
            comparison_experiments=[comparison_performance_experiment],
            metrics_to_compare=["average_wall_time_ms", "average_memory_mb"],
        )

        summary = result.summary_statistics

        # Verify summary statistics structure and precision
        assert "total_comparisons" in summary
        assert "significant_improvements" in summary
        assert "significant_degradations" in summary
        assert "average_improvement_percentage" in summary
        assert "maximum_improvement_percentage" in summary
        assert "minimum_improvement_percentage" in summary
        assert "metrics_compared" in summary

        # Verify numerical consistency
        assert isinstance(summary["average_improvement_percentage"], float)
        assert summary["maximum_improvement_percentage"] >= summary["minimum_improvement_percentage"]

    def test_metric_extraction_accuracy(self, analyzer):
        """Test metric value extraction accuracy from experiment results.

        Implements: TR-04 - Data extraction precision
        """
        # Create mock performance report
        mock_report = Mock()
        mock_report.details = [
            Mock(wall_time_ms=100.5, cpu_time_ms=90.3, memory_used_mb=45.7, success=True),
            Mock(wall_time_ms=105.2, cpu_time_ms=95.1, memory_used_mb=48.9, success=True),
        ]

        # Test wall time extraction
        values = analyzer._extract_performance_values(mock_report, "average_wall_time_ms")
        expected = [100.5, 105.2]
        assert values == expected

        # Test memory extraction
        values = analyzer._extract_performance_values(mock_report, "average_memory_mb")
        expected = [45.7, 48.9]
        assert values == expected

        # Test unknown metric
        values = analyzer._extract_performance_values(mock_report, "unknown_metric")
        assert values == []

    def test_determine_comparable_metrics(self, analyzer):
        """Test automatic metric determination for different experiment types.

        Implements: TR-04 - Metric selection accuracy
        """
        # Create mock experiments for different types
        performance_exp = Mock()
        performance_exp.config = Mock()
        performance_exp.config.experiment_type = Mock()
        performance_exp.config.experiment_type.value = "performance"

        ears_exp = Mock()
        ears_exp.config = Mock()
        ears_exp.config.experiment_type = Mock()
        ears_exp.config.experiment_type.value = "ears_coverage"

        language_exp = Mock()
        language_exp.config = Mock()
        language_exp.config.experiment_type = Mock()
        language_exp.config.experiment_type.value = "language_detection"

        unknown_exp = Mock()
        unknown_exp.config = Mock()
        unknown_exp.config.experiment_type = Mock()
        unknown_exp.config.experiment_type.value = "unknown_type"

        # Test metric determination
        perf_metrics = analyzer._determine_comparable_metrics(performance_exp)
        assert "average_wall_time_ms" in perf_metrics
        assert "average_cpu_time_ms" in perf_metrics
        assert "average_memory_mb" in perf_metrics
        assert "successful_executions" in perf_metrics

        ears_metrics = analyzer._determine_comparable_metrics(ears_exp)
        assert "coverage_rate" in ears_metrics
        assert "total_requirements" in ears_metrics
        assert "ears_compliant" in ears_metrics

        lang_metrics = analyzer._determine_comparable_metrics(language_exp)
        assert "accuracy_rate" in lang_metrics
        assert "japanese_accuracy" in lang_metrics
        assert "english_accuracy" in lang_metrics

        # Unknown type should default to duration_seconds
        unknown_metrics = analyzer._determine_comparable_metrics(unknown_exp)
        assert unknown_metrics == ["duration_seconds"]

    def test_ears_metric_extraction(self, analyzer):
        """Test EARS metric extraction accuracy.

        Implements: TR-01 - EARS analyzer unit test requirements
        """
        # Create mock EARS report
        mock_report = Mock()
        mock_report.coverage_rate = 0.85
        mock_report.total_requirements = 20
        mock_report.ears_compliant = 17

        # Test coverage rate extraction
        values = analyzer._extract_ears_values(mock_report, "coverage_rate")
        assert values == [0.85]

        # Test total requirements extraction
        values = analyzer._extract_ears_values(mock_report, "total_requirements")
        assert values == [20.0]

        # Test ears compliant extraction
        values = analyzer._extract_ears_values(mock_report, "ears_compliant")
        assert values == [17.0]

        # Test unknown metric
        values = analyzer._extract_ears_values(mock_report, "unknown_metric")
        assert values == []

    def test_language_metric_extraction(self, analyzer):
        """Test language detection metric extraction accuracy.

        Implements: TR-04 - Language detection precision requirements
        """
        # Create mock language detection report
        mock_report = Mock()
        mock_report.accuracy_rate = 0.92
        mock_report.japanese_accuracy = 0.88
        mock_report.english_accuracy = 0.96

        # Test accuracy rate extraction
        values = analyzer._extract_language_values(mock_report, "accuracy_rate")
        assert values == [0.92]

        # Test Japanese accuracy extraction
        values = analyzer._extract_language_values(mock_report, "japanese_accuracy")
        assert values == [0.88]

        # Test English accuracy extraction
        values = analyzer._extract_language_values(mock_report, "english_accuracy")
        assert values == [0.96]

        # Test unknown metric
        values = analyzer._extract_language_values(mock_report, "unknown_metric")
        assert values == []

    def test_simple_comparison_single_values(self, analyzer):
        """Test simple comparison for single value datasets.

        Implements: TR-04 - Statistical comparison edge cases
        """
        # Test single value comparison
        baseline_values = [10.5]
        comparison_values = [12.3]

        result = analyzer._simple_comparison(baseline_values, comparison_values)

        assert isinstance(result, StatisticalComparison)
        assert result.baseline_mean == 10.5
        assert result.comparison_mean == 12.3
        assert result.baseline_std == 0.0
        assert result.comparison_std == 0.0
        assert result.t_statistic == 0.0
        assert result.p_value == 1.0  # Not significant for single values
        assert result.degrees_of_freedom == 0
        assert result.effect_size == 0.0
        assert not result.is_significant

        # Confidence interval should equal the difference
        expected_diff = 12.3 - 10.5
        assert result.confidence_interval_lower == expected_diff
        assert result.confidence_interval_upper == expected_diff

    def test_empty_comparison_values(self, analyzer):
        """Test handling of empty comparison values.

        Implements: TR-04 - Edge case handling
        """
        baseline_values = []
        comparison_values = []

        result = analyzer._simple_comparison(baseline_values, comparison_values)

        assert result.baseline_mean == 0.0
        assert result.comparison_mean == 0.0
        assert result.confidence_interval_lower == 0.0
        assert result.confidence_interval_upper == 0.0

    def test_comparison_with_failed_metric_extraction(
        self, analyzer, baseline_performance_experiment, comparison_performance_experiment
    ):
        """Test behavior when metric extraction fails.

        Implements: TR-04 - Error handling in comparisons
        """
        # Mock _extract_metric_values to return empty lists
        analyzer._extract_metric_values = Mock(return_value=[])

        result = analyzer.compare_experiments(
            baseline_experiment=baseline_performance_experiment,
            comparison_experiments=[comparison_performance_experiment],
            metrics_to_compare=["nonexistent_metric"],
        )

        # Should handle gracefully with empty comparisons
        assert len(result.comparisons) == 0
        assert "No valid comparisons could be performed." in result.recommendations

    def test_recommendations_basic_functionality(self, analyzer):
        """Test basic recommendation generation functionality.

        Implements: TR-04 - Recommendation logic accuracy
        """
        # Test with empty comparisons
        recommendations = analyzer._generate_recommendations([])
        assert "No valid comparisons could be performed." in recommendations

        # Test improvement percentage calculation accuracy
        result = analyzer._calculate_improvement_percentage(100.0, 120.0)
        assert result == 20.0  # 20% improvement

        result = analyzer._calculate_improvement_percentage(100.0, 80.0)
        assert result == -20.0  # 20% degradation

    def test_no_significant_differences_recommendation(self, analyzer):
        """Test recommendation when no significant differences are found.

        Implements: TR-04 - Default recommendation handling
        """
        # Create mock comparison with no significant changes
        no_change = Mock()
        no_change.statistical_comparison = Mock()
        no_change.statistical_comparison.is_significant = False
        no_change.statistical_comparison.effect_size = 0.1  # Small effect
        no_change.statistical_comparison.baseline_std = 5.0
        no_change.statistical_comparison.baseline_mean = 100.0  # Low variability
        no_change.improvement_percentage = 1.0  # Small change
        no_change.metric_name = "test_metric"

        recommendations = analyzer._generate_recommendations([no_change])

        assert "No significant differences detected between experiments." in recommendations
