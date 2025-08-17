"""Traceability analysis utilities."""

import re
from typing import Any


def extract_req_ids(content: str) -> set[str]:
    """Extract REQ-XX IDs from content."""
    if not content:
        return set()
    return set(re.findall(r"\bREQ-\d{2}\b", content))


def extract_task_ids(content: str) -> set[str]:
    """Extract TASK-XX-XX IDs from content."""
    if not content:
        return set()
    return set(re.findall(r"\bTASK-\d{2}(?:-\d{2}){0,2}\b", content))


def extract_design_components(content: str) -> set[str]:
    """Extract design component names from design document."""
    if not content:
        return set()

    components = set()

    # Look for component definitions in the form: **component-name**:
    component_matches = re.findall(r"\*\*([a-zA-Z0-9_-]+)\*\*:", content)
    components.update(component_matches)

    # Also look for section headers that might be components
    section_matches = re.findall(r"###\s+([a-zA-Z0-9_-]+)", content)
    components.update(section_matches)

    return components


def build_traceability_matrix(
    requirements_content: str | None,
    design_content: str | None,
    tasks_content: str | None,
) -> dict[str, Any]:
    """Build a complete traceability matrix from spec documents."""
    matrix: dict[str, Any] = {
        "requirements": set(),
        "design_components": set(),
        "tasks": set(),
        "req_to_design": {},
        "design_to_tasks": {},
        "task_dependencies": {},
    }

    _extract_all_ids(matrix, requirements_content, design_content, tasks_content)
    _build_req_to_design_mapping(matrix, requirements_content, design_content)
    _build_design_to_tasks_mapping(matrix, design_content, tasks_content)
    _extract_task_dependencies(matrix, tasks_content)

    return matrix


def _extract_all_ids(
    matrix: dict[str, Any], requirements_content: str | None, design_content: str | None, tasks_content: str | None
) -> None:
    """Extract all IDs from the documents."""
    if requirements_content:
        matrix["requirements"] = extract_req_ids(requirements_content)

    if design_content:
        matrix["design_components"] = extract_design_components(design_content)

    if tasks_content:
        matrix["tasks"] = extract_task_ids(tasks_content)


def _build_req_to_design_mapping(
    matrix: dict[str, Any], requirements_content: str | None, design_content: str | None
) -> None:
    """Build mapping from requirements to design components."""
    if not (requirements_content and design_content):
        return

    for req_id in matrix["requirements"]:
        pattern = rf"{req_id}.*?(?=REQ-\d{{2}}|##|$)"
        matches = re.findall(pattern, design_content, re.DOTALL)

        related_components = set()
        for match in matches:
            comp_matches = re.findall(r"\*\*([a-zA-Z0-9_-]+)\*\*", match[:500])
            related_components.update(comp_matches)

        if related_components:
            matrix["req_to_design"][req_id] = related_components


def _build_design_to_tasks_mapping(
    matrix: dict[str, Any], design_content: str | None, tasks_content: str | None
) -> None:
    """Build mapping from design components to tasks."""
    if not (design_content and tasks_content):
        return

    for component in matrix["design_components"]:
        if component in tasks_content:
            related_tasks = set()
            pattern = rf"{re.escape(component)}.*?TASK-\d{{2}}(?:-\d{{2}}){{0,2}}"
            matches = re.findall(pattern, tasks_content, re.DOTALL)
            for match in matches:
                task_matches = re.findall(r"TASK-\d{2}(?:-\d{2}){0,2}", match)
                related_tasks.update(task_matches)

            if related_tasks:
                matrix["design_to_tasks"][component] = related_tasks


def _extract_task_dependencies(matrix: dict[str, Any], tasks_content: str | None) -> None:
    """Extract task dependencies from tasks content."""
    if not tasks_content:
        return

    for line in tasks_content.split("\n"):
        if "依存" in line or "Depends" in line.lower():
            task_match = re.search(r"\bTASK-\d{2}(?:-\d{2}){0,2}\b", line)
            if task_match:
                task_id = task_match.group(0)
                dep_part = line.split(":", 1)[-1] if ":" in line else line
                dep_ids = re.findall(r"\bTASK-\d{2}(?:-\d{2}){0,2}\b", dep_part)
                if dep_ids and dep_ids[0] != task_id:  # Avoid self-dependency
                    matrix["task_dependencies"][task_id] = set(dep_ids)


def check_circular_dependencies(dependencies: dict[str, set[str]]) -> list[str]:
    """Check for circular dependencies in task graph."""
    errors = []

    def has_cycle(node: str, visited: set[str], rec_stack: set[str]) -> bool:
        visited.add(node)
        rec_stack.add(node)

        if node in dependencies:
            for neighbor in dependencies[node]:
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    errors.append(f"Circular dependency: {node} -> {neighbor}")
                    return True

        rec_stack.remove(node)
        return False

    visited: set[str] = set()
    for node in dependencies:
        if node not in visited:
            has_cycle(node, visited, set())

    return errors


def calculate_coverage_metrics(matrix: dict[str, Any]) -> dict[str, float]:
    """Calculate coverage metrics from traceability matrix."""
    metrics = {
        "requirement_coverage": 0.0,
        "design_coverage": 0.0,
        "task_coverage": 0.0,
    }

    # Requirement coverage: % of requirements with design references
    if matrix["requirements"]:
        covered_reqs = len([r for r in matrix["requirements"] if r in matrix["req_to_design"]])
        metrics["requirement_coverage"] = (covered_reqs / len(matrix["requirements"])) * 100

    # Design coverage: % of design components with task references
    if matrix["design_components"]:
        covered_components = len([c for c in matrix["design_components"] if c in matrix["design_to_tasks"]])
        metrics["design_coverage"] = (covered_components / len(matrix["design_components"])) * 100

    # Task coverage: % of tasks with proper dependencies
    if matrix["tasks"]:
        tasks_with_deps = len(matrix["task_dependencies"])
        # Assume first phase tasks don't need dependencies
        expected_deps = max(0, len(matrix["tasks"]) - len([t for t in matrix["tasks"] if t.startswith("TASK-01-")]))
        if expected_deps > 0:
            metrics["task_coverage"] = (tasks_with_deps / expected_deps) * 100
        else:
            metrics["task_coverage"] = 100.0

    return metrics
