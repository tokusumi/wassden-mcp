"""Traceability analysis and change impact assessment."""

import re
from pathlib import Path
from typing import Any

from wassden.i18n import get_i18n
from wassden.lib import traceability
from wassden.types import HandlerResponse, Language, SpecDocuments, TextContent

# Constants
COMPLETE_COVERAGE_PERCENTAGE = 100


async def handle_get_traceability(
    specs: SpecDocuments,
) -> HandlerResponse:
    """Generate traceability report."""
    i18n = get_i18n(specs.language)

    matrix = traceability.build_traceability_matrix(
        await specs.get_requirements(),
        await specs.get_design(),
        await specs.get_tasks(),
    )

    report_lines = _build_traceability_report(matrix, i18n)

    return HandlerResponse(content=[TextContent(text="\n".join(report_lines))])


def _build_traceability_report(matrix: dict[str, Any], i18n: Any) -> list[str]:
    """Build the complete traceability report."""
    report_lines = [i18n.t("traceability.report.title") + "\n"]

    _add_overview_section(report_lines, matrix, i18n)
    _add_mapping_sections(report_lines, matrix, i18n)
    _add_coverage_analysis(report_lines, matrix, i18n)
    _add_task_dependencies(report_lines, matrix, i18n)
    _add_summary_section(report_lines, matrix, i18n)

    return report_lines


def _add_overview_section(report_lines: list[str], matrix: dict[str, Any], i18n: Any) -> None:
    """Add overview section to the report."""
    report_lines.extend(
        [
            i18n.t("traceability.report.overview.title"),
            i18n.t("traceability.report.overview.requirements_count", count=len(matrix["requirements"])),
            i18n.t("traceability.report.overview.design_elements_count", count=len(matrix["design_components"])),
            i18n.t("traceability.report.overview.tasks_count", count=len(matrix["tasks"])) + "\n",
        ]
    )


def _add_mapping_sections(report_lines: list[str], matrix: dict[str, Any], i18n: Any) -> None:
    """Add mapping sections to the report."""
    # Requirements to Design mapping
    if matrix["req_to_design"]:
        report_lines.append(i18n.t("traceability.report.mappings.req_to_design"))
        for req_id, design_refs in sorted(matrix["req_to_design"].items()):
            if design_refs:
                report_lines.append(f"- **{req_id}** → {', '.join(sorted(design_refs))}")
            else:
                report_lines.append(f"- **{req_id}** → ⚠️ {i18n.t('traceability.report.mappings.no_design_reference')}")
        report_lines.append("")

    # Design to Tasks mapping
    if matrix["design_to_tasks"]:
        report_lines.append(i18n.t("traceability.report.mappings.design_to_task"))
        for component, task_refs in sorted(matrix["design_to_tasks"].items()):
            if task_refs:
                report_lines.append(f"- **{component}** → {', '.join(sorted(task_refs))}")
            else:
                report_lines.append(f"- **{component}** → ⚠️ {i18n.t('traceability.report.mappings.no_task_reference')}")
        report_lines.append("")


def _add_coverage_analysis(report_lines: list[str], matrix: dict[str, Any], i18n: Any) -> None:
    """Add coverage analysis section to the report."""
    report_lines.append(i18n.t("traceability.report.coverage.title"))

    # Requirements coverage
    uncovered_reqs = matrix["requirements"] - set(matrix["req_to_design"].keys())
    if uncovered_reqs:
        report_lines.append(i18n.t("traceability.report.coverage.undesigned_requirements"))
        report_lines.extend(f"- {req}" for req in sorted(uncovered_reqs))
        report_lines.append("")

    # Design coverage
    uncovered_design = matrix["design_components"] - set(matrix["design_to_tasks"].keys())
    if uncovered_design:
        report_lines.append(i18n.t("traceability.report.coverage.untasked_design_elements"))
        report_lines.extend(f"- {component}" for component in sorted(uncovered_design))
        report_lines.append("")


def _add_task_dependencies(report_lines: list[str], matrix: dict[str, Any], i18n: Any) -> None:
    """Add task dependencies section to the report."""
    if matrix["task_dependencies"]:
        report_lines.append(i18n.t("traceability.report.dependencies.title"))
        for task_id, deps in sorted(matrix["task_dependencies"].items()):
            if deps:
                report_lines.append(f"- **{task_id}** ← {', '.join(sorted(deps))}")
        report_lines.append("")


