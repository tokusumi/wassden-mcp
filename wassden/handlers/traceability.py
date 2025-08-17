"""Traceability analysis and change impact assessment."""

import re
from typing import Any

from wassden.lib import fs_utils, traceability

# Constants
COMPLETE_COVERAGE_PERCENTAGE = 100


async def handle_get_traceability(args: dict[str, Any]) -> dict[str, Any]:
    """Generate traceability report."""
    requirements_path = args.get("requirementsPath", "specs/requirements.md")
    design_path = args.get("designPath", "specs/design.md")
    tasks_path = args.get("tasksPath", "specs/tasks.md")

    specs = await _read_spec_files(requirements_path, design_path, tasks_path)
    matrix = traceability.build_traceability_matrix(
        specs.get("requirements"),
        specs.get("design"),
        specs.get("tasks"),
    )

    report_lines = _build_traceability_report(matrix)

    return {
        "content": [
            {
                "type": "text",
                "text": "\n".join(report_lines),
            }
        ]
    }


async def _read_spec_files(requirements_path: str, design_path: str, tasks_path: str) -> dict[str, str | None]:
    """Read spec files if they exist."""
    specs: dict[str, str | None] = {}
    for name, path in [
        ("requirements", requirements_path),
        ("design", design_path),
        ("tasks", tasks_path),
    ]:
        try:
            specs[name] = await fs_utils.read_file(path)
        except FileNotFoundError:
            specs[name] = None
    return specs


def _build_traceability_report(matrix: dict[str, Any]) -> list[str]:
    """Build the complete traceability report."""
    report_lines = ["# トレーサビリティレポート\n"]

    _add_overview_section(report_lines, matrix)
    _add_mapping_sections(report_lines, matrix)
    _add_coverage_analysis(report_lines, matrix)
    _add_task_dependencies(report_lines, matrix)
    _add_summary_section(report_lines, matrix)

    return report_lines


def _add_overview_section(report_lines: list[str], matrix: dict[str, Any]) -> None:
    """Add overview section to the report."""
    report_lines.extend(
        [
            "## 概要",
            f"- 要件数: {len(matrix['requirements'])}",
            f"- 設計要素数: {len(matrix['design_components'])}",
            f"- タスク数: {len(matrix['tasks'])}\n",
        ]
    )


def _add_mapping_sections(report_lines: list[str], matrix: dict[str, Any]) -> None:
    """Add mapping sections to the report."""
    # Requirements to Design mapping
    if matrix["req_to_design"]:
        report_lines.append("## 要件 → 設計 マッピング")
        for req_id, design_refs in sorted(matrix["req_to_design"].items()):
            if design_refs:
                report_lines.append(f"- **{req_id}** → {', '.join(sorted(design_refs))}")
            else:
                report_lines.append(f"- **{req_id}** → ⚠️ 設計参照なし")
        report_lines.append("")

    # Design to Tasks mapping
    if matrix["design_to_tasks"]:
        report_lines.append("## 設計 → タスク マッピング")
        for component, task_refs in sorted(matrix["design_to_tasks"].items()):
            if task_refs:
                report_lines.append(f"- **{component}** → {', '.join(sorted(task_refs))}")
            else:
                report_lines.append(f"- **{component}** → ⚠️ タスク参照なし")
        report_lines.append("")


def _add_coverage_analysis(report_lines: list[str], matrix: dict[str, Any]) -> None:
    """Add coverage analysis section to the report."""
    report_lines.append("## カバレッジ分析")

    # Requirements coverage
    uncovered_reqs = matrix["requirements"] - set(matrix["req_to_design"].keys())
    if uncovered_reqs:
        report_lines.append("### ⚠️ 設計されていない要件")
        report_lines.extend(f"- {req}" for req in sorted(uncovered_reqs))
        report_lines.append("")

    # Design coverage
    uncovered_design = matrix["design_components"] - set(matrix["design_to_tasks"].keys())
    if uncovered_design:
        report_lines.append("### ⚠️ タスク化されていない設計要素")
        report_lines.extend(f"- {component}" for component in sorted(uncovered_design))
        report_lines.append("")


