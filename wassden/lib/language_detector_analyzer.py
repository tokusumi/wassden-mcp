"""Language detector analyzer component for measuring language detection accuracy.

This module provides functionality to analyze documents and measure
language detection accuracy rates for Japanese and English documents.

Implements: REQ-03, TASK-02-03
"""

from pathlib import Path
from typing import Any

import pycld2 as cld2  # type: ignore

from wassden.lib.experiment import LanguageDetectionReport, LanguageDetectionResult
from wassden.lib.language_detection import (
    detect_language_from_content,
    detect_language_from_spec_content,
)
from wassden.lib.statistics_engine import StatisticsEngine
from wassden.types import Language

# Detection confidence thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.8  # 80% confidence threshold
MEDIUM_CONFIDENCE_THRESHOLD = 0.5  # 50% confidence threshold


class LanguageDetectorAnalyzerError(Exception):
    """Base exception for language detector analyzer errors."""


class DocumentAnalysisError(LanguageDetectorAnalyzerError):
    """Raised when document analysis fails."""


class InvalidDocumentError(LanguageDetectorAnalyzerError):
    """Raised when document format is invalid."""


class LanguageDetectorAnalyzer:
    """Analyzer for measuring language detection accuracy in documents."""

    def __init__(self) -> None:
        """Initialize language detector analyzer."""
        self.statistics_engine = StatisticsEngine()

    async def analyze_document(
        self, document_path: Path, expected_language: Language, is_spec_document: bool = False
    ) -> LanguageDetectionResult:
        """Analyze a single document for language detection accuracy.

        Args:
            document_path: Path to document
            expected_language: Expected language of the document
            is_spec_document: Whether document is a spec document

        Returns:
            Language detection result

        Raises:
            DocumentAnalysisError: If document cannot be analyzed
            InvalidDocumentError: If document format is invalid
            FileNotFoundError: If document does not exist

        Implements: REQ-03 - 言語検出精度測定
        """
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        try:
            # Read document content
            content = document_path.read_text(encoding="utf-8")

            # Detect language using appropriate method
            if is_spec_document:
                detected_lang = detect_language_from_spec_content(content)
            else:
                detected_lang = detect_language_from_content(content)

            # Get confidence score using pycld2
            confidence_score = self._get_confidence_score(content)

            # Check if detection is correct
            is_correct = detected_lang == expected_language

            return LanguageDetectionResult(
                document_path=document_path,
                expected_language=expected_language.value,
                detected_language=detected_lang.value,
                confidence_score=confidence_score,
                is_correct=is_correct,
            )

        except UnicodeDecodeError as e:
            raise DocumentAnalysisError(f"Failed to decode document {document_path}: {e}") from e
        except Exception as e:
            raise DocumentAnalysisError(f"Failed to analyze document {document_path}: {e}") from e

    def _get_confidence_score(self, content: str) -> float:
        """Get confidence score for language detection.

        Args:
            content: Document content

        Returns:
            Confidence score (0.0-1.0)

        Implements: REQ-03 - 観点2: 検出信頼度を数値で出力する
        """
        if not content:
            return 0.0

        try:
            # Use pycld2 to get detailed detection results
            is_reliable, _, details = cld2.detect(content)

            if not details:
                return 0.0

            # Get the confidence score from the primary detected language
            # details[0] = (languageName, languageCode, percent, score)
            primary_percent = details[0][2]  # percent of text in this language

            # Convert percent to confidence score (0.0-1.0)
            confidence = float(primary_percent) / 100.0

            # Adjust confidence based on reliability flag
            if not is_reliable:
                confidence *= 0.5  # Reduce confidence if not reliable

            return confidence

        except Exception:
            # If detection fails, return low confidence
            return 0.0

    async def analyze_documents(
        self, document_specs: list[tuple[Path, Language]], is_spec_document: bool = False
    ) -> list[LanguageDetectionResult]:
        """Analyze multiple documents for language detection accuracy.

        Args:
            document_specs: List of (document_path, expected_language) tuples
            is_spec_document: Whether documents are spec documents

        Returns:
            List of language detection results

        Raises:
            LanguageDetectorAnalyzerError: If analysis fails
        """
        if not document_specs:
            raise LanguageDetectorAnalyzerError("No documents provided for analysis")

        results = []
        failed_documents = []

        for doc_path, expected_lang in document_specs:
            try:
                result = await self.analyze_document(doc_path, expected_lang, is_spec_document)
                results.append(result)
            except Exception as e:
                failed_documents.append((doc_path, str(e)))
                # Continue processing other documents
                continue

        if failed_documents and not results:
            # All documents failed
            failed_list = [f"{path}: {error}" for path, error in failed_documents]
            raise LanguageDetectorAnalyzerError(f"All documents failed to analyze: {failed_list}")

        return results

    def generate_accuracy_report(self, results: list[LanguageDetectionResult]) -> LanguageDetectionReport:
        """Generate accuracy report from detection results.

        Args:
            results: List of language detection results

        Returns:
            Language detection accuracy report

        Raises:
            LanguageDetectorAnalyzerError: If no results provided

        Implements: REQ-03 - 観点1: 日本語・英語の検出結果を記録する
        """
        if not results:
            raise LanguageDetectorAnalyzerError("No results provided for report generation")

        # Calculate overall accuracy
        correct_count = sum(1 for r in results if r.is_correct)
        total_count = len(results)
        overall_accuracy = correct_count / total_count if total_count > 0 else 0.0

        # Calculate language-specific accuracy
        japanese_results = [r for r in results if r.expected_language == Language.JAPANESE.value]
        english_results = [r for r in results if r.expected_language == Language.ENGLISH.value]

        japanese_correct = sum(1 for r in japanese_results if r.is_correct)
        english_correct = sum(1 for r in english_results if r.is_correct)

        japanese_accuracy = japanese_correct / len(japanese_results) if japanese_results else 0.0
        english_accuracy = english_correct / len(english_results) if english_results else 0.0

        # Calculate confidence score statistics
        confidence_scores = [r.confidence_score for r in results]
        confidence_stats = self.statistics_engine.calculate_descriptive_stats(confidence_scores)

        return LanguageDetectionReport(
            results=results,
            accuracy_rate=overall_accuracy,
            japanese_accuracy=japanese_accuracy,
            english_accuracy=english_accuracy,
            statistics=confidence_stats,
        )

    async def measure_language_detection_accuracy(
        self, document_specs: list[tuple[Path, Language]], is_spec_document: bool = False
    ) -> dict[str, Any]:
        """Measure language detection accuracy for documents.

        Args:
            document_specs: List of (document_path, expected_language) tuples
            is_spec_document: Whether documents are spec documents

        Returns:
            Language detection accuracy measurement results

        Implements: REQ-03 - 言語検出精度測定機能
        """
        # Analyze all documents
        results = await self.analyze_documents(document_specs, is_spec_document)

        # Generate accuracy report
        report = self.generate_accuracy_report(results)

        # Prepare detailed results
        return {
            "summary": {
                "total_documents": len(results),
                "correct_detections": sum(1 for r in results if r.is_correct),
                "overall_accuracy": report.accuracy_rate,
                "japanese_accuracy": report.japanese_accuracy,
                "english_accuracy": report.english_accuracy,
            },
            "confidence_statistics": {
                "mean": report.statistics.mean,
                "std_dev": report.statistics.std_dev,
                "min": report.statistics.min_value,
                "max": report.statistics.max_value,
                "confidence_interval": report.statistics.confidence_interval,
            },
            "quality_metrics": {
                "high_confidence_count": sum(1 for r in results if r.confidence_score >= HIGH_CONFIDENCE_THRESHOLD),
                "medium_confidence_count": sum(
                    1 for r in results if MEDIUM_CONFIDENCE_THRESHOLD <= r.confidence_score < HIGH_CONFIDENCE_THRESHOLD
                ),
                "low_confidence_count": sum(1 for r in results if r.confidence_score < MEDIUM_CONFIDENCE_THRESHOLD),
            },
            "detailed_results": [
                {
                    "document": str(r.document_path),
                    "expected": r.expected_language,
                    "detected": r.detected_language,
                    "confidence": r.confidence_score,
                    "correct": r.is_correct,
                }
                for r in results
            ],
        }

    def validate_detection_accuracy(self, report: LanguageDetectionReport, required_accuracy: float = 0.9) -> bool:
        """Validate if detection accuracy meets requirements.

        Args:
            report: Language detection report
            required_accuracy: Required minimum accuracy (default 90%)

        Returns:
            True if accuracy meets requirements, False otherwise

        Implements: TR-03 - 言語検出精度が90%以上で検証されること
        """
        return report.accuracy_rate >= required_accuracy