def _add_summary_section(report_lines: list[str], matrix: dict[str, Any], i18n: Any) -> None:
    """Add summary section to the report."""
    req_coverage = len(matrix["req_to_design"]) / len(matrix["requirements"]) * 100 if matrix["requirements"] else 0
    design_coverage = (
        len(matrix["design_to_tasks"]) / len(matrix["design_components"]) * 100 if matrix["design_components"] else 0
    )

    report_lines.extend(
        [
            i18n.t("traceability.report.summary.title"),
            i18n.t("traceability.report.summary.requirements_coverage", coverage=f"{req_coverage:.1f}"),
            i18n.t("traceability.report.summary.design_coverage", coverage=f"{design_coverage:.1f}"),
        ]
    )

    if req_coverage == COMPLETE_COVERAGE_PERCENTAGE and design_coverage == COMPLETE_COVERAGE_PERCENTAGE:
        report_lines.append(f"\n{i18n.t('traceability.report.summary.complete_traceability')}")
    else:
        report_lines.append(f"\n{i18n.t('traceability.report.summary.improvement_needed')}")


async def handle_analyze_changes(
    changed_file: Path,
    change_description: str,
    language: Language = Language.JAPANESE,
) -> HandlerResponse:
    """Analyze impact of changes to spec documents."""
    i18n = get_i18n(language)
    spec_type = _determine_spec_type(changed_file)

    if spec_type is None:
        return _handle_non_spec_file_change(changed_file, change_description, i18n)

    return await _handle_spec_file_change(changed_file, change_description, spec_type, i18n)


def _determine_spec_type(changed_file: Path) -> str | None:
    """Determine the type of spec file from the filename."""
    file_lower = str(changed_file).lower()
    if "requirements" in file_lower:
        return "requirements"
    if "design" in file_lower:
        return "design"
    if "tasks" in file_lower:
        return "tasks"
    return None


def _handle_non_spec_file_change(changed_file: Path, change_description: str, i18n: Any) -> HandlerResponse:
    """Handle changes to non-spec files."""
    impact_lines = [i18n.t("traceability.changes.non_spec_title") + "\n"]
    impact_lines.append(i18n.t("traceability.changes.non_spec_change_details.title"))
    impact_lines.append(i18n.t("traceability.changes.non_spec_change_details.file_label", file=str(changed_file)))
    impact_lines.append(
        i18n.t("traceability.changes.non_spec_change_details.change_label", change=change_description) + "\n"
    )

    file_lower = str(changed_file).lower()
    if file_lower.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c")):
        impact_lines.extend(
            [
                i18n.t("traceability.changes.non_spec_change_details.implementation_files.title"),
                i18n.t("traceability.changes.non_spec_change_details.implementation_files.direct_change"),
                i18n.t("traceability.changes.non_spec_change_details.implementation_files.consistency_check"),
            ]
        )
    elif file_lower.endswith((".md", ".txt", ".doc")):
        impact_lines.extend(
            [
                i18n.t("traceability.changes.non_spec_change_details.document_files.title"),
                i18n.t("traceability.changes.non_spec_change_details.document_files.document_update"),
                i18n.t("traceability.changes.non_spec_change_details.document_files.consistency_check"),
            ]
        )
    else:
        impact_lines.extend(
            [
                i18n.t("traceability.changes.non_spec_change_details.other_files.title"),
                i18n.t("traceability.changes.non_spec_change_details.other_files.change_detected"),
            ]
        )

    impact_lines.extend(
        [
            "\n" + i18n.t("traceability.changes.non_spec_change_details.recommended_actions.title"),
            i18n.t("traceability.changes.non_spec_change_details.recommended_actions.reflect_changes"),
            i18n.t("traceability.changes.non_spec_change_details.recommended_actions.run_validation"),
            i18n.t("traceability.changes.non_spec_change_details.recommended_actions.check_consistency"),
        ]
    )

    return HandlerResponse(content=[TextContent(text="\n".join(impact_lines))])


