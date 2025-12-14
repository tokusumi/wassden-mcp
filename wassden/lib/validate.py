"""Validation utilities for spec documents."""

import re
from typing import Any

from wassden.language_types import Language

from .spec_ast.validation_compat import (
    validate_design_ast,
    validate_requirements_ast,
    validate_tasks_ast,
)


def validate_req_id(req_id: str) -> bool:
    """Validate requirement ID format (REQ-XX where XX is 01-99)."""
    if not re.match(r"^REQ-\d{2}$", req_id):
        return False
    # Extract the number part and check it's not 00
    num_part = req_id.split("-")[1]
    return num_part != "00"


def validate_task_id(task_id: str) -> bool:
    """Validate task ID format (TASK-XX-XX or TASK-XX-XX-XX where XX is 01-99)."""
    if not re.match(r"^TASK-\d{2}(-\d{2}){1,2}$", task_id):
        return False
    # Extract all number parts and check none are 00
    parts = task_id.split("-")[1:]  # Remove "TASK" part
    return all(part != "00" for part in parts)


def validate_requirements(content: str, language: Language = Language.JAPANESE) -> dict[str, Any]:
    """Validate requirements document using AST validation."""
    return validate_requirements_ast(content, language)


def validate_design(content: str, requirements_content: str | None = None) -> dict[str, Any]:
    """Validate design document using AST validation."""
    return validate_design_ast(content, requirements_content)


def validate_tasks(
    content: str, requirements_content: str | None = None, design_content: str | None = None
) -> dict[str, Any]:
    """Validate tasks document using AST validation."""
    return validate_tasks_ast(content, requirements_content, design_content)
