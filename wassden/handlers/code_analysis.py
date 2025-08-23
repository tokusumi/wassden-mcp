"""Code analysis and implementation prompt generation."""

import re
from typing import Any

from wassden.i18n import get_i18n
from wassden.types import HandlerResponse, SpecDocuments, TextContent


async def handle_prompt_code(
    specs: SpecDocuments,
) -> HandlerResponse:
    """Generate implementation prompt from tasks, design, and requirements."""
    i18n = get_i18n(specs.language)

    tasks = await specs.get_tasks()
    design = await specs.get_design()
    requirements = await specs.get_requirements()

    if tasks is None:
        return HandlerResponse(
            content=[
                TextContent(text=i18n.t("code_prompts.implementation.error.tasks_not_found", path=specs.tasks_path))
            ]
        )

    if design is None:
        return HandlerResponse(
            content=[
                TextContent(text=i18n.t("code_prompts.implementation.error.design_not_found", path=specs.design_path))
            ]
        )

    if requirements is None:
        return HandlerResponse(
            content=[
                TextContent(
                    text=i18n.t(
                        "code_prompts.implementation.error.requirements_not_found", path=specs.requirements_path
                    )
                )
            ]
        )

    prompt = f"""{i18n.t("code_prompts.implementation.prompt.intro")}

{i18n.t("code_prompts.implementation.prompt.requirements_header")}
```markdown
{requirements}
```

{i18n.t("code_prompts.implementation.prompt.design_header")}
```markdown
{design}
```

{i18n.t("code_prompts.implementation.prompt.tasks_header")}
```markdown
{tasks}
```

{i18n.t("code_prompts.implementation.prompt.guidelines_header")}

{i18n.t("code_prompts.implementation.prompt.implementation_order")}

{i18n.t("code_prompts.implementation.prompt.quality_standards")}

{i18n.t("code_prompts.implementation.prompt.traceability")}

{i18n.t("code_prompts.implementation.prompt.quality_review")}

{i18n.t("code_prompts.implementation.prompt.verification")}

{i18n.t("code_prompts.implementation.prompt.progress_report")}

{i18n.t("code_prompts.implementation.prompt.start_instructions")}"""

    return HandlerResponse(content=[TextContent(text=prompt)])


async def handle_generate_review_prompt(
    task_id: str,
    specs: SpecDocuments,
) -> HandlerResponse:
    """Generate implementation review prompt for specific TASK-ID."""
    i18n = get_i18n(specs.language)

    if not task_id:
        return HandlerResponse(content=[TextContent(text=i18n.t("code_prompts.review.error.task_id_required"))])

    tasks = await specs.get_tasks()
    design = await specs.get_design()
    requirements = await specs.get_requirements()

    if tasks is None:
        return HandlerResponse(
            content=[TextContent(text=i18n.t("code_prompts.review.error.tasks_not_found", path=specs.tasks_path))]
        )

    if design is None:
        return HandlerResponse(
            content=[TextContent(text=i18n.t("code_prompts.review.error.design_not_found", path=specs.design_path))]
        )

    if requirements is None:
        return HandlerResponse(
            content=[
                TextContent(
                    text=i18n.t("code_prompts.review.error.requirements_not_found", path=specs.requirements_path)
                )
            ]
        )

    # Extract task info
    task_info = _extract_task_info(tasks, task_id)
    if not task_info:
        return HandlerResponse(
            content=[TextContent(text=i18n.t("code_prompts.review.error.task_not_found", task_id=task_id))]
        )

    # Extract related requirements and test requirements
    related_reqs = _extract_related_requirements(task_info, requirements)
    related_trs = _extract_related_test_requirements(task_info, requirements)

    # Generate review prompt
    task_summary = task_info.get("summary", "N/A")
    task_phase = task_info.get("phase", "N/A")

    prompt = f"""# {i18n.t("code_prompts.review.prompt.title", task_id=task_id)}

{i18n.t("code_prompts.review.prompt.target_task", task_id=task_id, task_summary=task_summary, task_phase=task_phase)}

{i18n.t("code_prompts.review.prompt.related_requirements")}

{i18n.t("code_prompts.review.prompt.functional_requirements")}
{_format_requirements_list(related_reqs, i18n)}

{i18n.t("code_prompts.review.prompt.test_requirements")}
{_format_requirements_list(related_trs, i18n)}

{i18n.t("code_prompts.review.prompt.quality_guardrails")}

{i18n.t("code_prompts.review.prompt.test_tampering")}

{i18n.t("code_prompts.review.prompt.incomplete_implementation")}

{i18n.t("code_prompts.review.prompt.static_quality")}

{i18n.t("code_prompts.review.prompt.project_quality_standards")}

{i18n.t("code_prompts.review.prompt.required_checks")}

{i18n.t("code_prompts.review.prompt.execution_examples")}

{i18n.t("code_prompts.review.prompt.pass_criteria")}

{i18n.t("code_prompts.review.prompt.design_compliance")}

{i18n.t("code_prompts.review.prompt.expected_file_structure")}
{_extract_file_structure_from_design(design, i18n)}

{i18n.t("code_prompts.review.prompt.expected_interfaces")}
{_extract_interfaces_from_design(design, i18n)}

{i18n.t("code_prompts.review.prompt.pass_criteria_all")}

{i18n.t("code_prompts.review.prompt.review_instructions", task_id=task_id)}

{i18n.t("code_prompts.review.prompt.next_steps", task_id=task_id)}
"""

    return HandlerResponse(content=[TextContent(text=prompt)])


