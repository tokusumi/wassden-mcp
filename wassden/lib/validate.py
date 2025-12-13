"""Validation utilities for spec documents."""

import os
import re
from typing import Any

from wassden.language_types import Language

from .validate_ears import validate_ears_in_content
from .validation_common import (
    check_circular_dependencies,
    check_design_coverage_with_threshold,
    check_requirement_coverage,
    check_requirement_coverage_with_threshold,
    check_tr_coverage,
    extract_design_components,
    extract_req_ids,
    extract_task_dependencies,
    extract_task_ids,
    extract_test_scenarios,
    extract_tr_ids,
    find_component_references,
)

# Feature flag: Use AST-based validation when enabled
USE_AST_VALIDATION = os.environ.get("USE_AST_VALIDATION", "0") == "1"

# Import AST validation functions only when feature flag is enabled
if USE_AST_VALIDATION:
    from .spec_ast.validation_compat import (
        validate_design_ast,
        validate_requirements_ast,
        validate_tasks_ast,
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
    # Define section pairs (Japanese, English)
    required_section_pairs = [
        ("サマリー", "Summary"),
        ("用語集", "Glossary"),
        ("スコープ", "Scope"),
        ("制約", "Constraints"),
        ("非機能要件", "Non-Functional Requirements"),
        ("KPI", "KPI"),
        ("機能要件", "Functional Requirements"),
        ("テスト要件", "Testing Requirements"),
    ]

    for ja_section, en_section in required_section_pairs:
        # Check if either Japanese or English version exists
        ja_pattern = rf"## \d*\.?\s*{re.escape(ja_section)}"
        en_pattern = rf"## \d*\.?\s*{re.escape(en_section)}"

        ja_found = re.search(ja_pattern, req_content) or f"## {ja_section}" in req_content
        en_found = re.search(en_pattern, req_content) or f"## {en_section}" in req_content

        if not ja_found and not en_found:
            errors.append(f"Missing required section: {ja_section} or {en_section}")


def _validate_requirement_ids(req_content: str, errors: list[str]) -> None:
    """Validate requirement IDs in the functional requirements section."""
    # Search for both Japanese and English functional requirements sections
    functional_req_match_ja = re.search(r"## \d*\.?\s*機能要件.*?(?=## |$)", req_content, re.DOTALL)
    functional_req_match_en = re.search(r"## \d*\.?\s*Functional Requirements.*?(?=## |$)", req_content, re.DOTALL)

    # Use whichever section is found
    functional_req_section = ""
    if functional_req_match_ja:
        functional_req_section = functional_req_match_ja.group(0)
    elif functional_req_match_en:
        functional_req_section = functional_req_match_en.group(0)

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

    # Define section pairs (Japanese, English)
    required_section_pairs = [
        ("アーキテクチャ", "Architecture"),
        ("コンポーネント設計", "Component Design"),
        ("データ", "Data"),
        ("API", "API"),
        ("非機能", "Non-functional"),
        ("テスト", "Test"),
    ]

    for ja_section, en_section in required_section_pairs:
        # Check if either Japanese or English version exists
        ja_pattern = rf"## \d*\.?\s*{re.escape(ja_section)}"
        en_pattern = rf"## \d*\.?\s*{re.escape(en_section)}"

        ja_found = re.search(ja_pattern, design_content) or f"## {ja_section}" in design_content
        en_found = re.search(en_pattern, design_content) or f"## {en_section}" in design_content

        if not ja_found and not en_found:
            errors.append(f"Missing required section: {ja_section} or {en_section}")

    # Check for REQ-ID references
    if not re.search(r"\bREQ-\d{2}\b", design_content):
        errors.append("No REQ-ID references found in design document")

    return errors


def _find_duplicate_task_ids(task_ids: list[str]) -> set[str]:
    """Find duplicate task IDs in a list."""
    seen = set()
    duplicates = set()
    for task_id in task_ids:
        if task_id in seen:
            duplicates.add(task_id)
        seen.add(task_id)
    return duplicates


def _extract_all_task_patterns(tasks_content: str) -> list[str]:
    """Extract all TASK patterns for validation - includes valid and invalid patterns.

    Only extracts patterns from the Task List section (タスク一覧 or Task List),
    not from other sections like dependencies or milestones.
    """
    all_task_ids = []

    # Find the task list section (support both Japanese and English)
    task_list_match_ja = re.search(r"## \d*\.?\s*タスク一覧.*?(?=## |$)", tasks_content, re.DOTALL)
    task_list_match_en = re.search(r"## \d*\.?\s*Task List.*?(?=## |$)", tasks_content, re.DOTALL)

    task_list_section = ""
    if task_list_match_ja:
        task_list_section = task_list_match_ja.group(0)
    elif task_list_match_en:
        task_list_section = task_list_match_en.group(0)
    else:
        # If no task list section found, return empty list
        return []

    # Extract task definitions (patterns surrounded by **) from task list section only
    # Case-insensitive to catch both TASK and task patterns
    task_def_patterns = re.findall(r"\*\*([Tt][Aa][Ss][Kk]-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)\*\*", task_list_section)
    all_task_ids.extend(task_def_patterns)

    # Also check for malformed patterns with wrong prefixes that should be TASK
    wrong_prefix_patterns = re.findall(r"\*\*(?:TSK|INVALID)-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\*\*", task_list_section)
    all_task_ids.extend(p.strip("*") for p in wrong_prefix_patterns)

    # Remove duplicates while preserving order for error reporting
    seen = set()
    unique_task_ids = []
    for task_id in all_task_ids:
        if task_id not in seen:
            seen.add(task_id)
            unique_task_ids.append(task_id)

    return unique_task_ids


def _find_invalid_task_ids(all_task_ids: list[str]) -> list[str]:
    """Find invalid task IDs from extracted patterns."""
    invalid_task_ids = []
    for task_id in set(all_task_ids):
        # Skip patterns that are clearly not intended as TASK-IDs
        if task_id.startswith(("REQ-", "NFR-", "KPI-", "TR-")):
            continue
        if not validate_task_id(task_id):
            invalid_task_ids.append(task_id)
    return invalid_task_ids


def validate_tasks_structure(tasks_content: str) -> list[str]:
    """Validate tasks document structure."""
    errors: list[str] = []

    # Define section pairs (Japanese, English)
    required_section_pairs = [
        ("概要", "Overview"),
        ("タスク一覧", "Task List"),
        ("依存関係", "Dependencies"),
        ("マイルストーン", "Milestones"),
    ]

    for ja_section, en_section in required_section_pairs:
        # Check if either Japanese or English version exists
        ja_pattern = rf"## \d*\.?\s*{re.escape(ja_section)}"
        en_pattern = rf"## \d*\.?\s*{re.escape(en_section)}"

        ja_found = re.search(ja_pattern, tasks_content) or f"## {ja_section}" in tasks_content
        en_found = re.search(en_pattern, tasks_content) or f"## {en_section}" in tasks_content

        if not ja_found and not en_found:
            errors.append(f"Missing required section: {ja_section} or {en_section}")

    # Extract and validate task IDs - only unique IDs in task definitions
    # Look for task definitions (with **TASK pattern)
    task_definitions = re.findall(r"\*\*TASK-\d{2}(?:-\d{2}){0,2}\*\*", tasks_content)
    task_ids_in_defs = [t.strip("*") for t in task_definitions]

    # Check for duplicates only in definitions
    if len(task_ids_in_defs) != len(set(task_ids_in_defs)):
        duplicates = _find_duplicate_task_ids(task_ids_in_defs)
        duplicate_list = sorted(duplicates)
        errors.append(f"Duplicate TASK-IDs found: {', '.join(duplicate_list)}")

    # Extract all TASK patterns for validation
    all_task_ids = _extract_all_task_patterns(tasks_content)

    # Validate format - exclude non-TASK patterns
    invalid_task_ids = _find_invalid_task_ids(all_task_ids)
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


def validate_requirements(content: str, language: Language = Language.JAPANESE) -> dict[str, Any]:
    """Validate requirements document."""
    # Use AST-based validation if feature flag is enabled
    if USE_AST_VALIDATION:
        return validate_requirements_ast(content, language)

    # Otherwise, use legacy validation
    errors = validate_requirements_structure(content)

    # EARS validation
    ears_result = validate_ears_in_content(content, language)
    if ears_result.rate < 1.0:  # If not all requirements match EARS pattern
        for violation in ears_result.violations:
            errors.append(f"EARS violation (line {violation.line}): {violation.reason}")

    # Count stats
    req_ids = list(extract_req_ids(content))
    nfr_ids = re.findall(r"\bNFR-\d{2}\b", content)
    kpi_ids = re.findall(r"\bKPI-\d{2}\b", content)
    tr_ids = list(extract_tr_ids(content))

    # Find sections - check for both Japanese and English
    found_sections = []
    section_pairs = [
        ("サマリー", "Summary"),
        ("用語集", "Glossary"),
        ("スコープ", "Scope"),
        ("制約", "Constraints"),
        ("非機能要件", "Non-Functional Requirements"),
        ("KPI", "KPI"),
        ("機能要件", "Functional Requirements"),
        ("テスト要件", "Testing Requirements"),
    ]

    for ja_section, en_section in section_pairs:
        ja_pattern = rf"## \d*\.?\s*{re.escape(ja_section)}"
        en_pattern = rf"## \d*\.?\s*{re.escape(en_section)}"

        ja_found = re.search(ja_pattern, content) or f"## {ja_section}" in content
        en_found = re.search(en_pattern, content) or f"## {en_section}" in content

        if ja_found:
            found_sections.append(ja_section)
        elif en_found:
            found_sections.append(en_section)

    return {
        "isValid": len(errors) == 0,
        "issues": errors,
        "stats": {
            "totalRequirements": len(set(req_ids)),
            "totalNFRs": len(set(nfr_ids)),
            "totalKPIs": len(set(kpi_ids)),
            "totalTRs": len(set(tr_ids)),
        },
        "foundSections": found_sections,
        "ears": ears_result.to_dict()["ears"],
    }


def _extract_ids_from_traceability_section(content: str) -> tuple[set[str], set[str]]:
    """Extract REQ-IDs and TR-IDs only from the traceability section of design document."""
    # Find the traceability section (section 7) with optional "(必須)" suffix - support both languages
    traceability_match_ja = re.search(r"## \d*\.?\s*トレーサビリティ(\s*\([^)]*\))?.*?(?=## |$)", content, re.DOTALL)
    traceability_match_en = re.search(r"## \d*\.?\s*Traceability(\s*\([^)]*\))?.*?(?=## |$)", content, re.DOTALL)

    traceability_section = ""
    if traceability_match_ja:
        traceability_section = traceability_match_ja.group(0)
    elif traceability_match_en:
        traceability_section = traceability_match_en.group(0)
    else:
        return set(), set()

    req_ids = re.findall(r"\bREQ-\d{2}\b", traceability_section)
    tr_ids = re.findall(r"\bTR-\d{2}\b", traceability_section)
    return set(req_ids), set(tr_ids)


def validate_design(content: str, requirements_content: str | None = None) -> dict[str, Any]:
    """Validate design document."""
    # Use AST-based validation if feature flag is enabled
    if USE_AST_VALIDATION:
        return validate_design_ast(content, requirements_content)

    # Otherwise, use legacy validation
    errors = validate_design_structure(content)

    # Extract referenced REQ-IDs and TR-IDs only from traceability section for proper validation
    referenced_reqs, referenced_trs = _extract_ids_from_traceability_section(content)

    # If no traceability section found, add error - check for both languages
    traceability_ja = re.search(r"## \d*\.?\s*トレーサビリティ(\s*\([^)]*\))?", content)
    traceability_en = re.search(r"## \d*\.?\s*Traceability(\s*\([^)]*\))?", content)

    if not traceability_ja and not traceability_en:
        errors.append("Missing required traceability section (トレーサビリティ or Traceability)")

    # If requirements content provided, check traceability
    missing_refs = []
    if requirements_content:
        # Extract all requirements and TRs using common logic
        all_reqs = extract_req_ids(requirements_content)
        all_trs = extract_tr_ids(requirements_content)

        # Check REQ coverage using common function
        req_coverage_errors = check_requirement_coverage(all_reqs, referenced_reqs)
        errors.extend(req_coverage_errors)

        # Check TR coverage using common function
        tr_coverage_errors = check_tr_coverage(all_trs, referenced_trs)
        errors.extend(tr_coverage_errors)

        # Calculate missing references (both REQs and TRs)
        missing_reqs = list(all_reqs - referenced_reqs)
        missing_trs = list(all_trs - referenced_trs)
        missing_refs = missing_reqs + missing_trs

    return {
        "isValid": len(errors) == 0,
        "issues": errors,
        "stats": {
            "referencedRequirements": len(referenced_reqs),
            "referencedTRs": len(referenced_trs),
            "missingReferences": missing_refs,
        },
    }


def validate_tasks(
    content: str, requirements_content: str | None = None, design_content: str | None = None
) -> dict[str, Any]:
    """Validate tasks document."""
    # Use AST-based validation if feature flag is enabled
    if USE_AST_VALIDATION:
        return validate_tasks_ast(content, requirements_content, design_content)

    # Otherwise, use legacy validation
    errors = validate_tasks_structure(content)

    # Extract task IDs using common logic
    task_ids = extract_task_ids(content)

    # Extract and check task dependencies using common logic
    dependencies = extract_task_dependencies(content)
    circular_errors = check_circular_dependencies(dependencies)
    errors.extend(circular_errors)

    # Check traceability using common logic
    missing_req_refs: list[str] = []
    missing_tr_refs: list[str] = []
    missing_design_refs: list[str] = []

    # Extract REQ-IDs and TR-IDs referenced in tasks
    tasks_referencing_reqs = extract_req_ids(content)
    tasks_referencing_trs = extract_tr_ids(content)

    # Check if tasks reference requirements but no requirements content exists
    if tasks_referencing_reqs and not requirements_content:
        errors.append("Requirements not referenced - tasks reference REQ-IDs but requirements.md is missing")

    # Check if tasks reference test requirements but no requirements content exists
    if tasks_referencing_trs and not requirements_content:
        errors.append("Test requirements not referenced - tasks reference TR-IDs but requirements.md is missing")

    # Check requirement and TR traceability
    if requirements_content:
        all_reqs = extract_req_ids(requirements_content)
        all_trs = extract_tr_ids(requirements_content)

        # Check REQ coverage
        req_coverage_errors, missing_req_refs = check_requirement_coverage_with_threshold(
            all_reqs, tasks_referencing_reqs, context="tasks"
        )
        errors.extend(req_coverage_errors)

        # Check TR coverage using common function
        tr_coverage_errors = check_tr_coverage(all_trs, tasks_referencing_trs)
        errors.extend(tr_coverage_errors)
        missing_tr_refs = list(all_trs - tasks_referencing_trs)

    # Check if tasks reference design components but no design content exists
    task_content_lines = content.split("\n")
    dc_references = []
    for line in task_content_lines:
        if "**DC**:" in line:
            # Extract component names from DC field
            dc_part = line.split("**DC**:")[-1].strip()
            components = re.findall(r"\*\*([a-zA-Z0-9_-]+)\*\*", dc_part)
            dc_references.extend(components)

    if dc_references and not design_content:
        errors.append("Design components not referenced - tasks reference design components but design.md is missing")

    # Check design component and test scenario traceability
    if design_content:
        # Extract both design components and test scenarios
        design_components = extract_design_components(design_content)
        test_scenarios = extract_test_scenarios(design_content)
        all_design_elements = design_components | test_scenarios

        # Find references to all design elements in tasks
        tasks_referencing_design = find_component_references(all_design_elements, content)

        # Check coverage for all design elements (components + test scenarios)
        coverage_errors, missing_design_refs = check_design_coverage_with_threshold(
            all_design_elements, tasks_referencing_design, context="tasks"
        )
        errors.extend(coverage_errors)

    return {
        "isValid": len(errors) == 0,
        "issues": errors,
        "stats": {
            "totalTasks": len(task_ids),
            "dependencies": len(dependencies),
            "missingRequirementReferences": missing_req_refs,
            "missingTRReferences": missing_tr_refs,
            "missingDesignReferences": missing_design_refs,
        },
    }
