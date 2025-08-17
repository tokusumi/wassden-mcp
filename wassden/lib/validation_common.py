"""Common validation logic for traceability checking."""

import re

# Display limits for error messages
MAX_DISPLAY_REQUIREMENTS = 5
MAX_DISPLAY_COMPONENTS = 3
DEPENDENCY_PARTS_COUNT = 2


def extract_req_ids(content: str) -> set[str]:
    """Extract REQ-IDs from content using consistent regex."""
    if not content:
        return set()
    return set(re.findall(r"\bREQ-\d{2}\b", content))


def extract_nfr_ids(content: str) -> set[str]:
    """Extract NFR-IDs from content using consistent regex."""
    if not content:
        return set()
    return set(re.findall(r"\bNFR-\d{2}\b", content))


def extract_kpi_ids(content: str) -> set[str]:
    """Extract KPI-IDs from content using consistent regex."""
    if not content:
        return set()
    return set(re.findall(r"\bKPI-\d{2}\b", content))


def extract_task_ids(content: str) -> set[str]:
    """Extract TASK-IDs from content using consistent regex."""
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


def check_requirement_coverage(all_requirements: set[str], referenced_requirements: set[str]) -> list[str]:
    """Check requirement coverage and return validation errors."""
    errors = []
    missing_refs = list(all_requirements - referenced_requirements)

    if missing_refs:
        errors.append(f"Missing references to requirements: {', '.join(sorted(missing_refs))}")

    return errors


def check_requirement_coverage_with_threshold(
    all_requirements: set[str], referenced_requirements: set[str], context: str = "tasks"
) -> tuple[list[str], list[str]]:
    """Check requirement coverage - 100% coverage required."""
    errors = []
    missing_refs = list(all_requirements - referenced_requirements)

    # 100% coverage required - any missing reference is an error
    if missing_refs:
        display_refs = missing_refs[:MAX_DISPLAY_REQUIREMENTS]
        suffix = "..." if len(missing_refs) > MAX_DISPLAY_REQUIREMENTS else ""
        errors.append(f"Requirements not referenced in {context}: {', '.join(sorted(display_refs))}{suffix}")

    return errors, missing_refs


def check_design_coverage_with_threshold(
    all_components: set[str], referenced_components: set[str], context: str = "tasks"
) -> tuple[list[str], list[str]]:
    """Check design component coverage - 100% coverage required."""
    errors = []
    missing_refs = list(all_components - referenced_components)

    # 100% coverage required - any missing reference is an error
    if missing_refs:
        display_refs = missing_refs[:MAX_DISPLAY_COMPONENTS]
        suffix = "..." if len(missing_refs) > MAX_DISPLAY_COMPONENTS else ""
        errors.append(f"Design components not referenced in {context}: {', '.join(sorted(display_refs))}{suffix}")

    return errors, missing_refs


def find_component_references(components: set[str], content: str) -> set[str]:
    """Find which components are referenced in content."""
    referenced = set()
    for component in components:
        if component in content:
            referenced.add(component)
    return referenced


def extract_task_dependencies(content: str) -> dict[str, list[str]]:
    """Extract task dependencies from content using consistent logic."""
    dependencies = {}
    for line in content.split("\n"):
        if "依存" in line or "Depends on" in line:
            parts = line.split(":")
            if len(parts) == DEPENDENCY_PARTS_COUNT:
                task_match = re.search(r"\bTASK-\d{2}(?:-\d{2}){0,2}\b", parts[0])
                if task_match:
                    task_id = task_match.group(0)
                    dep_ids = re.findall(r"\bTASK-\d{2}(?:-\d{2}){0,2}\b", parts[1])
                    dependencies[task_id] = dep_ids
    return dependencies


def check_circular_dependencies(dependencies: dict[str, list[str]]) -> list[str]:
    """Check for circular dependencies and return errors."""
    errors = []
    for task_id, deps in dependencies.items():
        circular_deps = [
            f"Circular dependency detected: {task_id} <-> {dep}"
            for dep in deps
            if dep in dependencies and task_id in dependencies[dep]
        ]
        errors.extend(circular_deps)
    return errors