def _extract_task_info(tasks_content: str, task_id: str) -> dict[str, str] | None:
    """Extract task information for specified task ID from tasks.md."""
    lines = tasks_content.split("\n")
    task_info = {}
    current_phase = ""

    for line in lines:
        # Extract phase
        if line.startswith("## Phase"):
            current_phase = line.strip()
            continue

        # Find task line
        if task_id in line and "TASK-" in line:
            task_info["phase"] = current_phase
            # Extract task summary (everything after task ID)
            parts = line.split(task_id)
            if len(parts) > 1:
                summary = parts[1].strip().lstrip(":")
                task_info["summary"] = summary
            return task_info

    return None


def _extract_related_requirements(task_info: dict[str, str], requirements_content: str) -> list[str]:
    """Extract REQ-IDs mentioned in task info."""
    task_text = f"{task_info.get('summary', '')} {task_info.get('phase', '')}"
    req_ids = []

    # Simple regex to find REQ-XX patterns

    matches = re.findall(r"REQ-\d+", task_text)
    req_ids.extend(matches)

    # Extract requirement details
    requirements = []
    for req_id in req_ids:
        req_detail = _find_requirement_detail(requirements_content, req_id)
        if req_detail:
            requirements.append(f"**{req_id}**: {req_detail}")

    return requirements


def _extract_related_test_requirements(task_info: dict[str, str], requirements_content: str) -> list[str]:
    """Extract TR-IDs mentioned in task info."""
    task_text = f"{task_info.get('summary', '')} {task_info.get('phase', '')}"
    tr_ids = []

    # Simple regex to find TR-XX patterns

    matches = re.findall(r"TR-\d+", task_text)
    tr_ids.extend(matches)

    # Extract test requirement details
    test_requirements = []
    for tr_id in tr_ids:
        tr_detail = _find_requirement_detail(requirements_content, tr_id)
        if tr_detail:
            test_requirements.append(f"**{tr_id}**: {tr_detail}")

    return test_requirements


def _find_requirement_detail(requirements_content: str, req_id: str) -> str | None:
    """Find requirement detail by ID."""
    lines = requirements_content.split("\n")
    # Use both Japanese and English patterns to find requirements
    requirement_patterns = ["システムは", "テスト", "system", "test", "shall", "should", "must"]
    for line in lines:
        if req_id in line and any(pattern in line.lower() for pattern in requirement_patterns):
            # Extract requirement text
            return line.strip()
    return None


def _format_requirements_list(requirements: list[str], i18n: Any) -> str:
    """Format requirements list for display."""
    if not requirements:
        return str(i18n.t("code_prompts.helpers.no_requirements"))

    return "\n".join(f"- {req}" for req in requirements)


def _extract_file_structure_from_design(design_content: str, i18n: Any) -> str:
    """Extract expected file structure from design.md."""
    # Simple extraction - look for file/module sections
    lines = design_content.split("\n")

    file_keywords = i18n.t("code_prompts.helpers.search_keywords.file_structure")
    structure_lines = [line.strip() for line in lines if any(keyword in line.lower() for keyword in file_keywords)]

    return (
        "\n".join(structure_lines) if structure_lines else str(i18n.t("code_prompts.helpers.file_structure_not_found"))
    )


def _extract_interfaces_from_design(design_content: str, i18n: Any) -> str:
    """Extract expected interfaces from design.md."""
    # Simple extraction - look for interface/API sections
    lines = design_content.split("\n")

    interface_keywords = i18n.t("code_prompts.helpers.search_keywords.interfaces")
    interface_lines = [line.strip() for line in lines if any(keyword in line.lower() for keyword in interface_keywords)]

    return "\n".join(interface_lines) if interface_lines else str(i18n.t("code_prompts.helpers.interfaces_not_found"))
