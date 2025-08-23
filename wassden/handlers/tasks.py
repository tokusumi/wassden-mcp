"""Tasks handling functions."""

from wassden.i18n import get_i18n
from wassden.lib import validate
from wassden.types import HandlerResponse, SpecDocuments, TextContent


async def handle_prompt_tasks(
    specs: SpecDocuments,
) -> HandlerResponse:
    """Generate prompt for creating tasks.md from design."""
    i18n = get_i18n(specs.language)

    design = await specs.get_design()
    requirements = await specs.get_requirements()

    if design is None:
        return HandlerResponse(
            content=[TextContent(text=i18n.t("tasks_prompts.error.design_not_found", path=specs.design_path))]
        )

    if requirements is None:
        return HandlerResponse(
            content=[
                TextContent(text=i18n.t("tasks_prompts.error.requirements_not_found", path=specs.requirements_path))
            ]
        )

    prompt = f"""{i18n.t("tasks_prompts.prompt.intro")}

{i18n.t("tasks_prompts.prompt.design_content")}
```markdown
{design}
```

{i18n.t("tasks_prompts.prompt.requirements_content")}
```markdown
{requirements}
```

{i18n.t("tasks_prompts.prompt.file_to_create", tasks_path=specs.tasks_path)}

{i18n.t("tasks_prompts.prompt.required_structure")}

{i18n.t("tasks_prompts.prompt.sections.overview")}

{i18n.t("tasks_prompts.prompt.sections.task_list")}

{i18n.t("tasks_prompts.prompt.sections.dependencies")}

{i18n.t("tasks_prompts.prompt.sections.milestones")}

{i18n.t("tasks_prompts.prompt.sections.risks")}

{i18n.t("tasks_prompts.prompt.instructions")}"""

    return HandlerResponse(content=[TextContent(text=prompt)])


async def handle_validate_tasks(
    specs: SpecDocuments,
) -> HandlerResponse:
    """Validate tasks.md structure and dependencies."""
    try:
        tasks_content = await specs.get_tasks()
        if tasks_content is None:
            raise FileNotFoundError(f"Tasks file not found: {specs.tasks_path}")

        i18n = get_i18n(specs.language)

        # Try to read requirements and design for traceability check
        requirements_content = await specs.get_requirements()
        design_content = await specs.get_design()

        validation_result = validate.validate_tasks(tasks_content, requirements_content, design_content)

        if validation_result["isValid"]:
            stats = validation_result.get("stats", {})

            success_text = i18n.t("validation.tasks.success.title") + "\n\n"
            success_text += (
                i18n.t(
                    "validation.tasks.success.stats",
                    totalTasks=stats.get("totalTasks", 0),
                    totalEstimatedHours=stats.get("totalEstimatedHours", 0),
                    totalDependencies=stats.get("dependencies", 0),
                )
                + "\n\n"
            )
            success_text += i18n.t("validation.tasks.success.next_step")

            return HandlerResponse(content=[TextContent(text=success_text)])

        fix_instructions = "\n".join(f"- {issue}" for issue in validation_result["issues"])
        numbered_issues = "\n".join(f"{i + 1}. {issue}" for i, issue in enumerate(validation_result["issues"]))

        error_text = i18n.t("validation.tasks.error.title") + "\n\n"
        error_text += i18n.t("validation.tasks.error.detected_issues") + "\n"
        error_text += fix_instructions + "\n\n"
        error_text += i18n.t("validation.tasks.error.fix_instructions") + "\n\n"
        error_text += numbered_issues + "\n\n"
        error_text += i18n.t("validation.tasks.error.verify_after_fix")

        return HandlerResponse(content=[TextContent(text=error_text)])
    except FileNotFoundError:
        i18n = get_i18n(specs.language)
        return HandlerResponse(
            content=[TextContent(text=i18n.t("validation.tasks.file_error.not_found", path=specs.tasks_path))]
        )
    except Exception as e:
        i18n = get_i18n(specs.language)
        return HandlerResponse(
            content=[TextContent(text=i18n.t("validation.tasks.file_error.general_error", error=str(e)))]
        )
