"""Statistics calculation engine for wassden experiment framework.

This module provides statistical analysis functionality including descriptive statistics,
confidence intervals, and statistical tests for experiment data analysis.

Implements: REQ-04, TASK-01-03
"""

import math
from typing import Any

import numpy as np
from scipy import stats

from wassden.lib.experiment import StatisticalSummary

# Statistical constants
MIN_SAMPLE_SIZE_FOR_CI = 2  # Minimum samples for confidence interval
SMALL_SAMPLE_THRESHOLD = 30  # Threshold for using t-distribution vs normal
MIN_COMPARISON_SAMPLES = 2  # Minimum samples for comparative analysis
MIN_NORMALITY_TEST_SAMPLES = 3  # Minimum samples for normality testing
SHAPIRO_WILK_THRESHOLD = 50  # Use Shapiro-Wilk for n < 50, Anderson-Darling for n >= 50
SIGNIFICANCE_LEVEL = 0.05  # Standard significance level (95% confidence)

# Cohen's d effect size thresholds (standard values in statistics)
COHEN_D_NEGLIGIBLE = 0.2
COHEN_D_SMALL = 0.5
COHEN_D_MEDIUM = 0.8


class StatisticsEngineError(Exception):
    """Base exception for statistics engine errors."""


class InsufficientDataError(StatisticsEngineError):
    """Raised when insufficient data is provided for statistical calculations."""


class InvalidDataError(StatisticsEngineError):
    """Raised when invalid data is provided for calculations."""


