"""Completeness checking handler."""

from wassden.i18n import get_i18n
from wassden.types import HandlerResponse, Language, TextContent


async def handle_check_completeness(
    user_input: str,
    language: Language = Language.JAPANESE,
) -> HandlerResponse:
    """Check user input completeness and generate questions or requirements prompt."""
    i18n = get_i18n(language)

    # Analyze input for missing information
    missing_info: list[str] = []

    # Check for technology stack
    if not any(keyword in user_input for keyword in i18n.t("completeness.keywords.technology")):
        missing_info.append(i18n.t("completeness.questions.technology"))

    # Check for target users
    if not any(keyword in user_input for keyword in i18n.t("completeness.keywords.users")):
        missing_info.append(i18n.t("completeness.questions.users"))

    # Check for constraints
    if not any(keyword in user_input for keyword in i18n.t("completeness.keywords.constraints")):
        missing_info.append(i18n.t("completeness.questions.constraints"))

    # Check for scope
    if not any(keyword in user_input for keyword in i18n.t("completeness.keywords.scope")):
        missing_info.append(i18n.t("completeness.questions.scope"))

    # Build the response prompt
    base_prompt = i18n.t("completeness.prompts.base", user_input=user_input)

    if missing_info:
        base_prompt += f"\n\n{i18n.t('completeness.prompts.missing_info')}\n"
        base_prompt += "\n".join(f"{i + 1}. {q}" for i, q in enumerate(missing_info))

    base_prompt += f"\n\n{i18n.t('completeness.prompts.sufficient_info')}\n\n---\n\n"
    base_prompt += i18n.t("completeness.prompts.file_instructions")

    return HandlerResponse(content=[TextContent(text=base_prompt)])
