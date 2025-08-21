"""EARS (Easy Approach to Requirements Syntax) validation module.

This module validates requirements against EARS patterns.
Initial version supports only Ubiquitous pattern.
"""

import re
from typing import Any

import markdown
from pydantic import BaseModel, Field

from wassden.i18n.core import get_i18n
from wassden.types import Language


class EARSViolation(BaseModel):
    """Represents an EARS pattern violation."""

    line: int = Field(description="Line number where violation occurred")
    text: str = Field(description="Original requirement text")
    reason: str = Field(description="Reason for violation")


class EARSValidationResult(BaseModel):
    """Result of EARS validation."""

    pattern: str = Field(description="EARS pattern validated against")
    total: int = Field(description="Total number of requirements")
    matched: int = Field(description="Number of matched requirements")
    rate: float = Field(description="Match rate (0.0 - 1.0)")
    violations: list[EARSViolation] = Field(default_factory=list, description="List of violations found")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format for compatibility."""
        return {
            "ears": {
                "pattern": self.pattern,
                "total": self.total,
                "matched": self.matched,
                "rate": self.rate,
                "violations": [{"line": v.line, "reason": v.reason, "text": v.text} for v in self.violations],
            }
        }


class EARSValidator:
    """Validates requirements against EARS patterns."""

    def __init__(self, language: Language = Language.JAPANESE) -> None:
        """Initialize validator with language support.

        Args:
            language: Language for validation and error messages
        """
        self.language = language.value
        self.i18n = get_i18n(language)

        # Ubiquitous pattern regex
        self.ubiquitous_patterns = {
            "ja": re.compile(r"^(システムは|本システムは).+([あ-ん]ること|すること|する)[。]?$"),
            "en": re.compile(r"^The system shall .+\.$", re.IGNORECASE),
        }

    def validate_ubiquitous(self, requirements: list[str]) -> EARSValidationResult:
        """Validate requirements against Ubiquitous pattern.

        Args:
            requirements: List of requirement texts

        Returns:
            Validation result with violations
        """
        pattern_regex = self.ubiquitous_patterns.get(self.language, self.ubiquitous_patterns["en"])
        violations = []
        matched_count = 0

        for i, req_text in enumerate(requirements, 1):
            req = req_text.strip()
            if not req:  # Skip empty lines
                continue

            if pattern_regex.match(req):
                matched_count += 1
            else:
                reason = self._get_violation_reason(req)
                violations.append(EARSViolation(line=i, text=req, reason=reason))

        total = len([r for r in requirements if r.strip()])
        rate = matched_count / total if total > 0 else 0.0

        return EARSValidationResult(
            pattern="ubiquitous", total=total, matched=matched_count, rate=rate, violations=violations
        )

    def _get_violation_reason(self, req: str) -> str:
        """Get localized violation reason for requirement.

        Args:
            req: Requirement text

        Returns:
            Localized violation reason
        """
        if self.language == "ja":
            return self._get_japanese_violation_reason(req)
        return self._get_english_violation_reason(req)

    def _get_japanese_violation_reason(self, req: str) -> str:
        """Get Japanese violation reason."""
        if not req.startswith(("システムは", "本システムは")):
            return str(self.i18n.t("validation_errors.ears.missing_system_prefix_ja"))
        if not (req.endswith(("すること。", "する。", "すること", "する")) or re.search(r"[あ-ん]ること[。]?$", req)):
            return str(self.i18n.t("validation_errors.ears.missing_action_suffix_ja"))
        return str(self.i18n.t("validation_errors.ears.pattern_mismatch_ja"))

    def _get_english_violation_reason(self, req: str) -> str:
        """Get English violation reason."""
        req_lower = req.lower()
        if not req_lower.startswith("the system "):
            return str(self.i18n.t("validation_errors.ears.missing_system_prefix_en"))
        if not req_lower.startswith("the system shall"):
            return str(self.i18n.t("validation_errors.ears.missing_shall_en"))
        if not req.endswith("."):
            return str(self.i18n.t("validation_errors.ears.missing_period_en"))
        return str(self.i18n.t("validation_errors.ears.pattern_mismatch_en"))

    def extract_requirements_from_markdown(self, markdown_text: str) -> list[str]:
        """Extract functional requirements from markdown text using markdown parser.

        Args:
            markdown_text: Markdown content

        Returns:
            List of requirement texts
        """
        # Use markdown parser to convert to HTML and parse it properly
        md = markdown.Markdown(extensions=["toc"])
        html_content = md.convert(markdown_text)

        functional_headers = [
            "機能要件（EARS）",
            ". 機能要件",
            "## 6. Functional Requirements",
            "機能要件",
            "Functional Requirements",
        ]

        # Try HTML-based extraction first
        requirements = self._extract_from_html(html_content, functional_headers)

        # Fallback to line-by-line if HTML parsing didn't work
        if not requirements:
            requirements = self._extract_from_text(markdown_text, functional_headers)

        return requirements

    def _extract_from_html(self, html_content: str, functional_headers: list[str]) -> list[str]:
        """Extract requirements from HTML content."""
        requirements = []

        for header in functional_headers:
            # Look for the header in HTML - be more specific to avoid substring matches
            if header == "Functional Requirements":
                # For this header, ensure it's not part of "Non-Functional Requirements"
                header_pattern = r"<h[1-6][^>]*>.*?(?<!Non-)Functional Requirements.*?</h[1-6]>"
            else:
                header_pattern = rf"<h[1-6][^>]*>.*?{re.escape(header)}.*?</h[1-6]>"
            header_match = re.search(header_pattern, html_content, re.IGNORECASE | re.DOTALL)

            if header_match:
                # Find content after this header until next header
                start_pos = header_match.end()
                next_header_pattern = r"<h[1-6][^>]*>.*?</h[1-6]>"
                remaining_content = html_content[start_pos:]
                next_header_match = re.search(next_header_pattern, remaining_content)

                section_content = (
                    remaining_content[: next_header_match.start()] if next_header_match else remaining_content
                )

                # Extract list items from this section using HTML
                list_item_matches = re.findall(r"<li[^>]*>(.*?)</li>", section_content, re.DOTALL)

                for item_html in list_item_matches:
                    req_text = self._clean_html_text(item_html)
                    if req_text and self._is_requirement_item(req_text):
                        requirements.append(req_text)
                break

        return requirements

    def _clean_html_text(self, html_text: str) -> str:
        """Clean HTML text and entities."""
        # Remove HTML tags and clean up the text
        text = re.sub(r"<[^>]+>", "", html_text)
        text = re.sub(r"\s+", " ", text.strip())

        # Use markdown parsing knowledge to clean up entities
        text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

        # Strip REQ-ID prefixes for EARS validation
        req_id_pattern = r"^(REQ-\d+|TR-\d+|NFR-\d+|KPI-\d+):\s*(.+)$"
        req_id_match = re.match(req_id_pattern, text)
        if req_id_match:
            text = req_id_match.group(2).strip()

        return text

    def _extract_from_text(self, markdown_text: str, functional_headers: list[str]) -> list[str]:
        """Fallback extraction using line-by-line parsing."""
        requirements = []
        lines = markdown_text.split("\n")
        in_functional_section = False
        current_header_level = 0

        for line in lines:
            stripped_line = line.strip()

            # Check for headers
            if stripped_line.startswith("#"):
                header_level = len(stripped_line) - len(stripped_line.lstrip("#"))
                header_text = stripped_line.lstrip("# ").strip()

                # Check if we're entering functional requirements section
                if header_text in functional_headers:
                    in_functional_section = True
                    current_header_level = header_level
                    continue

                # Check if we're leaving the section
                if in_functional_section and header_level <= current_header_level:
                    in_functional_section = False

            # Extract list items in functional requirements section only
            if in_functional_section:
                req_text = self._extract_list_item(stripped_line)
                if req_text and self._is_requirement_item(req_text):
                    requirements.append(req_text)

        return requirements

    def _extract_list_item(self, line: str) -> str:
        """Extract requirement text from a markdown list item."""
        # Handle various markdown list formats
        list_patterns = [
            r"^[-*+]\s+(.+)$",  # Standard markdown lists
            r"^\d+\.\s+(.+)$",  # Numbered lists
            r"^•\s+(.+)$",  # Bullet points
            r"^\s*[-*+]\s+(.+)$",  # Indented lists
            r"^\s*\d+\.\s+(.+)$",  # Indented numbered lists
        ]

        for pattern in list_patterns:
            match = re.match(pattern, line)
            if match:
                req_text = match.group(1).strip()
                # Clean up markdown syntax using markdown knowledge
                req_text = re.sub(r"\*\*(.+?)\*\*", r"\1", req_text)  # Bold
                req_text = re.sub(r"\*(.+?)\*", r"\1", req_text)  # Italic
                req_text = re.sub(r"`(.+?)`", r"\1", req_text)  # Code
                req_text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", req_text)  # Links

                # Strip REQ-ID prefixes for EARS validation
                req_id_pattern = r"^(REQ-\d+|TR-\d+|NFR-\d+|KPI-\d+):\s*(.+)$"
                req_id_match = re.match(req_id_pattern, req_text)
                if req_id_match:
                    req_text = req_id_match.group(2).strip()

                return req_text

        return ""

    def _is_requirement_item(self, text: str) -> bool:
        """Check if the text is a functional requirement (not acceptance criteria or other content)."""
        # Skip acceptance criteria and other non-requirement items
        skip_patterns = [
            r"受け入れ観点",  # Acceptance criteria
            r"受入観点",  # Acceptance criteria (alternative)
            r"Acceptance criteria",
            r"テスト観点",  # Test criteria
            r"Test criteria",
            r"注意事項",  # Notes
            r"Note:",
            r"備考",  # Remarks
            r"Remark:",
        ]

        return all(not re.search(pattern, text, re.IGNORECASE) for pattern in skip_patterns)


def validate_ears_in_content(content: str, language: Language = Language.JAPANESE) -> EARSValidationResult:
    """Validate EARS patterns in markdown content.

    This is the main integration point with existing validation system.

    Args:
        content: Markdown content to validate
        language: Language for validation

    Returns:
        EARS validation result
    """
    validator = EARSValidator(language)
    requirements = validator.extract_requirements_from_markdown(content)
    return validator.validate_ubiquitous(requirements)
