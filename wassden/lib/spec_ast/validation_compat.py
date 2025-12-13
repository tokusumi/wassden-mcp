"""Compatibility layer for AST-based validation.

This module provides backward-compatible wrappers around the new AST-based
validation system, maintaining the existing function interfaces while using
the new validation engine internally.
"""

import re
from typing import Any

from wassden.language_types import Language

from .blocks import BlockType, DocumentBlock, ListItemBlock, RequirementBlock, SectionBlock, TaskBlock
from .id_extractor import IDExtractor
from .parser import SpecMarkdownParser
from .validation_engine import ValidationEngine
from .validation_rules import ValidationResult

# Constants
HEADING_LEVEL_2 = 2  # Level 2 headings (##) for backward compatibility with legacy validation


def extract_stats_from_document(document: DocumentBlock, doc_type: str) -> dict[str, Any]:
    """Extract statistics from parsed document.

    Args:
        document: Parsed document block
        doc_type: Type of document (requirements, design, tasks)

    Returns:
        Dictionary with statistics
    """
    if doc_type == "requirements":
        return _extract_requirements_stats(document)
    if doc_type == "design":
        return _extract_design_stats(document)
    if doc_type == "tasks":
        return _extract_tasks_stats(document)
    return {}


def _extract_requirements_stats(document: DocumentBlock) -> dict[str, Any]:  # noqa: C901, PLR0912
    """Extract statistics from requirements document."""
    req_ids = set()
    nfr_ids = set()
    kpi_ids = set()
    tr_ids = set()

    # Extract from RequirementBlock objects (if parser creates them)
    req_blocks = document.get_blocks_by_type(BlockType.REQUIREMENT)
    for block in req_blocks:
        if isinstance(block, RequirementBlock) and block.req_id:
            if block.req_id.startswith("REQ-"):
                req_ids.add(block.req_id)
            elif block.req_id.startswith("NFR-"):
                nfr_ids.add(block.req_id)
            elif block.req_id.startswith("KPI-"):
                kpi_ids.add(block.req_id)
            elif block.req_id.startswith("TR-"):
                tr_ids.add(block.req_id)

    # Also extract from SectionBlock titles (current parser behavior)
    section_blocks = document.get_blocks_by_type(BlockType.SECTION)
    for block in section_blocks:
        if isinstance(block, SectionBlock) and block.title:
            req_id, _, _ = IDExtractor.extract_req_id_from_text(block.title)
            if req_id:
                if req_id.startswith("REQ-"):
                    req_ids.add(req_id)
                elif req_id.startswith("NFR-"):
                    nfr_ids.add(req_id)
                elif req_id.startswith("KPI-"):
                    kpi_ids.add(req_id)
                elif req_id.startswith("TR-"):
                    tr_ids.add(req_id)

    return {
        "totalRequirements": len(req_ids),
        "totalNFRs": len(nfr_ids),
        "totalKPIs": len(kpi_ids),
        "totalTRs": len(tr_ids),
    }


def _extract_design_stats(document: DocumentBlock) -> dict[str, Any]:  # noqa: C901, PLR0912
    """Extract statistics from design document."""
    referenced_reqs = set()
    referenced_trs = set()

    # Extract from RequirementBlock objects (if parser creates them)
    req_blocks = document.get_blocks_by_type(BlockType.REQUIREMENT)
    for block in req_blocks:
        if isinstance(block, RequirementBlock) and block.req_id:
            if block.req_id.startswith("REQ-"):
                referenced_reqs.add(block.req_id)
            elif block.req_id.startswith("TR-"):
                referenced_trs.add(block.req_id)

    # Also extract from SectionBlock titles (current parser behavior)
    section_blocks = document.get_blocks_by_type(BlockType.SECTION)
    for block in section_blocks:
        if isinstance(block, SectionBlock) and block.title:
            req_id, _, _ = IDExtractor.extract_req_id_from_text(block.title)
            if req_id:
                if req_id.startswith("REQ-"):
                    referenced_reqs.add(req_id)
                elif req_id.startswith("TR-"):
                    referenced_trs.add(req_id)

    # Also extract from ListItemBlocks (for traceability section)
    list_item_blocks = document.get_blocks_by_type(BlockType.LIST_ITEM)
    for block in list_item_blocks:
        if isinstance(block, ListItemBlock) and block.content:
            # Extract all REQ-IDs from list item content
            req_ids = list(IDExtractor.extract_all_req_ids(block.content))
            for req_id in req_ids:
                if req_id.startswith("REQ-"):
                    referenced_reqs.add(req_id)
                elif req_id.startswith("TR-"):
                    referenced_trs.add(req_id)

    return {
        "referencedRequirements": len(referenced_reqs),
        "referencedTRs": len(referenced_trs),
        "missingReferences": [],  # Will be populated by validation results
    }


