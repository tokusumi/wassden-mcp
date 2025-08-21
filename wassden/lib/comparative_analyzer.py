"""Comparative experiment analyzer for statistical comparison of experiment results.

This module provides functionality to compare multiple experiment results
and perform statistical analysis to determine significant differences.

Implements: REQ-07, TASK-02-06
"""

import math
from typing import Any

from scipy import stats

from wassden.lib.experiment import (
    ComparativeExperimentReport,
    ComparisonResult,
    ExperimentResult,
    StatisticalComparison,
)
from wassden.lib.statistics_engine import StatisticsEngine

# Statistical constants
SIGNIFICANCE_THRESHOLD = 0.05
LARGE_EFFECT_THRESHOLD = 0.8
MINIMUM_IMPROVEMENT_THRESHOLD = 5.0
HIGH_VARIABILITY_THRESHOLD = 0.3
MINIMUM_SAMPLES_FOR_TTEST = 2


class ComparativeAnalysisError(Exception):
    """Base exception for comparative analysis errors."""


class InsufficientDataError(ComparativeAnalysisError):
    """Raised when insufficient data for statistical analysis."""


class IncompatibleExperimentsError(ComparativeAnalysisError):
    """Raised when experiments are not compatible for comparison."""


class ComparativeAnalyzer:
    """Analyzer for comparative experiments with statistical testing."""

    def __init__(self) -> None:
        """Initialize comparative analyzer."""
        self.statistics_engine = StatisticsEngine()

    def compare_experiments(
        self,
        baseline_experiment: ExperimentResult,
        comparison_experiments: list[ExperimentResult],
        metrics_to_compare: list[str] | None = None,
    ) -> ComparativeExperimentReport:
        """Compare multiple experiments with statistical analysis.

        Args:
            baseline_experiment: Baseline experiment for comparison
            comparison_experiments: List of experiments to compare against baseline
            metrics_to_compare: Specific metrics to compare (default: all applicable)

        Returns:
            Comprehensive comparison report with statistical analysis

        Raises:
            InsufficientDataError: If not enough data for statistical analysis
            IncompatibleExperimentsError: If experiments cannot be compared

        Implements: REQ-07 - システムは、比較実験を実行するとき、複数の実験結果を比較分析すること
        """
        if not comparison_experiments:
            raise InsufficientDataError("At least one comparison experiment is required")

        # Validate experiment compatibility
        self._validate_experiment_compatibility(baseline_experiment, comparison_experiments)

        # Determine metrics to compare if not specified
        if metrics_to_compare is None:
            metrics_to_compare = self._determine_comparable_metrics(baseline_experiment)

        # Perform comparisons
        comparisons = []
        for comparison_exp in comparison_experiments:
            for metric in metrics_to_compare:
                comparison_result = self._compare_single_metric(baseline_experiment, comparison_exp, metric)
                if comparison_result:
                    comparisons.append(comparison_result)

        # Generate summary statistics
        summary_stats = self._generate_summary_statistics(comparisons)

        # Generate recommendations
        recommendations = self._generate_recommendations(comparisons)

        return ComparativeExperimentReport(
            baseline_experiment=baseline_experiment,
            comparison_experiments=comparison_experiments,
            comparisons=comparisons,
            summary_statistics=summary_stats,
            recommendations=recommendations,
        )

    def _validate_experiment_compatibility(
        self, baseline: ExperimentResult, comparisons: list[ExperimentResult]
    ) -> None:
        """Validate that experiments can be compared."""
        baseline_type = baseline.config.experiment_type

        for comp_exp in comparisons:
            if comp_exp.config.experiment_type != baseline_type:
                raise IncompatibleExperimentsError(
                    f"Experiment types don't match: {baseline_type} vs {comp_exp.config.experiment_type}"
                )

    def _determine_comparable_metrics(self, experiment: ExperimentResult) -> list[str]:
        """Determine which metrics can be compared for the experiment type."""
        experiment_type = experiment.config.experiment_type.value

        metric_mappings = {
            "ears_coverage": ["coverage_rate", "total_requirements", "ears_compliant"],
            "performance": [
                "average_wall_time_ms",
                "average_cpu_time_ms",
                "average_memory_mb",
                "successful_executions",
            ],
            "language_detection": ["accuracy_rate", "japanese_accuracy", "english_accuracy"],
        }

        return metric_mappings.get(experiment_type, ["duration_seconds"])

    def _compare_single_metric(
        self, baseline: ExperimentResult, comparison: ExperimentResult, metric_name: str
    ) -> ComparisonResult | None:
        """Compare a single metric between two experiments."""
        try:
            # Extract values for the metric
            baseline_values = self._extract_metric_values(baseline, metric_name)
            comparison_values = self._extract_metric_values(comparison, metric_name)

            if not baseline_values or not comparison_values:
                return None

            # Perform statistical comparison
            statistical_comparison = self._perform_statistical_test(baseline_values, comparison_values)

            # Calculate improvement percentage
            baseline_mean = sum(baseline_values) / len(baseline_values)
            comparison_mean = sum(comparison_values) / len(comparison_values)
            improvement_pct = self._calculate_improvement_percentage(baseline_mean, comparison_mean)

            return ComparisonResult(
                baseline_experiment_id=baseline.experiment_id,
                comparison_experiment_id=comparison.experiment_id,
                metric_name=metric_name,
                baseline_values=baseline_values,
                comparison_values=comparison_values,
                statistical_comparison=statistical_comparison,
                improvement_percentage=improvement_pct,
            )

        except Exception:
            # Skip metrics that can't be compared
            return None

    def _extract_metric_values(self, experiment: ExperimentResult, metric_name: str) -> list[float]:
        """Extract values for a specific metric from an experiment result."""
        # Handle special cases for duration
        if metric_name == "duration_seconds":
            return [experiment.duration_seconds]

        # Extract from type-specific reports
        if experiment.performance_report:
            return self._extract_performance_values(experiment.performance_report, metric_name)

        if experiment.ears_report:
            return self._extract_ears_values(experiment.ears_report, metric_name)

        if experiment.language_report:
            return self._extract_language_values(experiment.language_report, metric_name)

        return []

    def _extract_performance_values(self, report: Any, metric_name: str) -> list[float]:
        """Extract performance metric values."""
        performance_metrics = [
            "average_wall_time_ms",
            "average_cpu_time_ms",
            "average_memory_mb",
            "successful_executions",
        ]

        if metric_name not in performance_metrics:
            return []

        if metric_name == "average_wall_time_ms":
            return [detail.wall_time_ms for detail in report.details if detail.success]
        if metric_name == "average_cpu_time_ms":
            return [detail.cpu_time_ms for detail in report.details if detail.success]
        if metric_name == "average_memory_mb":
            return [detail.memory_used_mb for detail in report.details if detail.success]
        if metric_name == "successful_executions":
            return [float(report.successful_executions)]

        return []

    def _extract_ears_values(self, report: Any, metric_name: str) -> list[float]:
        """Extract EARS metric values."""
        ears_metrics = ["coverage_rate", "total_requirements", "ears_compliant"]

        if metric_name not in ears_metrics:
            return []

        if metric_name == "coverage_rate":
            return [report.coverage_rate]
        if metric_name == "total_requirements":
            return [float(report.total_requirements)]
        if metric_name == "ears_compliant":
            return [float(report.ears_compliant)]

        return []

    def _extract_language_values(self, report: Any, metric_name: str) -> list[float]:
        """Extract language detection metric values."""
        language_metrics = ["accuracy_rate", "japanese_accuracy", "english_accuracy"]

        if metric_name not in language_metrics:
            return []

        metric_handlers = {
            "accuracy_rate": lambda: [report.accuracy_rate],
            "japanese_accuracy": lambda: [report.japanese_accuracy],
            "english_accuracy": lambda: [report.english_accuracy],
        }

        if metric_name in metric_handlers:
            return metric_handlers[metric_name]()

        return []

    def _perform_statistical_test(
        self, baseline_values: list[float], comparison_values: list[float]
    ) -> StatisticalComparison:
        """Perform statistical t-test between two groups of values."""
        if len(baseline_values) < MINIMUM_SAMPLES_FOR_TTEST or len(comparison_values) < MINIMUM_SAMPLES_FOR_TTEST:
            # Use simple comparison for single values
            return self._simple_comparison(baseline_values, comparison_values)

        # Calculate basic statistics
        baseline_mean = sum(baseline_values) / len(baseline_values)
        comparison_mean = sum(comparison_values) / len(comparison_values)

        baseline_std = math.sqrt(sum((x - baseline_mean) ** 2 for x in baseline_values) / (len(baseline_values) - 1))
        comparison_std = math.sqrt(
            sum((x - comparison_mean) ** 2 for x in comparison_values) / (len(comparison_values) - 1)
        )

        # Perform t-test
        t_stat, p_value = stats.ttest_ind(baseline_values, comparison_values)

        # Calculate degrees of freedom
        n1, n2 = len(baseline_values), len(comparison_values)
        df = n1 + n2 - 2

        # Calculate Cohen's d effect size
        pooled_std = math.sqrt(((n1 - 1) * baseline_std**2 + (n2 - 1) * comparison_std**2) / df)
        cohens_d = (comparison_mean - baseline_mean) / pooled_std if pooled_std > 0 else 0.0

        # Calculate 95% confidence interval for the difference
        se_diff = pooled_std * math.sqrt(1 / n1 + 1 / n2)
        t_critical = stats.t.ppf(0.975, df)  # 95% CI
        diff_mean = comparison_mean - baseline_mean
        ci_lower = diff_mean - t_critical * se_diff
        ci_upper = diff_mean + t_critical * se_diff

        return StatisticalComparison(
            baseline_mean=baseline_mean,
            comparison_mean=comparison_mean,
            baseline_std=baseline_std,
            comparison_std=comparison_std,
            t_statistic=float(t_stat),
            p_value=float(p_value),
            degrees_of_freedom=df,
            effect_size=cohens_d,
            is_significant=bool(p_value < SIGNIFICANCE_THRESHOLD),
            confidence_interval_lower=ci_lower,
            confidence_interval_upper=ci_upper,
        )

    def _simple_comparison(self, baseline_values: list[float], comparison_values: list[float]) -> StatisticalComparison:
        """Create comparison for single values (no statistical test possible)."""
        baseline_mean = baseline_values[0] if baseline_values else 0.0
        comparison_mean = comparison_values[0] if comparison_values else 0.0

        return StatisticalComparison(
            baseline_mean=baseline_mean,
            comparison_mean=comparison_mean,
            baseline_std=0.0,
            comparison_std=0.0,
            t_statistic=0.0,
            p_value=1.0,  # Not significant for single values
            degrees_of_freedom=0,
            effect_size=0.0,
            is_significant=False,
            confidence_interval_lower=comparison_mean - baseline_mean,
            confidence_interval_upper=comparison_mean - baseline_mean,
        )

    def _generate_summary_statistics(self, comparisons: list[ComparisonResult]) -> dict[str, Any]:
        """Generate summary statistics across all comparisons."""
        if not comparisons:
            return {}

        significant_improvements = [
            c for c in comparisons if c.statistical_comparison.is_significant and c.improvement_percentage > 0
        ]
        significant_degradations = [
            c for c in comparisons if c.statistical_comparison.is_significant and c.improvement_percentage < 0
        ]

        avg_improvement = sum(c.improvement_percentage for c in comparisons) / len(comparisons)
        max_improvement = max((c.improvement_percentage for c in comparisons), default=0.0)
        min_improvement = min((c.improvement_percentage for c in comparisons), default=0.0)

        return {
            "total_comparisons": len(comparisons),
            "significant_improvements": len(significant_improvements),
            "significant_degradations": len(significant_degradations),
            "average_improvement_percentage": avg_improvement,
            "maximum_improvement_percentage": max_improvement,
            "minimum_improvement_percentage": min_improvement,
            "metrics_compared": list({c.metric_name for c in comparisons}),
        }

    def _generate_recommendations(self, comparisons: list[ComparisonResult]) -> list[str]:
        """Generate recommendations based on comparison results."""
        recommendations = []

        if not comparisons:
            recommendations.append("No valid comparisons could be performed.")
            return recommendations

        # Analyze significant changes
        significant_improvements = [
            c
            for c in comparisons
            if c.statistical_comparison.is_significant and c.improvement_percentage > MINIMUM_IMPROVEMENT_THRESHOLD
        ]
        significant_degradations = [
            c
            for c in comparisons
            if c.statistical_comparison.is_significant and c.improvement_percentage < -MINIMUM_IMPROVEMENT_THRESHOLD
        ]

        if significant_improvements:
            best_improvement = max(significant_improvements, key=lambda x: x.improvement_percentage)
            recommendations.append(
                f"Significant improvement detected in {best_improvement.metric_name}: "
                f"{best_improvement.improvement_percentage:.1f}% better than baseline."
            )

        if significant_degradations:
            worst_degradation = min(significant_degradations, key=lambda x: x.improvement_percentage)
            recommendations.append(
                f"Performance degradation detected in {worst_degradation.metric_name}: "
                f"{abs(worst_degradation.improvement_percentage):.1f}% worse than baseline."
            )

        # Large effect sizes
        large_effects = [c for c in comparisons if abs(c.statistical_comparison.effect_size) > LARGE_EFFECT_THRESHOLD]
        if large_effects:
            recommendations.append(
                f"Large effect sizes detected in {len(large_effects)} comparisons - consider investigating."
            )

        # High variability warning
        high_variability = [
            c
            for c in comparisons
            if c.statistical_comparison.baseline_std
            > c.statistical_comparison.baseline_mean * HIGH_VARIABILITY_THRESHOLD
        ]
        if high_variability:
            recommendations.append("High variability detected in some metrics - consider increasing sample size.")

        if not recommendations:
            recommendations.append("No significant differences detected between experiments.")

        return recommendations

    def _calculate_improvement_percentage(self, baseline_mean: float, comparison_mean: float) -> float:
        """Calculate improvement percentage between baseline and comparison."""
        if baseline_mean == 0:
            return 0.0
        return ((comparison_mean - baseline_mean) / baseline_mean) * 100.0
