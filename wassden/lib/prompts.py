"""Prompt generation utilities."""

from wassden.i18n import get_i18n
from wassden.types import Language


def generate_requirements_prompt(
    project_description: str,
    scope: str | None = None,
    constraints: str | None = None,
    language: Language = Language.JAPANESE,
) -> str:
    """Generate a prompt for creating requirements.md."""
    i18n = get_i18n(language)

    scope_text = scope or i18n.t("prompts.requirements.scope_default")
    constraints_text = constraints or i18n.t("prompts.requirements.constraints_default")

    return f"""{i18n.t("prompts.requirements.instruction")}

{i18n.t("prompts.requirements.project_info")}
{i18n.t("prompts.requirements.overview", project_description=project_description)}
{i18n.t("prompts.requirements.scope", scope=scope_text)}
{i18n.t("prompts.requirements.constraints", constraints=constraints_text)}

{i18n.t("prompts.requirements.file_section")}
{i18n.t("prompts.requirements.filename")}

{i18n.t("prompts.requirements.structure_section")}
{i18n.t("prompts.requirements.structure_template")}

{i18n.t("prompts.requirements.instruction_conclusion")}"""


def generate_design_prompt(requirements: str, language: Language = Language.JAPANESE) -> str:
    """Generate a prompt for creating design.md."""
    i18n = get_i18n(language)

    return f"""{i18n.t("prompts.design.instruction")}

{i18n.t("prompts.design.requirements_section")}
```markdown
{requirements}
```

{i18n.t("prompts.design.file_section")}
{i18n.t("prompts.design.filename")}

{i18n.t("prompts.design.structure_section")}
{i18n.t("prompts.design.structure_template")}

{i18n.t("prompts.design.instruction_conclusion")}"""


def generate_tasks_prompt(design: str, requirements: str, language: Language = Language.JAPANESE) -> str:
    """Generate a prompt for creating tasks.md."""
    i18n = get_i18n(language)

    return f"""{i18n.t("prompts.tasks.instruction")}

{i18n.t("prompts.tasks.design_section")}
```markdown
{design}
```

{i18n.t("prompts.tasks.requirements_section")}
```markdown
{requirements}
```

{i18n.t("prompts.tasks.file_section")}
{i18n.t("prompts.tasks.filename")}

{i18n.t("prompts.tasks.structure_section")}
{i18n.t("prompts.tasks.structure_template")}

{i18n.t("prompts.tasks.instruction_conclusion")}"""


def generate_validation_fix_prompt(spec_type: str, issues: list[str], language: Language = Language.JAPANESE) -> str:
    """Generate a prompt for fixing validation issues."""
    i18n = get_i18n(language)

    issue_list = "\n".join(f"- {issue}" for issue in issues)

    return f"""{i18n.t("prompts.validation_fix.header", spec_type=spec_type)}

{i18n.t("prompts.validation_fix.issues_section")}
{issue_list}

{i18n.t("prompts.validation_fix.fix_section")}
{i18n.t("prompts.validation_fix.fix_instruction", spec_type=spec_type)}

{chr(10).join(f"{i + 1}. {issue}" for i, issue in enumerate(issues))}

{i18n.t("prompts.validation_fix.confirmation_section")}
{i18n.t("prompts.validation_fix.confirmation_instruction", spec_type=spec_type)}"""


def generate_implementation_prompt(
    requirements: str, design: str, tasks: str, language: Language = Language.JAPANESE
) -> str:
    """Generate a prompt for implementation phase."""
    i18n = get_i18n(language)

    return f"""{i18n.t("prompts.implementation.instruction")}

{i18n.t("prompts.implementation.specs_section")}

{i18n.t("prompts.implementation.requirements_subsection")}
```markdown
{requirements}
```

{i18n.t("prompts.implementation.design_subsection")}
```markdown
{design}
```

{i18n.t("prompts.implementation.tasks_subsection")}
```markdown
{tasks}
```

{i18n.t("prompts.implementation.guidelines_section")}
{i18n.t("prompts.implementation.guidelines_template")}

{i18n.t("prompts.implementation.start_section")}
{i18n.t("prompts.implementation.start_instruction")}
{i18n.t("prompts.implementation.ready_declaration")}"""


def generate_completeness_questions(missing_info: list[str], language: Language = Language.JAPANESE) -> str:
    """Generate questions for missing information."""
    if not missing_info:
        return ""

    i18n = get_i18n(language)

    questions = f"\n{i18n.t('prompts.completeness.unclear_points')}\n"
    questions += "\n".join(f"{i + 1}. {q}" for i, q in enumerate(missing_info))
    return questions


def format_traceability_report(matrix: dict, language: Language = Language.JAPANESE) -> str:
    """Format a traceability matrix into a readable report."""
    i18n = get_i18n(language)

    lines = [i18n.t("prompts.traceability_report.title") + "\n"]

    # Summary statistics
    lines.append(i18n.t("prompts.traceability_report.overview_section"))
    lines.append(i18n.t("prompts.traceability_report.requirements_count", count=len(matrix.get("requirements", []))))
    lines.append(
        i18n.t("prompts.traceability_report.design_elements_count", count=len(matrix.get("design_components", [])))
    )
    lines.append(i18n.t("prompts.traceability_report.tasks_count", count=len(matrix.get("tasks", []))) + "\n")

    # Requirements to Design mapping
    if matrix.get("req_to_design"):
        lines.append(i18n.t("prompts.traceability_report.req_to_design_section"))
        for req_id, design_refs in sorted(matrix["req_to_design"].items()):
            if design_refs:
                lines.append(f"- **{req_id}** → {', '.join(sorted(design_refs))}")
            else:
                lines.append(f"- **{req_id}** → {i18n.t('prompts.traceability_report.no_design_reference')}")
        lines.append("")

    return "\n".join(lines)
