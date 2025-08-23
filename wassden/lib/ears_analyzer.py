"""EARS analyzer component for measuring EARS compliance coverage.

This module provides functionality to analyze Markdown documents and measure
EARS pattern compliance rates for requirements documentation.

Implements: REQ-01, TASK-02-01
"""

from pathlib import Path
from typing import Any

from wassden.lib.experiment import EARSCoverageReport, EARSViolationDetail
from wassden.lib.language_detection import determine_language
from wassden.lib.validate_ears import EARSValidator, validate_ears_in_content

# Coverage rate thresholds
HIGH_COVERAGE_THRESHOLD = 0.9  # 90% coverage threshold


class EARSAnalyzerError(Exception):
    """Base exception for EARS analyzer errors."""


class DocumentParseError(EARSAnalyzerError):
    """Raised when document parsing fails."""


class InvalidMarkdownError(EARSAnalyzerError):
    """Raised when markdown format is invalid."""


class EARSAnalyzer:
    """Analyzer for measuring EARS compliance coverage in documents."""

    def __init__(self) -> None:
        """Initialize EARS analyzer."""
        self.validator = EARSValidator()

    async def analyze_document(self, document_path: Path) -> EARSCoverageReport:
        """Analyze a single document for EARS compliance.

        Args:
            document_path: Path to markdown document

        Returns:
            EARS coverage report

        Raises:
            DocumentParseError: If document cannot be parsed
            InvalidMarkdownError: If document format is invalid
            FileNotFoundError: If document does not exist

        Implements: REQ-01 - EARS適用率測定
        """
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        if document_path.suffix.lower() not in [".md", ".markdown"]:
            raise InvalidMarkdownError(f"Not a markdown file: {document_path}")

        try:
            # Read document content
            content = document_path.read_text(encoding="utf-8")

            # Detect language for proper validation
            language = determine_language(content=content, is_spec_document=True)

            # Validate EARS compliance
            validation_result = validate_ears_in_content(content, language)

            # Extract requirements and calculate coverage
            total_requirements = validation_result.total
            ears_compliant = validation_result.matched
            coverage_rate = validation_result.rate

            # Convert violations to detailed format
            violations = [
                EARSViolationDetail(
                    line_number=violation.line,
                    requirement_text=violation.text,
                    violation_type=violation.reason,
                    suggestion=None,  # EARSViolation doesn't have suggestion field
                )
                for violation in validation_result.violations
            ]

            return EARSCoverageReport(
                total_requirements=total_requirements,
                ears_compliant=ears_compliant,
                coverage_rate=coverage_rate,
                violations=violations,
                document_path=document_path,
            )

        except UnicodeDecodeError as e:
            raise DocumentParseError(f"Failed to decode document {document_path}: {e}") from e
        except Exception as e:
            raise DocumentParseError(f"Failed to analyze document {document_path}: {e}") from e

    async def analyze_documents(self, document_paths: list[Path]) -> list[EARSCoverageReport]:
        """Analyze multiple documents for EARS compliance.

        Args:
            document_paths: List of paths to markdown documents

        Returns:
            List of EARS coverage reports

        Raises:
            EARSAnalyzerError: If analysis fails
        """
        if not document_paths:
            raise EARSAnalyzerError("No documents provided for analysis")

        reports = []
        failed_documents = []

        for doc_path in document_paths:
            try:
                report = await self.analyze_document(doc_path)
                reports.append(report)
            except Exception as e:
                failed_documents.append((doc_path, str(e)))
                # Continue processing other documents
                continue

        if failed_documents and not reports:
            # All documents failed
            failed_list = [f"{path}: {error}" for path, error in failed_documents]
            raise EARSAnalyzerError(f"All documents failed to analyze: {failed_list}")

        return reports

    def aggregate_coverage_reports(self, reports: list[EARSCoverageReport]) -> dict[str, Any]:
        """Aggregate multiple EARS coverage reports into summary statistics.

        Args:
            reports: List of EARS coverage reports

        Returns:
            Aggregated coverage statistics

        Raises:
            EARSAnalyzerError: If no reports provided
        """
        if not reports:
            raise EARSAnalyzerError("No reports provided for aggregation")

        # Calculate aggregate statistics
        total_requirements = sum(report.total_requirements for report in reports)
        total_compliant = sum(report.ears_compliant for report in reports)
        overall_coverage_rate = total_compliant / total_requirements if total_requirements > 0 else 0.0

        # Collect all violations
        all_violations = []
        for report in reports:
            all_violations.extend(report.violations)

        # Calculate per-document statistics
        document_stats = [
            {
                "document_path": str(report.document_path),
                "total_requirements": report.total_requirements,
                "ears_compliant": report.ears_compliant,
                "coverage_rate": report.coverage_rate,
                "violation_count": len(report.violations),
            }
            for report in reports
        ]

        # Group violations by type
        violation_types = {}
        for violation in all_violations:
            vtype = violation.violation_type
            if vtype not in violation_types:
                violation_types[vtype] = 0
            violation_types[vtype] += 1

        return {
            "summary": {
                "total_documents": len(reports),
                "total_requirements": total_requirements,
                "total_compliant": total_compliant,
                "overall_coverage_rate": overall_coverage_rate,
                "total_violations": len(all_violations),
            },
            "document_statistics": document_stats,
            "violation_analysis": {
                "by_type": violation_types,
                "total_violations": len(all_violations),
            },
            "quality_metrics": {
                "documents_with_100_percent_coverage": len([r for r in reports if r.coverage_rate >= 1.0]),
                "documents_with_90_percent_coverage": len(
                    [r for r in reports if r.coverage_rate >= HIGH_COVERAGE_THRESHOLD]
                ),
                "average_coverage_rate": sum(r.coverage_rate for r in reports) / len(reports),
                "min_coverage_rate": min(r.coverage_rate for r in reports),
                "max_coverage_rate": max(r.coverage_rate for r in reports),
            },
        }

    async def measure_ears_coverage(
        self, document_paths: list[Path], output_detail_level: str = "summary"
    ) -> dict[str, Any]:
        """Measure EARS coverage for documents with configurable detail level.

        Args:
            document_paths: List of document paths to analyze
            output_detail_level: Level of detail ("summary", "detailed", "full")

        Returns:
            EARS coverage measurement results

        Implements: REQ-01 - 観点2: EARSパターン適合度を百分率で算出する
        """
        # Analyze all documents
        reports = await self.analyze_documents(document_paths)

        # Generate aggregated statistics
        aggregated_stats = self.aggregate_coverage_reports(reports)

        # Format output based on detail level
        if output_detail_level == "summary":
            return {
                "coverage_summary": aggregated_stats["summary"],
                "quality_metrics": aggregated_stats["quality_metrics"],
            }
        if output_detail_level == "detailed":
            return {
                "coverage_summary": aggregated_stats["summary"],
                "document_statistics": aggregated_stats["document_statistics"],
                "violation_analysis": aggregated_stats["violation_analysis"],
                "quality_metrics": aggregated_stats["quality_metrics"],
            }
        if output_detail_level == "full":
            # Include full reports with all violation details
            full_reports = [
                {
                    "document_path": str(report.document_path),
                    "total_requirements": report.total_requirements,
                    "ears_compliant": report.ears_compliant,
                    "coverage_rate": report.coverage_rate,
                    "violations": [
                        {
                            "line_number": v.line_number,
                            "requirement_text": v.requirement_text,
                            "violation_type": v.violation_type,
                            "suggestion": v.suggestion,
                        }
                        for v in report.violations
                    ],
                }
                for report in reports
            ]

            return {
                "coverage_summary": aggregated_stats["summary"],
                "document_reports": full_reports,
                "violation_analysis": aggregated_stats["violation_analysis"],
                "quality_metrics": aggregated_stats["quality_metrics"],
            }
        raise EARSAnalyzerError(f"Invalid output detail level: {output_detail_level}")
