"""Requirements handling functions."""

from pathlib import Path

from wassden.i18n import get_i18n
from wassden.lib import fs_utils, validate
from wassden.types import HandlerResponse, Language, TextContent


async def handle_prompt_requirements(
    project_description: str,
    scope: str = "",
    constraints: str = "",
    language: Language = Language.JAPANESE,
) -> HandlerResponse:
    """Generate prompt for creating requirements.md."""
    i18n = get_i18n(language)

    # Use defaults if not provided
    if not scope:
        scope = i18n.t("requirements.prompts.default_scope")
    if not constraints:
        constraints = i18n.t("requirements.prompts.default_constraints")

    prompt = i18n.t(
        "requirements.prompts.main", project_description=project_description, scope=scope, constraints=constraints
    )

    return HandlerResponse(content=[TextContent(text=prompt)])


async def handle_validate_requirements(
    requirements_path: Path = Path("specs/requirements.md"),
    language: Language = Language.JAPANESE,
) -> HandlerResponse:
    """Validate requirements.md and generate fix instructions if needed."""
    try:
        content = await fs_utils.read_file(requirements_path)
        i18n = get_i18n(language)
        validation_result = validate.validate_requirements(content, language)

        if validation_result["isValid"]:
            stats = validation_result["stats"]
            found_sections = validation_result["foundSections"]

            success_text = i18n.t("validation.requirements.success.title") + "\n\n"
            success_text += (
                i18n.t(
                    "validation.requirements.success.stats",
                    totalRequirements=stats["totalRequirements"],
                    totalNFRs=stats["totalNFRs"],
                    totalKPIs=stats["totalKPIs"],
                )
                + "\n\n"
            )
            success_text += i18n.t("validation.requirements.success.structure") + "\n"
            success_text += "\n".join(f"✅ {section}" for section in found_sections) + "\n\n"
            success_text += i18n.t("validation.requirements.success.next_step")

            return HandlerResponse(content=[TextContent(text=success_text)])

        fix_instructions = "\n".join(f"- {issue}" for issue in validation_result["issues"])
        numbered_issues = "\n".join(f"{i + 1}. {issue}" for i, issue in enumerate(validation_result["issues"]))

        error_text = i18n.t("validation.requirements.error.title") + "\n\n"
        error_text += i18n.t("validation.requirements.error.detected_issues") + "\n"
        error_text += fix_instructions + "\n\n"
        error_text += i18n.t("validation.requirements.error.fix_instructions") + "\n\n"
        error_text += numbered_issues + "\n\n"
        error_text += i18n.t("validation.requirements.error.verify_after_fix")

        return HandlerResponse(content=[TextContent(text=error_text)])
    except FileNotFoundError:
        i18n = get_i18n(language)
        return HandlerResponse(
            content=[TextContent(text=i18n.t("validation.requirements.file_error.not_found", path=requirements_path))]
        )
    except Exception as e:
        i18n = get_i18n(language)
        return HandlerResponse(
            content=[TextContent(text=i18n.t("validation.requirements.file_error.general_error", error=str(e)))]
        )