async def _handle_spec_file_change(
    changed_file: Path, change_description: str, spec_type: str, i18n: Any
) -> HandlerResponse:
    """Handle changes to spec files."""
    # Use the changed file to locate sibling specs
    specs = await SpecDocuments.from_feature_dir(changed_file.parent)
    matrix = traceability.build_traceability_matrix(
        await specs.get_requirements(),
        await specs.get_design(),
        await specs.get_tasks(),
    )

    impact_lines = _build_change_header(changed_file, change_description, i18n)
    changed_ids = _extract_changed_ids(change_description)

    if spec_type == "requirements":
        _add_requirements_impact(impact_lines, changed_ids, matrix, i18n)
    elif spec_type == "design":
        _add_design_impact(impact_lines, changed_ids, matrix, i18n)
    elif spec_type == "tasks":
        _add_tasks_impact(impact_lines, changed_ids, matrix, i18n)

    impact_lines.extend(
        [
            "\n" + i18n.t("traceability.changes.spec_change_details.next_steps.title"),
            i18n.t("traceability.changes.spec_change_details.next_steps.update_documents"),
            i18n.t("traceability.changes.spec_change_details.next_steps.validate_tools"),
            i18n.t("traceability.changes.spec_change_details.next_steps.check_traceability"),
        ]
    )

    return HandlerResponse(content=[TextContent(text="\n".join(impact_lines))])


def _build_change_header(changed_file: Path, change_description: str, i18n: Any) -> list[str]:
    """Build the header section of the change impact report."""
    return [
        i18n.t("traceability.changes.non_spec_title") + "\n",
        i18n.t("traceability.changes.non_spec_change_details.title"),
        i18n.t("traceability.changes.non_spec_change_details.file_label", file=str(changed_file)),
        i18n.t("traceability.changes.non_spec_change_details.change_label", change=change_description) + "\n",
    ]


def _extract_changed_ids(change_description: str) -> set[str]:
    """Extract changed IDs from the change description."""
    changed_ids = set()
    changed_ids.update(re.findall(r"\bREQ-\d{2}\b", change_description))
    changed_ids.update(re.findall(r"\bTASK-\d{2}(?:-\d{2}){0,2}\b", change_description))
    return changed_ids


def _add_requirements_impact(impact_lines: list[str], changed_ids: set[str], matrix: dict[str, Any], i18n: Any) -> None:
    """Add requirements change impact analysis."""
    impact_lines.append(i18n.t("traceability.changes.requirements_impact.title"))
    affected_design = set()
    for req_id in changed_ids:
        if req_id in matrix["req_to_design"]:
            affected_design.update(matrix["req_to_design"][req_id])

    if affected_design:
        impact_lines.extend(f"- {component}" for component in sorted(affected_design))
        impact_lines.append("\n" + i18n.t("traceability.changes.requirements_impact.recommendations_title"))
        recommendations = i18n.t("traceability.changes.requirements_impact.recommendations")
        impact_lines.extend(recommendations)
    else:
        impact_lines.append(i18n.t("traceability.changes.requirements_impact.no_impact"))


def _add_design_impact(impact_lines: list[str], changed_ids: set[str], matrix: dict[str, Any], i18n: Any) -> None:
    """Add design change impact analysis."""
    impact_lines.append(i18n.t("traceability.changes.design_impact.title"))
    affected_tasks = set()
    for component in changed_ids:
        if component in matrix["design_to_tasks"]:
            affected_tasks.update(matrix["design_to_tasks"][component])

    if affected_tasks:
        impact_lines.extend(f"- {task}" for task in sorted(affected_tasks))
        impact_lines.append("\n" + i18n.t("traceability.changes.design_impact.recommendations_title"))
        recommendations = i18n.t("traceability.changes.design_impact.recommendations")
        impact_lines.extend(recommendations)
    else:
        impact_lines.append(i18n.t("traceability.changes.design_impact.no_impact"))


def _add_tasks_impact(impact_lines: list[str], changed_ids: set[str], matrix: dict[str, Any], i18n: Any) -> None:
    """Add tasks change impact analysis."""
    impact_lines.append(i18n.t("traceability.changes.tasks_impact.title"))
    affected_tasks = set()
    for task_id in changed_ids:
        for other_task, deps in matrix["task_dependencies"].items():
            if task_id in deps:
                affected_tasks.add(other_task)

    if affected_tasks:
        dependent_task_suffix = i18n.t("traceability.changes.tasks_impact.dependent_task")
        impact_lines.extend(f"- {task}{dependent_task_suffix}" for task in sorted(affected_tasks))
        impact_lines.append("\n" + i18n.t("traceability.changes.tasks_impact.recommendations_title"))
        recommendations = i18n.t("traceability.changes.tasks_impact.recommendations")
        impact_lines.extend(recommendations)
    else:
        impact_lines.append(i18n.t("traceability.changes.tasks_impact.no_impact"))
