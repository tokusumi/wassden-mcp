"""Unit tests for EARS validation module."""

from wassden.lib.validate_ears import EARSValidator
from wassden.types import Language


class TestEARSValidator:
    """Test EARS validator functionality."""

    def setup_method(self) -> None:
        """Setup test fixtures."""
        self.validator = EARSValidator(Language.JAPANESE)

    def test_validate_ubiquitous_japanese_valid(self) -> None:
        """Test valid Japanese Ubiquitous patterns."""
        requirements = [
            "システムはユーザー情報を保存すること。",
            "システムはログインを検証する。",
            "本システムはデータを暗号化すること。",
        ]
        result = self.validator.validate_ubiquitous(requirements)

        assert result.pattern == "ubiquitous"
        assert result.total == 3
        assert result.matched == 3
        assert result.rate == 1.0
        assert len(result.violations) == 0

    def test_validate_ubiquitous_japanese_invalid(self) -> None:
        """Test invalid Japanese Ubiquitous patterns."""
        requirements = [
            "ユーザーはログインできる。",  # Not starting with システムは
            "システムは処理を実行します。",  # Not ending with すること/する
            "システムがデータを保存する。",  # Using が instead of は
        ]
        result = self.validator.validate_ubiquitous(requirements)

        assert result.total == 3
        assert result.matched == 0
        assert result.rate == 0.0
        assert len(result.violations) == 3
        assert "「システムは」または「本システムは」で始まっていません" in result.violations[0].reason

    def test_validate_ubiquitous_english_valid(self) -> None:
        """Test valid English Ubiquitous patterns."""
        # Create validator with English language
        validator = EARSValidator(Language.ENGLISH)
        requirements = [
            "The system shall save user information.",
            "The system shall validate login credentials.",
            "The system shall encrypt all data.",
        ]
        result = validator.validate_ubiquitous(requirements)

        assert result.pattern == "ubiquitous"
        assert result.total == 3
        assert result.matched == 3
        assert result.rate == 1.0
        assert len(result.violations) == 0

    def test_validate_ubiquitous_english_invalid(self) -> None:
        """Test invalid English Ubiquitous patterns."""
        # Create validator with English language
        validator = EARSValidator(Language.ENGLISH)
        requirements = [
            "Users can login to the system",  # Not starting with The system
            "The system should save data.",  # Using should instead of shall
            "The system shall process requests",  # Missing period
        ]
        result = validator.validate_ubiquitous(requirements)

        assert result.total == 3
        assert result.matched == 0
        assert result.rate == 0.0
        assert len(result.violations) == 3
        assert "Not starting with 'The system'" in result.violations[0].reason
        assert "Missing 'shall'" in result.violations[1].reason
        assert "Not ending with period" in result.violations[2].reason

    def test_validate_ubiquitous_empty_list(self) -> None:
        """Test validation with empty requirements list."""
        result = self.validator.validate_ubiquitous([])

        assert result.total == 0
        assert result.matched == 0
        assert result.rate == 0.0
        assert len(result.violations) == 0

    def test_validate_ubiquitous_skip_empty_lines(self) -> None:
        """Test that empty lines are skipped."""
        requirements = [
            "システムはデータを保存すること。",
            "",
            "  ",
            "システムはログを記録する。",
        ]
        result = self.validator.validate_ubiquitous(requirements)

        assert result.total == 2  # Only non-empty lines
        assert result.matched == 2
        assert result.rate == 1.0

    def test_extract_requirements_from_markdown_japanese(self) -> None:
        """Test extracting requirements from Japanese markdown."""
        markdown = """# 要件定義書

## 概要
システムの概要です。

## 機能要件
- システムはユーザー認証を行うこと。
- システムはデータを暗号化する。
- システムはログを記録すること。

## 非機能要件
- レスポンスは3秒以内
"""
        requirements = self.validator.extract_requirements_from_markdown(markdown)

        assert len(requirements) == 3
        assert requirements[0] == "システムはユーザー認証を行うこと。"
        assert requirements[1] == "システムはデータを暗号化する。"
        assert requirements[2] == "システムはログを記録すること。"

    def test_extract_requirements_from_markdown_english(self) -> None:
        """Test extracting requirements from English markdown."""
        markdown = """# Requirements Document

## Overview
System overview.

## Functional Requirements
- The system shall authenticate users.
- The system shall encrypt data.
- The system shall log activities.

## Non-Functional Requirements
- Response time under 3 seconds
"""
        # Create validator with English language
        validator = EARSValidator(Language.ENGLISH)
        requirements = validator.extract_requirements_from_markdown(markdown)

        assert len(requirements) == 3
        assert requirements[0] == "The system shall authenticate users."
        assert requirements[1] == "The system shall encrypt data."
        assert requirements[2] == "The system shall log activities."

    def test_result_to_dict(self) -> None:
        """Test converting result to dictionary format."""
        requirements = ["Invalid requirement"]
        result = self.validator.validate_ubiquitous(requirements)
        result_dict = result.to_dict()

        assert "ears" in result_dict
        assert result_dict["ears"]["pattern"] == "ubiquitous"
        assert result_dict["ears"]["total"] == 1
        assert result_dict["ears"]["matched"] == 0
        assert result_dict["ears"]["rate"] == 0.0
        assert len(result_dict["ears"]["violations"]) == 1
        assert "line" in result_dict["ears"]["violations"][0]
        assert "reason" in result_dict["ears"]["violations"][0]
        assert "text" in result_dict["ears"]["violations"][0]