def _extract_tasks_stats(document: DocumentBlock) -> dict[str, Any]:
    """Extract statistics from tasks document."""
    task_ids = set()
    dependencies = 0

    # Extract from TaskBlock objects (if parser creates them)
    task_blocks = document.get_blocks_by_type(BlockType.TASK)
    for block in task_blocks:
        if isinstance(block, TaskBlock):
            if block.task_id:
                task_ids.add(block.task_id)
            if block.dependencies:
                dependencies += len(block.dependencies)

    # Also extract from SectionBlock titles (current parser behavior)
    section_blocks = document.get_blocks_by_type(BlockType.SECTION)
    for block in section_blocks:
        if isinstance(block, SectionBlock) and block.title:
            task_id, _ = IDExtractor.extract_task_id_from_text(block.title)
            if task_id:
                task_ids.add(task_id)
            # Extract dependencies from block content if available
            if block.raw_content:
                task_deps = IDExtractor.extract_task_dependencies(block.raw_content)
                dependencies += len(task_deps)

    return {
        "totalTasks": len(task_ids),
        "dependencies": dependencies,
        "missingRequirementReferences": [],  # Will be populated by validation results
        "missingTRReferences": [],
        "missingDesignReferences": [],
    }


def extract_found_sections(document: DocumentBlock) -> list[str]:
    """Extract list of found section titles from document.

    Args:
        document: Parsed document block

    Returns:
        List of section titles found in document (level 2 headings only for backward compatibility)
    """
    section_blocks = document.get_blocks_by_type(BlockType.SECTION)
    # Only include level 2 sections for backward compatibility with legacy validation
    return [
        block.title
        for block in section_blocks
        if isinstance(block, SectionBlock) and block.title and block.level == HEADING_LEVEL_2
    ]


def convert_validation_results_to_errors(results: list[ValidationResult]) -> list[str]:
    """Convert AST validation results to simple error list.

    Args:
        results: List of validation results from AST validation

    Returns:
        List of error message strings
    """
    errors: list[str] = []
    for result in results:
        if not result.is_valid:
            errors.extend(error.message for error in result.errors)
    return errors


def convert_validation_results_to_dict(results: list[ValidationResult]) -> dict[str, Any]:
    """Convert AST validation results to legacy dict format.

    Args:
        results: List of validation results from AST validation

    Returns:
        Dictionary with validation results in legacy format
    """
    # Collect all errors
    all_errors: list[str] = []
    for result in results:
        if not result.is_valid:
            all_errors.extend(error.message for error in result.errors)

    # Determine if valid
    is_valid = len(all_errors) == 0

    return {
        "isValid": is_valid,
        "issues": all_errors,
    }


def extract_missing_references_from_results(results: list[ValidationResult]) -> dict[str, list[str]]:
    """Extract missing references from validation results.

    Args:
        results: List of validation results

    Returns:
        Dictionary with missing references by type
    """
    missing_refs: dict[str, list[str]] = {
        "requirements": [],
        "test_requirements": [],
        "design": [],
    }

    for result in results:
        for error in result.errors:
            message = error.message

            # Extract missing requirements (REQ-XX, NFR-XX, KPI-XX)
            if "Requirements not referenced" in message or "Requirement not referenced" in message:
                # Parse: "Requirements not referenced: REQ-01, REQ-02..."
                match = re.search(r"(?:Requirements?|REQ-\d+)[^:]*:\s*(.+)", message)
                if match:
                    refs_str = match.group(1).replace("...", "")
                    refs = [r.strip() for r in refs_str.split(",") if r.strip().startswith(("REQ-", "NFR-", "KPI-"))]
                    missing_refs["requirements"].extend(refs)

            # Extract missing test requirements (TR-XX)
            if "Test requirement not referenced" in message or "TR-" in message:
                match = re.search(r"(TR-\d+)", message)
                if match:
                    missing_refs["test_requirements"].append(match.group(1))

            # Extract missing design components
            if "not referenced in tasks:" in message:
                # Pattern: "Design components not referenced in tasks: comp1, comp2, comp3..."
                # or "Test scenario not referenced in tasks: test-xxx"
                list_match = re.search(r"not referenced in tasks:\s*(.+)", message)
                if list_match:
                    components_str = list_match.group(1).replace("...", "")
                    # Split by comma and extract component names
                    components = [c.strip() for c in components_str.split(",") if c.strip()]
                    # Filter to only valid component/scenario names
                    valid_comps = [c for c in components if re.match(r"^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)+$", c)]
                    missing_refs["design"].extend(valid_comps)

    # Remove duplicates and sort
    for key, values in missing_refs.items():
        missing_refs[key] = sorted(set(values))

    return missing_refs


def validate_requirements_structure_ast(req_content: str, language: Language = Language.JAPANESE) -> list[str]:
    """Validate requirements document structure using AST validation.

    This is a compatibility wrapper that uses the new AST-based validation
    while maintaining the existing function interface.

    Args:
        req_content: Requirements document content
        language: Language for validation

    Returns:
        List of error messages (empty if valid)
    """
    # Parse document
    parser = SpecMarkdownParser(language)
    document = parser.parse(req_content)

    # Validate using AST engine
    engine = ValidationEngine(language)
    results = engine.validate_requirements(document)

    # Convert to legacy format
    return convert_validation_results_to_errors(results)


