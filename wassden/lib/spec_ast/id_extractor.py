"""ID extraction utilities for spec documents.

This module provides functions to extract and parse various types of IDs
from specification documents (requirements, tasks, design components, etc.).
"""

import re


class IDExtractor:
    """Extractor for various ID types in spec documents."""

    # ID patterns (using existing patterns from validation_common.py)
    REQ_ID_PATTERN = r"\bREQ-\d{2}\b"
    NFR_ID_PATTERN = r"\bNFR-\d{2}\b"
    KPI_ID_PATTERN = r"\bKPI-\d{2}\b"
    TR_ID_PATTERN = r"\bTR-\d{2}\b"
    TASK_ID_PATTERN = r"\bTASK-\d{2}(?:-\d{2}){0,2}\b"
    DC_PATTERN = r"\bDC-\d{2}\b"

    # Prefixed patterns for list items (e.g., "REQ-01: requirement text")
    PREFIXED_REQ_PATTERN = r"^(REQ-\d+|NFR-\d+|KPI-\d+|TR-\d+):\s*(.+)$"
    PREFIXED_TASK_PATTERN = r"^(TASK-\d+(?:-\d+){0,2}):\s*(.+)$"

    # Loose patterns for malformed IDs
    LOOSE_REQ_PATTERN = r"^(REQ[-A-Za-z0-9]*|TR[-A-Za-z0-9]*|NFR[-A-Za-z0-9]*|KPI[-A-Za-z0-9]*):\s*(.+)$"
    LOOSE_TASK_PATTERN = r"^(TASK[-A-Za-z0-9]*):\s*(.+)$"

    @staticmethod
    def extract_req_id_from_text(text: str) -> tuple[str | None, str, str]:
        """Extract requirement ID from text.

        Args:
            text: Text that may contain a requirement ID prefix (e.g., "REQ-01: description")

        Returns:
            Tuple of (req_id, req_text_without_id, req_type)
            - req_id: Extracted ID (e.g., "REQ-01") or None
            - req_text_without_id: Text with ID prefix stripped
            - req_type: Requirement type ("REQ", "NFR", "KPI", "TR")
        """
        text = text.strip()

        # Try strict pattern first
        match = re.match(IDExtractor.PREFIXED_REQ_PATTERN, text)
        if match:
            req_id = match.group(1)
            req_text = match.group(2).strip()
            req_type = req_id.split("-")[0]
            return req_id, req_text, req_type

        # Try loose pattern for malformed IDs
        match = re.match(IDExtractor.LOOSE_REQ_PATTERN, text)
        if match:
            req_id = match.group(1)
            req_text = match.group(2).strip()
            req_type = req_id.split("-")[0] if "-" in req_id else "REQ"
            return req_id, req_text, req_type

        # No ID found
        return None, text, "REQ"

    @staticmethod
    def extract_task_id_from_text(text: str) -> tuple[str | None, str]:
        """Extract task ID from text.

        Args:
            text: Text that may contain a task ID prefix (e.g., "TASK-01-01: description")

        Returns:
            Tuple of (task_id, task_text_without_id)
            - task_id: Extracted ID (e.g., "TASK-01-01") or None
            - task_text_without_id: Text with ID prefix stripped
        """
        text = text.strip()

        # Try strict pattern first
        match = re.match(IDExtractor.PREFIXED_TASK_PATTERN, text)
        if match:
            task_id = match.group(1)
            task_text = match.group(2).strip()
            return task_id, task_text

        # Try loose pattern for malformed IDs
        match = re.match(IDExtractor.LOOSE_TASK_PATTERN, text)
        if match:
            task_id = match.group(1)
            task_text = match.group(2).strip()
            return task_id, task_text

        # No ID found
        return None, text

    @staticmethod
    def extract_all_req_ids(text: str) -> set[str]:
        """Extract all requirement IDs from text.

        Args:
            text: Text to search

        Returns:
            Set of requirement IDs found
        """
        ids: set[str] = set()
        ids.update(re.findall(IDExtractor.REQ_ID_PATTERN, text))
        ids.update(re.findall(IDExtractor.NFR_ID_PATTERN, text))
        ids.update(re.findall(IDExtractor.KPI_ID_PATTERN, text))
        ids.update(re.findall(IDExtractor.TR_ID_PATTERN, text))
        return ids

    @staticmethod
    def extract_all_task_ids(text: str) -> set[str]:
        """Extract all task IDs from text.

        Args:
            text: Text to search

        Returns:
            Set of task IDs found
        """
        return set(re.findall(IDExtractor.TASK_ID_PATTERN, text))

    @staticmethod
    def extract_all_dc_refs(text: str) -> set[str]:
        """Extract all design component references from text.

        Args:
            text: Text to search

        Returns:
            Set of DC references found (e.g., {"DC-01", "DC-03"})
        """
        return set(re.findall(IDExtractor.DC_PATTERN, text))

    @staticmethod
    def extract_task_dependencies(text: str) -> list[str]:
        """Extract task dependencies from task text.

        Looks for patterns like "depends on TASK-01-01" or "requires TASK-02-03".

        Args:
            text: Task description text

        Returns:
            List of task IDs this task depends on
        """
        dependencies: list[str] = []

        # Pattern: "depends on TASK-XX-XX" or "requires TASK-XX-XX"
        dependency_patterns = [
            r"depends on (TASK-\d{2}(?:-\d{2}){0,2})",
            r"requires (TASK-\d{2}(?:-\d{2}){0,2})",
            r"after (TASK-\d{2}(?:-\d{2}){0,2})",
            r"依存:\s*(TASK-\d{2}(?:-\d{2}){0,2})",  # Japanese
        ]

        for pattern in dependency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dependencies.extend(matches)

        return dependencies

    @staticmethod
    def is_acceptance_criteria(text: str) -> bool:
        """Check if text appears to be acceptance criteria rather than a requirement.

        Args:
            text: Text to check

        Returns:
            True if text looks like acceptance criteria
        """
        skip_patterns = [
            r"受け入れ観点",
            r"受入観点",
            r"Acceptance criteria",
            r"テスト観点",
            r"Test criteria",
        ]

        return any(re.search(pattern, text, re.IGNORECASE) for pattern in skip_patterns)