def _add_task_dependencies(report_lines: list[str], matrix: dict[str, Any]) -> None:
    """Add task dependencies section to the report."""
    if matrix["task_dependencies"]:
        report_lines.append("## タスク依存関係")
        for task_id, deps in sorted(matrix["task_dependencies"].items()):
            if deps:
                report_lines.append(f"- **{task_id}** ← {', '.join(sorted(deps))}")
        report_lines.append("")


def _add_summary_section(report_lines: list[str], matrix: dict[str, Any]) -> None:
    """Add summary section to the report."""
    req_coverage = len(matrix["req_to_design"]) / len(matrix["requirements"]) * 100 if matrix["requirements"] else 0
    design_coverage = (
        len(matrix["design_to_tasks"]) / len(matrix["design_components"]) * 100 if matrix["design_components"] else 0
    )

    report_lines.extend(
        ["## サマリー", f"- 要件カバレッジ: {req_coverage:.1f}%", f"- 設計カバレッジ: {design_coverage:.1f}%"]
    )

    if req_coverage == COMPLETE_COVERAGE_PERCENTAGE and design_coverage == COMPLETE_COVERAGE_PERCENTAGE:
        report_lines.append("\n✅ 完全なトレーサビリティが確保されています！")
    else:
        report_lines.append("\n⚠️ トレーサビリティに改善の余地があります。")


async def handle_analyze_changes(args: dict[str, Any]) -> dict[str, Any]:
    """Analyze impact of changes to spec documents."""
    changed_file = args["changedFile"]
    change_description = args["changeDescription"]

    spec_type = _determine_spec_type(changed_file)

    if spec_type is None:
        return _handle_non_spec_file_change(changed_file, change_description)

    return await _handle_spec_file_change(changed_file, change_description, spec_type)


def _determine_spec_type(changed_file: str) -> str | None:
    """Determine the type of spec file from the filename."""
    file_lower = changed_file.lower()
    if "requirements" in file_lower:
        return "requirements"
    if "design" in file_lower:
        return "design"
    if "tasks" in file_lower:
        return "tasks"
    return None


def _handle_non_spec_file_change(changed_file: str, change_description: str) -> dict[str, Any]:
    """Handle changes to non-spec files."""
    impact_lines = ["# 変更影響分析レポート\n"]
    impact_lines.append("## 変更内容")
    impact_lines.append(f"- ファイル: {changed_file}")
    impact_lines.append(f"- 変更: {change_description}\n")

    file_lower = changed_file.lower()
    if file_lower.endswith((".py", ".js", ".ts", ".java", ".cpp", ".c")):
        impact_lines.extend(
            ["## 実装ファイルの変更", "- コードベースへの直接的な変更", "- 関連する仕様書との整合性確認が必要"]
        )
    elif file_lower.endswith((".md", ".txt", ".doc")):
        impact_lines.extend(
            ["## ドキュメント変更", "- ドキュメントの更新", "- 他の関連ドキュメントとの整合性確認が必要"]
        )
    else:
        impact_lines.extend(["## ファイル変更", "- ファイルの変更が検出されました"])

    impact_lines.extend(
        [
            "\n## 推奨アクション",
            "1. 変更内容を関連する仕様書に反映",
            "2. 仕様書の検証ツールを実行",
            "3. `get_traceability` で全体の整合性を確認",
        ]
    )

    return {
        "content": [
            {
                "type": "text",
                "text": "\n".join(impact_lines),
            }
        ]
    }


async def _handle_spec_file_change(changed_file: str, change_description: str, spec_type: str) -> dict[str, Any]:
    """Handle changes to spec files."""
    specs = await _read_all_specs()
    matrix = traceability.build_traceability_matrix(
        specs.get("requirements"),
        specs.get("design"),
        specs.get("tasks"),
    )

    impact_lines = _build_change_header(changed_file, change_description)
    changed_ids = _extract_changed_ids(change_description)

    if spec_type == "requirements":
        _add_requirements_impact(impact_lines, changed_ids, matrix)
    elif spec_type == "design":
        _add_design_impact(impact_lines, changed_ids, matrix)
    elif spec_type == "tasks":
        _add_tasks_impact(impact_lines, changed_ids, matrix)

    impact_lines.extend(
        [
            "\n## 次のステップ",
            "1. 影響を受ける文書を更新",
            "2. 各文書の validate_* ツールで検証",
            "3. `get_traceability` で全体の整合性を確認",
        ]
    )

    return {
        "content": [
            {
                "type": "text",
                "text": "\n".join(impact_lines),
            }
        ]
    }