def validate_design_structure_ast(design_content: str, language: Language = Language.JAPANESE) -> list[str]:
    """Validate design document structure using AST validation.

    This is a compatibility wrapper that uses the new AST-based validation
    while maintaining the existing function interface.

    Args:
        design_content: Design document content
        language: Language for validation

    Returns:
        List of error messages (empty if valid)
    """
    # Parse document
    parser = SpecMarkdownParser(language)
    document = parser.parse(design_content)

    # Validate using AST engine
    engine = ValidationEngine(language)
    results = engine.validate_design(document)

    # Convert to legacy format
    return convert_validation_results_to_errors(results)


def validate_tasks_structure_ast(tasks_content: str, language: Language = Language.JAPANESE) -> list[str]:
    """Validate tasks document structure using AST validation.

    This is a compatibility wrapper that uses the new AST-based validation
    while maintaining the existing function interface.

    Args:
        tasks_content: Tasks document content
        language: Language for validation

    Returns:
        List of error messages (empty if valid)
    """
    # Parse document
    parser = SpecMarkdownParser(language)
    document = parser.parse(tasks_content)

    # Validate using AST engine
    engine = ValidationEngine(language)
    results = engine.validate_tasks(document)

    # Convert to legacy format
    return convert_validation_results_to_errors(results)


def validate_requirements_ast(content: str, language: Language = Language.JAPANESE) -> dict[str, Any]:
    """Validate requirements document using AST validation.

    This is a compatibility wrapper that uses the new AST-based validation
    while maintaining the existing function interface.

    Args:
        content: Requirements document content
        language: Language for validation

    Returns:
        Dictionary with validation results
    """
    # Parse document
    parser = SpecMarkdownParser(language)
    document = parser.parse(content)

    # Validate using AST engine
    engine = ValidationEngine(language)
    results = engine.validate_requirements(document)

    # Convert to legacy format
    result_dict = convert_validation_results_to_dict(results)

    # Extract stats from parsed document
    result_dict["stats"] = extract_stats_from_document(document, "requirements")
    result_dict["foundSections"] = extract_found_sections(document)
    result_dict["ears"] = {"pattern": "ubiquitous", "total": 0, "matched": 0, "rate": 1.0, "violations": []}

    return result_dict


def validate_design_ast(
    content: str, requirements_content: str | None = None, language: Language = Language.JAPANESE
) -> dict[str, Any]:
    """Validate design document using AST validation.

    This is a compatibility wrapper that uses the new AST-based validation
    while maintaining the existing function interface.

    Args:
        content: Design document content
        requirements_content: Optional requirements document for traceability
        language: Language for validation

    Returns:
        Dictionary with validation results
    """
    # Parse documents
    parser = SpecMarkdownParser(language)
    document = parser.parse(content)

    # Create engine and set context
    engine = ValidationEngine(language)
    if requirements_content:
        req_document = parser.parse(requirements_content)
        engine.set_requirements_document(req_document)

    # Validate using AST engine
    results = engine.validate_design(document)

    # Convert to legacy format
    result_dict = convert_validation_results_to_dict(results)

    # Extract stats from parsed document
    result_dict["stats"] = extract_stats_from_document(document, "design")
    result_dict["foundSections"] = extract_found_sections(document)

    return result_dict


def validate_tasks_ast(
    content: str,
    requirements_content: str | None = None,
    design_content: str | None = None,
    language: Language = Language.JAPANESE,
) -> dict[str, Any]:
    """Validate tasks document using AST validation.

    This is a compatibility wrapper that uses the new AST-based validation
    while maintaining the existing function interface.

    Args:
        content: Tasks document content
        requirements_content: Optional requirements document for traceability
        design_content: Optional design document for traceability
        language: Language for validation

    Returns:
        Dictionary with validation results
    """
    # Parse documents
    parser = SpecMarkdownParser(language)
    document = parser.parse(content)

    # Create engine and set context
    engine = ValidationEngine(language)
    if requirements_content:
        req_document = parser.parse(requirements_content)
        engine.set_requirements_document(req_document)
    if design_content:
        design_document = parser.parse(design_content)
        engine.set_design_document(design_document)

    # Validate using AST engine
    results = engine.validate_tasks(document)

    # Convert to legacy format
    result_dict = convert_validation_results_to_dict(results)

    # Extract stats from parsed document
    result_dict["stats"] = extract_stats_from_document(document, "tasks")
    result_dict["foundSections"] = extract_found_sections(document)

    # Extract missing references from validation results
    missing_refs = extract_missing_references_from_results(results)
    result_dict["stats"]["missingRequirementReferences"] = missing_refs.get("requirements", [])
    result_dict["stats"]["missingTRReferences"] = missing_refs.get("test_requirements", [])
    result_dict["stats"]["missingDesignReferences"] = missing_refs.get("design", [])

    return result_dict
