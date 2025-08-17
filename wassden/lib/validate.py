"""Validation utilities for spec documents."""

import re
from typing import Any

from .validation_common import (
    check_circular_dependencies,
    check_design_coverage_with_threshold,
    check_requirement_coverage,
    check_requirement_coverage_with_threshold,
    extract_design_components,
    extract_req_ids,
    extract_task_dependencies,
    extract_task_ids,
    find_component_references,
)

# Constants
DEPENDENCY_SPLIT_PARTS = 2


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


def validate_requirements_structure(req_content: str) -> list[str]:
    """Validate requirements document structure."""
    errors: list[str] = []

    _check_required_sections(req_content, errors)
    _validate_requirement_ids(req_content, errors)

    return errors


def _check_required_sections(req_content: str, errors: list[str]) -> None:
    """Check for required sections in requirements document."""
    required_sections = [
        "サマリー",
        "用語集",
        "スコープ",
        "制約",
        "非機能要件",
        "KPI",
        "機能要件",
    ]

    for section in required_sections:
        pattern = rf"## \d*\.?\s*{re.escape(section)}"
        if not re.search(pattern, req_content) and f"## {section}" not in req_content:
            errors.append(f"Missing required section: {section}")


def _validate_requirement_ids(req_content: str, errors: list[str]) -> None:
    """Validate requirement IDs in the functional requirements section."""
    functional_req_match = re.search(r"## \d*\.?\s*機能要件.*?(?=## |$)", req_content, re.DOTALL)
    functional_req_section = functional_req_match.group(0) if functional_req_match else ""

    req_lines = [line for line in functional_req_section.split("\n") if line.strip().startswith("-")]

    all_req_ids, all_candidate_ids = _extract_ids_from_lines(req_lines)

    _check_duplicate_req_ids(all_req_ids, errors)
    _validate_id_formats(all_candidate_ids, errors)


def _extract_ids_from_lines(req_lines: list[str]) -> tuple[list[str], list[str]]:
    """Extract all IDs from requirement lines."""
    all_req_ids: list[str] = []
    all_candidate_ids: list[str] = []

    for line in req_lines:
        id_matches = re.findall(r"\b[A-Za-z]+-\d+[A-Za-z]*", line)
        req_punct_matches = re.findall(r"\b[Rr][Ee][Qq]-[^\s:]*", line)

        cleaned_req_ids = []
        for req_id in req_punct_matches:
            match = re.match(r"^([Rr][Ee][Qq]-\d+[A-Za-z]*)", req_id)
            if match:
                cleaned_req_ids.append(match.group(1))
            else:
                cleaned_req_ids.append(req_id)

        line_ids = list(set(id_matches + cleaned_req_ids))
        all_candidate_ids.extend(line_ids)

        line_req_ids = [req_id for req_id in line_ids if req_id.upper().startswith("REQ-")]
        all_req_ids.extend(line_req_ids)

    return all_req_ids, all_candidate_ids


def _check_duplicate_req_ids(all_req_ids: list[str], errors: list[str]) -> None:
    """Check for duplicate REQ-IDs."""
    unique_req_ids = set(all_req_ids)
    if len(all_req_ids) != len(unique_req_ids):
        seen = set()
        duplicates = set()
        for req_id in all_req_ids:
            if req_id in seen:
                duplicates.add(req_id)
            seen.add(req_id)
        duplicate_list = sorted(duplicates)
        errors.append(f"Duplicate REQ-IDs found: {', '.join(duplicate_list)}")


def _validate_id_formats(all_candidate_ids: list[str], errors: list[str]) -> None:
    """Validate format of all candidate IDs."""
    unique_candidate_ids = list(set(all_candidate_ids))
    invalid_ids = [candidate_id for candidate_id in unique_candidate_ids if not validate_req_id(candidate_id)]
    errors.extend(f"Invalid REQ-ID format: {candidate_id}" for candidate_id in invalid_ids)


def validate_design_structure(design_content: str) -> list[str]:
    """Validate design document structure."""
    errors: list[str] = []

    required_sections = [
        "アーキテクチャ",
        "コンポーネント設計",
        "データ",
        "API",
        "非機能",
        "テスト",
    ]

    for section in required_sections:
        pattern = rf"## \d*\.?\s*{re.escape(section)}"
        if not re.search(pattern, design_content) and f"## {section}" not in design_content:
            errors.append(f"Missing required section: {section}")

    # Check for REQ-ID references
    if not re.search(r"\bREQ-\d{2}\b", design_content):
        errors.append("No REQ-ID references found in design document")

    return errors


