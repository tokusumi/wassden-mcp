"""Design handling functions."""

from wassden.i18n import get_i18n
from wassden.lib import validate
from wassden.types import HandlerResponse, SpecDocuments, TextContent


async def handle_prompt_design(
    specs: SpecDocuments,
) -> HandlerResponse:
    """Generate prompt for creating design.md from requirements."""
    requirements = await specs.get_requirements()
    i18n = get_i18n(specs.language)

    if requirements is None:
        return HandlerResponse(
            content=[
                TextContent(text=i18n.t("design_prompts.error.requirements_not_found", path=specs.requirements_path))
            ]
        )

    prompt = f"""{i18n.t("design_prompts.prompt.intro")}

{i18n.t("design_prompts.prompt.requirements_content")}
```markdown
{requirements}
```

{i18n.t("design_prompts.prompt.file_to_create", design_path=specs.design_path)}

{i18n.t("design_prompts.prompt.required_structure")}

{i18n.t("design_prompts.prompt.sections.architecture")}

{i18n.t("design_prompts.prompt.sections.components")}

{i18n.t("design_prompts.prompt.sections.data")}

{i18n.t("design_prompts.prompt.sections.api")}

{i18n.t("design_prompts.prompt.sections.non_functional")}

{i18n.t("design_prompts.prompt.sections.testing")}

{i18n.t("design_prompts.prompt.sections.traceability")}

{i18n.t("design_prompts.prompt.sections.flow")}

{i18n.t("design_prompts.prompt.sections.edge_cases")}

{i18n.t("design_prompts.prompt.sections.security")}

{i18n.t("design_prompts.prompt.sections.risks")}

{i18n.t("design_prompts.prompt.instructions")}"""

    return HandlerResponse(content=[TextContent(text=prompt)])


async def handle_validate_design(
    specs: SpecDocuments,
) -> HandlerResponse:
    """Validate design.md structure and traceability."""
    try:
        design_content = await specs.get_design()
        if design_content is None:
            raise FileNotFoundError(f"Design file not found: {specs.design_path}")

        i18n = get_i18n(specs.language)

        # Try to read requirements for traceability check
        requirements_content = await specs.get_requirements()

        validation_result = validate.validate_design(design_content, requirements_content)

        if validation_result["isValid"]:
            stats = validation_result.get("stats", {})

            success_text = i18n.t("validation.design.success.title") + "\n\n"
            success_text += (
                i18n.t(
                    "validation.design.success.stats",
                    totalDesignElements=0,  # Not implemented in validation yet
                    totalComponents=0,  # Not implemented in validation yet
                    reqCoverage=stats.get("referencedRequirements", 0),
                )
                + "\n\n"
            )
            success_text += i18n.t("validation.design.success.next_step")

            return HandlerResponse(content=[TextContent(text=success_text)])

        fix_instructions = "\n".join(f"- {issue}" for issue in validation_result["issues"])
        numbered_issues = "\n".join(f"{i + 1}. {issue}" for i, issue in enumerate(validation_result["issues"]))

        error_text = i18n.t("validation.design.error.title") + "\n\n"
        error_text += i18n.t("validation.design.error.detected_issues") + "\n"
        error_text += fix_instructions + "\n\n"
        error_text += i18n.t("validation.design.error.fix_instructions") + "\n\n"
        error_text += numbered_issues + "\n\n"
        error_text += i18n.t("validation.design.error.verify_after_fix")

        return HandlerResponse(content=[TextContent(text=error_text)])
    except FileNotFoundError:
        i18n = get_i18n(specs.language)
        return HandlerResponse(
            content=[TextContent(text=i18n.t("validation.design.file_error.not_found", path=specs.design_path))]
        )
    except Exception as e:
        i18n = get_i18n(specs.language)
        return HandlerResponse(
            content=[TextContent(text=i18n.t("validation.design.file_error.general_error", error=str(e)))]
        )
