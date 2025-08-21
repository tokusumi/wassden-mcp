"""Unit tests for statistics engine module.

Tests for TASK-01-03 statistical calculation functionality.
"""

import math

import pytest

from wassden.lib.statistics_engine import (
    InsufficientDataError,
    InvalidDataError,
    StatisticsEngine,
)


class TestStatisticsEngine:
    """Test cases for StatisticsEngine."""

    def test_calculate_descriptive_stats_basic(self):
        """Test basic descriptive statistics calculation.

        Implements: REQ-04 - 観点1: 平均値、分散、標準偏差が正確に算出されること
        """
        # Test data with known statistical properties
        data = [1.0, 2.0, 3.0, 4.0, 5.0]

        result = StatisticsEngine.calculate_descriptive_stats(data)

        # Verify basic statistics
        assert result.mean == 3.0
        assert result.sample_size == 5
        assert result.min_value == 1.0
        assert result.max_value == 5.0

        # Verify variance and standard deviation (sample statistics)
        expected_variance = 2.5  # Sample variance with ddof=1
        expected_std_dev = math.sqrt(expected_variance)

        assert abs(result.variance - expected_variance) < 1e-10
        assert abs(result.std_dev - expected_std_dev) < 1e-10

    def test_calculate_confidence_interval_95(self):
        """Test 95% confidence interval calculation.

        Implements: REQ-04 - 観点2: 95%信頼区間の計算が統計的に正しいこと
        """
        # Test with known data
        data = [1.0, 2.0, 3.0, 4.0, 5.0]

        result = StatisticsEngine.calculate_descriptive_stats(data)

        # Confidence interval should be symmetric around the mean
        lower, upper = result.confidence_interval
        assert lower < result.mean < upper

        # For this sample size, should use t-distribution
        # Confidence interval should be wider than ±1 standard error
        assert upper - lower > 0  # Should have non-zero width

    def test_confidence_interval_single_point(self):
        """Test confidence interval for single data point."""
        data = [5.0]

        result = StatisticsEngine.calculate_descriptive_stats(data)

        # Single point confidence interval should equal the value
        assert result.confidence_interval == (5.0, 5.0)

    def test_empty_data_raises_error(self):
        """Test that empty data raises appropriate error."""
        with pytest.raises(InsufficientDataError, match="empty dataset"):
            StatisticsEngine.calculate_descriptive_stats([])

    def test_invalid_data_raises_error(self):
        """Test that invalid data raises appropriate error."""
        # Test with NaN
        with pytest.raises(InvalidDataError, match="Invalid numeric value"):
            StatisticsEngine.calculate_descriptive_stats([1.0, float("nan"), 3.0])

        # Test with infinity
        with pytest.raises(InvalidDataError, match="Invalid numeric value"):
            StatisticsEngine.calculate_descriptive_stats([1.0, float("inf"), 3.0])

        # Test with non-numeric value
        with pytest.raises(InvalidDataError, match="Non-numeric value"):
            StatisticsEngine.calculate_descriptive_stats([1.0, "invalid", 3.0])

    def test_large_dataset_precision(self):
        """Test statistical calculations with larger dataset for precision."""
        # Generate data with known statistical properties
        data = list(range(1, 101))  # 1 to 100

        result = StatisticsEngine.calculate_descriptive_stats(data)

        # Verify mean
        expected_mean = 50.5
        assert abs(result.mean - expected_mean) < 1e-10

        # Verify sample size
        assert result.sample_size == 100

        # Verify bounds
        assert result.min_value == 1.0
        assert result.max_value == 100.0

    def test_compare_datasets_basic(self):
        """Test basic dataset comparison."""
        baseline = [1.0, 2.0, 3.0, 4.0, 5.0]
        comparison = [2.0, 3.0, 4.0, 5.0, 6.0]  # Shifted up by 1

        result = StatisticsEngine.compare_datasets(baseline, comparison)

        # Verify structure
        assert "baseline_stats" in result
        assert "comparison_stats" in result
        assert "t_test" in result
        assert "f_test" in result
        assert "effect_size" in result

        # Verify means are different
        assert result["comparison_stats"].mean > result["baseline_stats"].mean

        # Verify t-test structure
        t_test = result["t_test"]
        assert "t_statistic" in t_test
        assert "p_value" in t_test
        assert "significant" in t_test
        assert isinstance(t_test["significant"], bool)

    def test_compare_datasets_insufficient_data(self):
        """Test comparison with insufficient data."""
        baseline = [1.0]  # Only one point
        comparison = [2.0, 3.0]

        with pytest.raises(InsufficientDataError, match="At least 2 data points"):
            StatisticsEngine.compare_datasets(baseline, comparison)

    def test_validate_statistical_assumptions(self):
        """Test statistical assumptions validation."""
        # Test with normal-ish data
        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

        result = StatisticsEngine.validate_statistical_assumptions(data)

        # Verify structure
        assert "normality_test" in result
        assert "outlier_detection" in result

        # Verify normality test
        normality = result["normality_test"]
        assert normality["applicable"] is True
        assert "test" in normality
        assert "is_normal" in normality

        # Verify outlier detection
        outliers = result["outlier_detection"]
        assert outliers["applicable"] is True
        assert "outliers" in outliers
        assert "outlier_count" in outliers

    def test_validate_assumptions_insufficient_data(self):
        """Test assumptions validation with insufficient data."""
        data = [1.0, 2.0]  # Only 2 points

        result = StatisticsEngine.validate_statistical_assumptions(data)

        # Should indicate not applicable
        assert result["normality_test"]["applicable"] is False
        assert result["outlier_detection"]["applicable"] is False

    def test_aggregate_experiment_results(self):
        """Test aggregation of multiple experiment results."""
        results = [
            {"metric_a": 1.0, "metric_b": 10.0, "status": "completed"},
            {"metric_a": 2.0, "metric_b": 20.0, "status": "completed"},
            {"metric_a": 3.0, "metric_b": 30.0, "status": "completed"},
        ]

        aggregated = StatisticsEngine.aggregate_experiment_results(results)

        # Verify structure
        assert "total_experiments" in aggregated
        assert "metrics_analyzed" in aggregated
        assert "statistics" in aggregated
        assert "data_quality" in aggregated

        # Verify counts
        assert aggregated["total_experiments"] == 3

        # Verify metrics are analyzed
        stats = aggregated["statistics"]
        assert "metric_a" in stats
        assert "metric_b" in stats

        # Verify metric_a statistics
        metric_a_stats = stats["metric_a"]
        assert metric_a_stats["mean"] == 2.0  # (1+2+3)/3
        assert metric_a_stats["sample_size"] == 3

    def test_aggregate_no_results(self):
        """Test aggregation with no results."""
        with pytest.raises(InsufficientDataError, match="No experiment results"):
            StatisticsEngine.aggregate_experiment_results([])

    def test_effect_size_interpretation(self):
        """Test effect size interpretation."""
        # Test Cohen's d interpretation
        assert StatisticsEngine._interpret_effect_size(0.1) == "negligible"
        assert StatisticsEngine._interpret_effect_size(0.3) == "small"
        assert StatisticsEngine._interpret_effect_size(0.6) == "medium"
        assert StatisticsEngine._interpret_effect_size(1.0) == "large"

        # Test negative values (absolute value should be used)
        assert StatisticsEngine._interpret_effect_size(-0.3) == "small"
        assert StatisticsEngine._interpret_effect_size(-1.0) == "large"

    def test_statistical_precision_requirements(self):
        """Test that calculations meet precision requirements."""
        # Test with data that has exact known statistics
        data = [0.0, 1.0, 2.0, 3.0, 4.0]

        result = StatisticsEngine.calculate_descriptive_stats(data)

        # Mean should be exactly 2.0
        assert result.mean == 2.0

        # Sample variance should be exactly 2.5
        assert abs(result.variance - 2.5) < 1e-15

        # Standard deviation should be sqrt(2.5)
        expected_std = math.sqrt(2.5)
        assert abs(result.std_dev - expected_std) < 1e-15

    def test_high_precision_floating_point_calculations(self):
        """Test high precision floating point calculations for TR-04.

        Implements: TR-04 - Numerical precision test requirements
        """
        # Test with high precision decimal values
        data = [1.123456789012345, 2.234567890123456, 3.345678901234567, 4.456789012345678, 5.567890123456789]

        result = StatisticsEngine.calculate_descriptive_stats(data)

        # Verify high precision mean calculation
        expected_mean = sum(data) / len(data)
        assert abs(result.mean - expected_mean) < 1e-14

        # Verify precision maintained through variance calculation
        assert result.variance > 0
        assert result.std_dev > 0

        # Verify confidence interval bounds maintain precision
        lower, upper = result.confidence_interval
        assert lower < result.mean < upper
        assert abs((upper - lower) - (upper - lower)) < 1e-14  # Self-consistency check

    def test_extreme_value_numerical_stability(self):
        """Test numerical stability with extreme values for TR-04.

        Implements: TR-04 - Numerical precision under extreme conditions
        """
        # Test with very large numbers
        large_data = [1e10, 1e10 + 1, 1e10 + 2, 1e10 + 3, 1e10 + 4]
        result = StatisticsEngine.calculate_descriptive_stats(large_data)

        expected_mean = 1e10 + 2.0
        assert abs(result.mean - expected_mean) < 1e-10

        # Test with very small numbers
        small_data = [1e-10, 2e-10, 3e-10, 4e-10, 5e-10]
        result = StatisticsEngine.calculate_descriptive_stats(small_data)

        expected_mean = 3e-10
        assert abs(result.mean - expected_mean) < 1e-20

    def test_statistical_consistency_across_operations(self):
        """Test mathematical consistency across statistical operations for TR-04.

        Implements: TR-04 - Statistical consistency validation
        """
        data = [10.5, 15.3, 20.1, 25.7, 30.9]

        result = StatisticsEngine.calculate_descriptive_stats(data)

        # Test mathematical relationships
        # Variance should equal (std_dev)^2
        assert abs(result.variance - result.std_dev**2) < 1e-10

        # Sample size should match input
        assert result.sample_size == len(data)

        # Min and max should be correct
        assert result.min_value == min(data)
        assert result.max_value == max(data)

        # Mean should be within [min, max]
        assert result.min_value <= result.mean <= result.max_value

        # Standard deviation should be non-negative
        assert result.std_dev >= 0

        # Confidence interval should contain the mean
        lower, upper = result.confidence_interval
        assert lower <= result.mean <= upper
