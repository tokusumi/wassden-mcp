"""Unit tests for language detector analyzer module.

Tests for TASK-02-03 language detection accuracy measurement functionality.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from wassden.lib.experiment import LanguageDetectionResult, StatisticalSummary
from wassden.lib.language_detector_analyzer import (
    DocumentAnalysisError,
    LanguageDetectorAnalyzer,
    LanguageDetectorAnalyzerError,
)
from wassden.types import Language

pytestmark = pytest.mark.dev


@pytest.mark.dev
class TestLanguageDetectorAnalyzer:
    """Test cases for LanguageDetectorAnalyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create LanguageDetectorAnalyzer instance."""
        return LanguageDetectorAnalyzer()

    @pytest.fixture
    def sample_japanese_document(self):
        """Create a sample Japanese document."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("""# プロジェクト仕様書

## 概要
このプロジェクトは日本語の文書検出精度を測定するためのものです。

## 機能要件
- 日本語文書の検出
- 検出精度の測定
- 信頼度スコアの算出

## 非機能要件
- 90%以上の検出精度
- リアルタイム処理
""")
            return Path(f.name)

    @pytest.fixture
    def sample_english_document(self):
        """Create a sample English document."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("""# Project Specification

## Overview
This project is designed to measure the accuracy of English document detection.

## Functional Requirements
- Detect English documents
- Measure detection accuracy
- Calculate confidence scores