class StatisticsEngine:
    """Engine for statistical calculations and analysis."""

    @staticmethod
    def calculate_descriptive_stats(data: list[float]) -> StatisticalSummary:
        """Calculate descriptive statistics for numerical data.

        Args:
            data: List of numerical values

        Returns:
            Statistical summary containing mean, variance, std_dev, etc.

        Raises:
            InsufficientDataError: If data is empty or has insufficient samples
            InvalidDataError: If data contains invalid values

        Implements: REQ-04 - 観点1: 平均値、分散、標準偏差を算出する
        """
        if not data:
            raise InsufficientDataError("Cannot calculate statistics for empty dataset")

        if len(data) < 1:
            raise InsufficientDataError("At least 1 data point is required")

        # Validate data - check for NaN, inf, or non-numeric values
        clean_data = []
        for value in data:
            if not isinstance(value, int | float):
                raise InvalidDataError(f"Non-numeric value found: {value}")
            if math.isnan(value) or math.isinf(value):
                raise InvalidDataError(f"Invalid numeric value found: {value}")
            clean_data.append(float(value))

        # Calculate descriptive statistics using numpy for precision
        np_data = np.array(clean_data)

        mean = float(np.mean(np_data))
        variance = float(np.var(np_data, ddof=1)) if len(clean_data) > 1 else 0.0
        std_dev = float(np.std(np_data, ddof=1)) if len(clean_data) > 1 else 0.0
        min_value = float(np.min(np_data))
        max_value = float(np.max(np_data))

        # Calculate 95% confidence interval
        confidence_interval = StatisticsEngine._calculate_confidence_interval(clean_data, confidence_level=0.95)

        return StatisticalSummary(
            mean=mean,
            variance=variance,
            std_dev=std_dev,
            confidence_interval=confidence_interval,
            sample_size=len(clean_data),
            min_value=min_value,
            max_value=max_value,
        )

    @staticmethod
    def _calculate_confidence_interval(data: list[float], confidence_level: float = 0.95) -> tuple[float, float]:
        """Calculate confidence interval for the mean.

        Args:
            data: List of numerical values
            confidence_level: Confidence level (default 0.95 for 95%)

        Returns:
            Tuple of (lower_bound, upper_bound)

        Implements: REQ-04 - 観点2: 信頼区間を95%水準で算出する
        """
        if len(data) < MIN_SAMPLE_SIZE_FOR_CI:
            # For single data point, confidence interval equals the value
            value = data[0] if data else 0.0
            return (value, value)

        n = len(data)
        mean = np.mean(data)
        sem = stats.sem(data)  # Standard error of the mean

        # Use t-distribution for small samples, normal for large samples
        if n < SMALL_SAMPLE_THRESHOLD:
            # t-distribution for small samples
            t_critical = stats.t.ppf((1 + confidence_level) / 2, n - 1)
            margin_of_error = t_critical * sem
        else:
            # Normal distribution for large samples
            z_critical = stats.norm.ppf((1 + confidence_level) / 2)
            margin_of_error = z_critical * sem

        lower_bound = float(mean - margin_of_error)
        upper_bound = float(mean + margin_of_error)

        return (lower_bound, upper_bound)

    @staticmethod
    def compare_datasets(
        baseline_data: list[float], comparison_data: list[float], alpha: float = 0.05
    ) -> dict[str, Any]:
        """Compare two datasets using statistical tests.

        Args:
            baseline_data: Baseline dataset
            comparison_data: Comparison dataset
            alpha: Significance level for statistical tests

        Returns:
            Dictionary containing comparison results

        Raises:
            InsufficientDataError: If either dataset is too small

        Implements: REQ-07 support for comparative analysis
        """
        if len(baseline_data) < MIN_COMPARISON_SAMPLES or len(comparison_data) < MIN_COMPARISON_SAMPLES:
            raise InsufficientDataError("At least 2 data points required in each dataset for comparison")

        # Calculate statistics for both datasets
        baseline_stats = StatisticsEngine.calculate_descriptive_stats(baseline_data)
        comparison_stats = StatisticsEngine.calculate_descriptive_stats(comparison_data)

        # Perform t-test to check for significant difference
        t_statistic, p_value = stats.ttest_ind(baseline_data, comparison_data)

        # Perform F-test for variance comparison
        f_statistic = np.var(comparison_data, ddof=1) / np.var(baseline_data, ddof=1)
        f_p_value = 2 * min(
            stats.f.cdf(f_statistic, len(comparison_data) - 1, len(baseline_data) - 1),
            1 - stats.f.cdf(f_statistic, len(comparison_data) - 1, len(baseline_data) - 1),
        )

        # Calculate effect size (Cohen's d)
        pooled_std = math.sqrt(
            (
                (len(baseline_data) - 1) * baseline_stats.variance
                + (len(comparison_data) - 1) * comparison_stats.variance
            )
            / (len(baseline_data) + len(comparison_data) - 2)
        )
        cohens_d = (comparison_stats.mean - baseline_stats.mean) / pooled_std if pooled_std > 0 else 0.0

        return {
            "baseline_stats": baseline_stats,
            "comparison_stats": comparison_stats,
            "t_test": {
                "t_statistic": float(t_statistic),
                "p_value": float(p_value),
                "significant": bool(p_value < alpha),
                "alpha": alpha,
            },
            "f_test": {
                "f_statistic": float(f_statistic),
                "p_value": float(f_p_value),
                "significant": bool(f_p_value < alpha),
                "alpha": alpha,
            },
            "effect_size": {
                "cohens_d": float(cohens_d),
                "interpretation": StatisticsEngine._interpret_effect_size(cohens_d),
            },
        }

    @staticmethod
    def _interpret_effect_size(cohens_d: float) -> str:
        """Interpret Cohen's d effect size.

        Args:
            cohens_d: Cohen's d value

        Returns:
            Interpretation string
        """
        abs_d = abs(cohens_d)
        if abs_d < COHEN_D_NEGLIGIBLE:
            return "negligible"
        if abs_d < COHEN_D_SMALL:
            return "small"
        if abs_d < COHEN_D_MEDIUM:
            return "medium"
        return "large"

    @staticmethod
    def validate_statistical_assumptions(data: list[float]) -> dict[str, Any]:
        """Validate statistical assumptions for the dataset.

        Args:
            data: Dataset to validate

        Returns:
            Dictionary containing validation results
        """
        if len(data) < MIN_NORMALITY_TEST_SAMPLES:
            return {
                "normality_test": {"applicable": False, "reason": "Insufficient data (n < 3)"},
                "outlier_detection": {"applicable": False, "reason": "Insufficient data (n < 3)"},
            }

        results = {}

        # Normality test (Shapiro-Wilk for n < 50, Anderson-Darling for n >= 50)
        if len(data) < SHAPIRO_WILK_THRESHOLD:
            stat, p_value = stats.shapiro(data)
            results["normality_test"] = {
                "test": "shapiro_wilk",
                "statistic": float(stat),
                "p_value": float(p_value),
                "is_normal": p_value > SIGNIFICANCE_LEVEL,
                "applicable": True,
            }
        else:
            result = stats.anderson(data, dist="norm")
            critical_value = result.critical_values[2]  # 5% significance level
            results["normality_test"] = {
                "test": "anderson_darling",
                "statistic": float(result.statistic),
                "critical_value": float(critical_value),
                "is_normal": result.statistic < critical_value,
                "applicable": True,
            }

        # Outlier detection using IQR method
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = [x for x in data if x < lower_bound or x > upper_bound]

        results["outlier_detection"] = {
            "method": "IQR",
            "lower_bound": float(lower_bound),
            "upper_bound": float(upper_bound),
            "outliers": outliers,
            "outlier_count": len(outliers),
            "outlier_percentage": len(outliers) / len(data) * 100,
            "applicable": True,
        }

        return results

    @staticmethod
    def aggregate_experiment_results(results: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate multiple experiment results with statistical analysis.

        Args:
            results: List of experiment result dictionaries

        Returns:
            Aggregated statistical summary

        Raises:
            InsufficientDataError: If no results provided
        """
        if not results:
            raise InsufficientDataError("No experiment results provided for aggregation")

        # Extract numerical metrics from results
        metrics: dict[str, list[float]] = {}
        for result in results:
            for key, value in result.items():
                if isinstance(value, int | float) and not math.isnan(value) and not math.isinf(value):
                    if key not in metrics:
                        metrics[key] = []
                    metrics[key].append(float(value))

        if not metrics:
            raise InvalidDataError("No valid numerical metrics found in experiment results")

        # Calculate statistics for each metric
        aggregated_stats = {}
        for metric_name, values in metrics.items():
            if len(values) >= 1:
                try:
                    stats_summary = StatisticsEngine.calculate_descriptive_stats(values)
                    aggregated_stats[metric_name] = stats_summary.model_dump()
                except (InsufficientDataError, InvalidDataError) as e:
                    aggregated_stats[metric_name] = {"error": str(e)}

        return {
            "total_experiments": len(results),
            "metrics_analyzed": list(metrics.keys()),
            "statistics": aggregated_stats,
            "data_quality": {
                "complete_experiments": len(results),
                "metrics_with_valid_data": len([k for k, v in aggregated_stats.items() if "error" not in v]),
            },
        }