def validate_tasks_structure(tasks_content: str) -> list[str]:
    """Validate tasks document structure."""
    errors: list[str] = []

    required_sections = [
        "概要",
        "タスク一覧",
        "依存関係",
        "マイルストーン",
    ]

    for section in required_sections:
        pattern = rf"## \d*\.?\s*{re.escape(section)}"
        if not re.search(pattern, tasks_content) and f"## {section}" not in tasks_content:
            errors.append(f"Missing required section: {section}")

    # Extract and validate task IDs - only unique IDs in task definitions
    # Look for task definitions (with **TASK pattern)
    task_definitions = re.findall(r"\*\*TASK-\d{2}(?:-\d{2}){0,2}\*\*", tasks_content)
    task_ids_in_defs = [t.strip("*") for t in task_definitions]

    # Check for duplicates only in definitions
    if len(task_ids_in_defs) != len(set(task_ids_in_defs)):
        # Find specific duplicates
        seen = set()
        duplicates = set()
        for task_id in task_ids_in_defs:
            if task_id in seen:
                duplicates.add(task_id)
            seen.add(task_id)
        duplicate_list = sorted(duplicates)
        errors.append(f"Duplicate TASK-IDs found: {', '.join(duplicate_list)}")

    # Extract all task IDs for format validation (including invalid ones)
    # First get the main patterns
    all_task_ids = re.findall(r"\bTASK-\d{1,3}(?:-\d{1,3}){0,2}\b", tasks_content)
    # Also look for case-insensitive and slightly malformed ones
    additional_patterns = re.findall(r"\b[Tt][Aa][Ss][Kk]-\d+(?:-\d+)*(?:-\d+)*\b", tasks_content)
    all_task_ids.extend(additional_patterns)
    # Look for other patterns that could be intended as task IDs (wrong prefix, format issues)
    malformed_patterns = re.findall(
        r"\b(?:[A-Z]+[A-Z]*|[Tt][Aa][Ss][Kk]|INVALID|TSK)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\b", tasks_content
    )
    for task_id in malformed_patterns:
        # Only include patterns that look like they were intended to be task IDs
        # Exclude common things like REQ-XX, NFR-XX, etc.
        if (
            task_id not in all_task_ids
            and not task_id.startswith(("REQ-", "NFR-", "KPI-"))
            and not re.match(r"^[a-z]+-[a-z]+$", task_id)
        ):  # Exclude things like "input-handler"
            all_task_ids.append(task_id)

    # Validate format
    invalid_task_ids = [task_id for task_id in set(all_task_ids) if not validate_task_id(task_id)]
    errors.extend(f"Invalid TASK-ID format: {task_id}" for task_id in invalid_task_ids)

    return errors


def validate_spec_structure(spec_type: str, content: str) -> dict[str, Any]:
    """Validate spec document structure based on type."""
    if spec_type == "requirements":
        errors = validate_requirements_structure(content)
    elif spec_type == "design":
        errors = validate_design_structure(content)
    elif spec_type == "tasks":
        errors = validate_tasks_structure(content)
    else:
        errors = [f"Unknown spec type: {spec_type}"]

    return {"isValid": len(errors) == 0, "errors": errors}


def validate_requirements(content: str) -> dict[str, Any]:
    """Validate requirements document."""
    errors = validate_requirements_structure(content)

    # Count stats
    req_ids = re.findall(r"\bREQ-\d{2}\b", content)
    nfr_ids = re.findall(r"\bNFR-\d{2}\b", content)
    kpi_ids = re.findall(r"\bKPI-\d{2}\b", content)

    # Find sections
    found_sections = []
    for section in ["サマリー", "用語集", "スコープ", "制約", "非機能要件", "KPI", "機能要件"]:
        pattern = rf"## \d*\.?\s*{re.escape(section)}"
        if re.search(pattern, content) or f"## {section}" in content:
            found_sections.append(section)

    return {
        "isValid": len(errors) == 0,
        "issues": errors,
        "stats": {
            "totalRequirements": len(set(req_ids)),
            "totalNFRs": len(set(nfr_ids)),
            "totalKPIs": len(set(kpi_ids)),
        },
        "foundSections": found_sections,
    }


def validate_design(content: str, requirements_content: str | None = None) -> dict[str, Any]:
    """Validate design document."""
    errors = validate_design_structure(content)

    # Extract referenced REQ-IDs using common logic
    referenced_reqs = extract_req_ids(content)

    # If requirements content provided, check traceability
    missing_refs = []
    if requirements_content:
        # Extract all requirements using common logic
        all_reqs = extract_req_ids(requirements_content)
        coverage_errors = check_requirement_coverage(all_reqs, referenced_reqs)
        errors.extend(coverage_errors)
        missing_refs = list(all_reqs - referenced_reqs)

    return {
        "isValid": len(errors) == 0,
        "issues": errors,
        "stats": {
            "referencedRequirements": len(referenced_reqs),
            "missingReferences": missing_refs,
        },
    }


def validate_tasks(
    content: str, requirements_content: str | None = None, design_content: str | None = None
) -> dict[str, Any]:
    """Validate tasks document."""
    errors = validate_tasks_structure(content)

    # Extract task IDs using common logic
    task_ids = extract_task_ids(content)

    # Extract and check task dependencies using common logic
    dependencies = extract_task_dependencies(content)
    circular_errors = check_circular_dependencies(dependencies)
    errors.extend(circular_errors)

    # Check traceability using common logic
    missing_req_refs: list[str] = []
    missing_design_refs: list[str] = []

    # Check requirement traceability
    if requirements_content:
        all_reqs = extract_req_ids(requirements_content)
        tasks_referencing_reqs = extract_req_ids(content)

        coverage_errors, missing_req_refs = check_requirement_coverage_with_threshold(
            all_reqs, tasks_referencing_reqs, context="tasks"
        )
        errors.extend(coverage_errors)

    # Check design component traceability
    if design_content:
        design_components = extract_design_components(design_content)
        tasks_referencing_design = find_component_references(design_components, content)

        coverage_errors, missing_design_refs = check_design_coverage_with_threshold(
            design_components, tasks_referencing_design, context="tasks"
        )
        errors.extend(coverage_errors)

    return {
        "isValid": len(errors) == 0,
        "issues": errors,
        "stats": {
            "totalTasks": len(task_ids),
            "dependencies": len(dependencies),
            "missingRequirementReferences": missing_req_refs,
            "missingDesignReferences": missing_design_refs,
        },
    }