## Non-Functional Requirements
- Detection accuracy above 90%
- Real-time processing
""")
            return Path(f.name)

    @pytest.mark.asyncio
    async def test_analyze_document_japanese_success(self, analyzer, sample_japanese_document):
        """Test successful Japanese document analysis.

        Implements: REQ-03 - 観点1: 日本語・英語の検出結果を記録する
        """
        try:
            result = await analyzer.analyze_document(sample_japanese_document, Language.JAPANESE, is_spec_document=True)

            assert isinstance(result, LanguageDetectionResult)
            assert result.document_path == sample_japanese_document
            assert result.expected_language == Language.JAPANESE.value
            assert result.detected_language == Language.JAPANESE.value
            assert result.is_correct is True
            assert 0.0 <= result.confidence_score <= 1.0
        finally:
            sample_japanese_document.unlink()

    @pytest.mark.asyncio
    async def test_analyze_document_english_success(self, analyzer, sample_english_document):
        """Test successful English document analysis.

        Implements: REQ-03 - 観点1: 日本語・英語の検出結果を記録する
        """
        try:
            result = await analyzer.analyze_document(sample_english_document, Language.ENGLISH, is_spec_document=True)

            assert isinstance(result, LanguageDetectionResult)
            assert result.document_path == sample_english_document
            assert result.expected_language == Language.ENGLISH.value
            assert result.detected_language == Language.ENGLISH.value
            assert result.is_correct is True
            assert 0.0 <= result.confidence_score <= 1.0
        finally:
            sample_english_document.unlink()

    @pytest.mark.asyncio
    async def test_analyze_document_file_not_found(self, analyzer):
        """Test document analysis with non-existent file."""
        non_existent_path = Path("/non/existent/file.md")

        with pytest.raises(FileNotFoundError, match="Document not found"):
            await analyzer.analyze_document(non_existent_path, Language.JAPANESE)

    @pytest.mark.asyncio
    async def test_analyze_document_decode_error(self, analyzer):
        """Test document analysis with decode error."""
        # Create a file with invalid encoding
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False) as f:
            f.write(b"\x80\x81\x82\x83")  # Invalid UTF-8 bytes
            bad_file = Path(f.name)

        try:
            with pytest.raises(DocumentAnalysisError, match="Failed to decode document"):
                await analyzer.analyze_document(bad_file, Language.JAPANESE)
        finally:
            bad_file.unlink()

    def test_get_confidence_score_high_confidence(self, analyzer):
        """Test confidence score calculation for high confidence detection.

        Implements: REQ-03 - 観点2: 検出信頼度を数値で出力する
        """
        # Mock pycld2.detect to return high confidence result
        with patch("wassden.lib.language_detector_analyzer.cld2.detect") as mock_detect:
            mock_detect.return_value = (
                True,  # is_reliable
                100,  # text_bytes_found
                [("Japanese", "ja", 95, 1000)],  # 95% Japanese
            )

            score = analyzer._get_confidence_score("これは日本語のテキストです。")
            assert score == 0.95  # 95% confidence

    def test_get_confidence_score_low_confidence(self, analyzer):
        """Test confidence score calculation for low confidence detection."""
        # Mock pycld2.detect to return low confidence result
        with patch("wassden.lib.language_detector_analyzer.cld2.detect") as mock_detect:
            mock_detect.return_value = (
                False,  # not reliable
                100,  # text_bytes_found
                [("English", "en", 60, 500)],  # 60% English
            )

            score = analyzer._get_confidence_score("Mixed content here")
            assert score == 0.3  # 60% * 0.5 (unreliable penalty)

    def test_get_confidence_score_empty_content(self, analyzer):
        """Test confidence score for empty content."""
        score = analyzer._get_confidence_score("")
        assert score == 0.0

    def test_get_confidence_score_detection_failure(self, analyzer):
        """Test confidence score when detection fails."""
        with patch("wassden.lib.language_detector_analyzer.cld2.detect", side_effect=Exception("Detection failed")):
            score = analyzer._get_confidence_score("Some text")
            assert score == 0.0

    @pytest.mark.asyncio
    async def test_analyze_documents_success(self, analyzer, sample_japanese_document, sample_english_document):
        """Test analyzing multiple documents."""
        try:
            document_specs = [
                (sample_japanese_document, Language.JAPANESE),
                (sample_english_document, Language.ENGLISH),
            ]

            results = await analyzer.analyze_documents(document_specs, is_spec_document=True)

            assert len(results) == 2
            assert all(isinstance(r, LanguageDetectionResult) for r in results)
            assert results[0].expected_language == Language.JAPANESE.value
            assert results[1].expected_language == Language.ENGLISH.value
        finally:
            sample_japanese_document.unlink()
            sample_english_document.unlink()

    @pytest.mark.asyncio
    async def test_analyze_documents_empty_list(self, analyzer):
        """Test analyzing empty document list."""
        with pytest.raises(LanguageDetectorAnalyzerError, match="No documents provided"):
            await analyzer.analyze_documents([])

    @pytest.mark.asyncio
    async def test_analyze_documents_partial_failure(self, analyzer, sample_japanese_document):
        """Test analyzing documents with partial failures."""
        try:
            non_existent = Path("/non/existent/file.md")
            document_specs = [
                (sample_japanese_document, Language.JAPANESE),
                (non_existent, Language.ENGLISH),
            ]

            results = await analyzer.analyze_documents(document_specs, is_spec_document=True)

            # Should continue with successful documents
            assert len(results) == 1
            assert results[0].document_path == sample_japanese_document
        finally:
            sample_japanese_document.unlink()

    def test_generate_accuracy_report_success(self, analyzer):
        """Test generating accuracy report from results."""
        # Create mock results
        results = [
            LanguageDetectionResult(
                document_path=Path("doc1.md"),
                expected_language="ja",
                detected_language="ja",
                confidence_score=0.95,
                is_correct=True,
            ),
            LanguageDetectionResult(
                document_path=Path("doc2.md"),
                expected_language="en",
                detected_language="en",
                confidence_score=0.90,
                is_correct=True,
            ),
            LanguageDetectionResult(
                document_path=Path("doc3.md"),
                expected_language="ja",
                detected_language="en",
                confidence_score=0.60,
                is_correct=False,
            ),
        ]

        report = analyzer.generate_accuracy_report(results)

        assert report.accuracy_rate == 2 / 3  # 2 correct out of 3
        assert report.japanese_accuracy == 0.5  # 1 correct out of 2 Japanese
        assert report.english_accuracy == 1.0  # 1 correct out of 1 English
        assert len(report.results) == 3
        assert isinstance(report.statistics, StatisticalSummary)

    def test_generate_accuracy_report_empty_results(self, analyzer):
        """Test generating report with empty results."""
        with pytest.raises(LanguageDetectorAnalyzerError, match="No results provided"):
            analyzer.generate_accuracy_report([])

    @pytest.mark.asyncio
    async def test_measure_language_detection_accuracy(
        self, analyzer, sample_japanese_document, sample_english_document
    ):
        """Test complete accuracy measurement workflow."""
        try:
            document_specs = [
                (sample_japanese_document, Language.JAPANESE),
                (sample_english_document, Language.ENGLISH),
            ]

            result = await analyzer.measure_language_detection_accuracy(document_specs, is_spec_document=True)

            assert "summary" in result
            assert "confidence_statistics" in result
            assert "quality_metrics" in result
            assert "detailed_results" in result

            summary = result["summary"]
            assert summary["total_documents"] == 2
            assert 0.0 <= summary["overall_accuracy"] <= 1.0
            assert 0.0 <= summary["japanese_accuracy"] <= 1.0
            assert 0.0 <= summary["english_accuracy"] <= 1.0

            # Check detailed results
            assert len(result["detailed_results"]) == 2
            for detail in result["detailed_results"]:
                assert "document" in detail
                assert "expected" in detail
                assert "detected" in detail
                assert "confidence" in detail
                assert "correct" in detail
        finally:
            sample_japanese_document.unlink()
            sample_english_document.unlink()

    def test_validate_detection_accuracy_success(self, analyzer):
        """Test validation of detection accuracy - passing case.

        Implements: TR-03 - 言語検出精度が90%以上で検証されること
        """
        # Create mock report with high accuracy
        mock_report = MagicMock()
        mock_report.accuracy_rate = 0.92

        assert analyzer.validate_detection_accuracy(mock_report, required_accuracy=0.9) is True

    def test_validate_detection_accuracy_failure(self, analyzer):
        """Test validation of detection accuracy - failing case."""
        # Create mock report with low accuracy
        mock_report = MagicMock()
        mock_report.accuracy_rate = 0.85

        assert analyzer.validate_detection_accuracy(mock_report, required_accuracy=0.9) is False

    def test_validate_detection_accuracy_exact_threshold(self, analyzer):
        """Test validation at exact threshold."""
        mock_report = MagicMock()
        mock_report.accuracy_rate = 0.9

        assert analyzer.validate_detection_accuracy(mock_report, required_accuracy=0.9) is True