async def _read_all_specs() -> dict[str, str | None]:
    """Read all spec files."""
    specs: dict[str, str | None] = {}
    for name, path in [
        ("requirements", "specs/requirements.md"),
        ("design", "specs/design.md"),
        ("tasks", "specs/tasks.md"),
    ]:
        try:
            specs[name] = await fs_utils.read_file(path)
        except FileNotFoundError:
            specs[name] = None
    return specs


def _build_change_header(changed_file: str, change_description: str) -> list[str]:
    """Build the header section of the change impact report."""
    return ["# 変更影響分析レポート\n", "## 変更内容", f"- ファイル: {changed_file}", f"- 変更: {change_description}\n"]


def _extract_changed_ids(change_description: str) -> set[str]:
    """Extract changed IDs from the change description."""
    changed_ids = set()
    changed_ids.update(re.findall(r"\bREQ-\d{2}\b", change_description))
    changed_ids.update(re.findall(r"\bTASK-\d{2}(?:-\d{2}){0,2}\b", change_description))
    return changed_ids


def _add_requirements_impact(impact_lines: list[str], changed_ids: set[str], matrix: dict[str, Any]) -> None:
    """Add requirements change impact analysis."""
    impact_lines.append("## 影響を受ける設計要素")
    affected_design = set()
    for req_id in changed_ids:
        if req_id in matrix["req_to_design"]:
            affected_design.update(matrix["req_to_design"][req_id])

    if affected_design:
        impact_lines.extend(f"- {component}" for component in sorted(affected_design))
        impact_lines.extend(
            [
                "\n## 推奨アクション",
                "1. 上記の設計要素を確認し、必要に応じて更新",
                "2. `validate_design` を実行して整合性を確認",
                "3. 関連するタスクの見直し",
            ]
        )
    else:
        impact_lines.append("- なし（この要件はまだ設計に反映されていません）")


def _add_design_impact(impact_lines: list[str], changed_ids: set[str], matrix: dict[str, Any]) -> None:
    """Add design change impact analysis."""
    impact_lines.append("## 影響を受けるタスク")
    affected_tasks = set()
    for component in changed_ids:
        if component in matrix["design_to_tasks"]:
            affected_tasks.update(matrix["design_to_tasks"][component])

    if affected_tasks:
        impact_lines.extend(f"- {task}" for task in sorted(affected_tasks))
        impact_lines.extend(
            [
                "\n## 推奨アクション",
                "1. 上記のタスクの内容を確認し、必要に応じて更新",
                "2. `validate_tasks` を実行して整合性を確認",
                "3. タスクの工数見積もりの再評価",
            ]
        )
    else:
        impact_lines.append("- なし（この設計要素はまだタスク化されていません）")


def _add_tasks_impact(impact_lines: list[str], changed_ids: set[str], matrix: dict[str, Any]) -> None:
    """Add tasks change impact analysis."""
    impact_lines.append("## 依存関係の影響")
    affected_tasks = set()
    for task_id in changed_ids:
        for other_task, deps in matrix["task_dependencies"].items():
            if task_id in deps:
                affected_tasks.add(other_task)

    if affected_tasks:
        impact_lines.extend(f"- {task} (依存タスク)" for task in sorted(affected_tasks))
        impact_lines.extend(
            [
                "\n## 推奨アクション",
                "1. 依存タスクのスケジュール調整",
                "2. マイルストーンへの影響確認",
                "3. リスク評価の更新",
            ]
        )
    else:
        impact_lines.append("- なし（他のタスクへの依存影響はありません）")
