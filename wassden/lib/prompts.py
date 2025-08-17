"""Prompt generation utilities."""


def generate_requirements_prompt(
    project_description: str,
    scope: str | None = None,
    constraints: str | None = None,
) -> str:
    """Generate a prompt for creating requirements.md."""
    return f"""以下の指示に従って、EARS形式のrequirements.mdファイルを作成してください：

## プロジェクト情報
- 概要: {project_description}
- スコープ: {scope or "スコープ情報を分析して記載"}
- 制約: {constraints or "技術的・ビジネス制約を分析して記載"}

## 作成するファイル
ファイル名: specs/requirements.md

## 必須構造
[要件定義の構造テンプレート...]

このプロンプトに従って、高品質なrequirements.mdを作成してください。"""


def generate_design_prompt(requirements: str) -> str:
    """Generate a prompt for creating design.md."""
    return f"""以下のrequirements.mdに基づいて、design.mdファイルを作成してください：

## Requirements内容
```markdown
{requirements}
```

## 作成するファイル
ファイル名: specs/design.md

## 必須構造
[設計書の構造テンプレート...]

このプロンプトに従って、トレーサビリティが確保された高品質なdesign.mdを作成してください。"""


def generate_tasks_prompt(design: str, requirements: str) -> str:
    """Generate a prompt for creating tasks.md."""
    return f"""以下のdesign.mdとrequirements.mdに基づいて、WBS形式のtasks.mdファイルを作成してください：

## Design内容
```markdown
{design}
```

## Requirements内容
```markdown
{requirements}
```

## 作成するファイル
ファイル名: specs/tasks.md

## 必須構造
[タスクリストの構造テンプレート...]

このプロンプトに従って、実行可能で管理しやすいtasks.mdを作成してください。"""


def generate_validation_fix_prompt(spec_type: str, issues: list[str]) -> str:
    """Generate a prompt for fixing validation issues."""
    issue_list = "\n".join(f"- {issue}" for issue in issues)

    return f"""⚠️ {spec_type}.md に修正が必要です：

## 検出された問題
{issue_list}

## 修正手順
以下の指示に従って {spec_type}.md を修正してください：

{chr(10).join(f"{i + 1}. {issue}" for i, issue in enumerate(issues))}

## 修正後の確認
修正が完了したら、再度 validate_{spec_type} を実行して検証してください。"""


def generate_implementation_prompt(requirements: str, design: str, tasks: str) -> str:
    """Generate a prompt for implementation phase."""
    return f"""以下の仕様書に基づいて、段階的に実装を進めてください：

## 実装の基礎となる仕様書

### Requirements (要件定義)
```markdown
{requirements}
```

### Design (設計書)
```markdown
{design}
```

### Tasks (実装タスク)
```markdown
{tasks}
```

## 実装ガイドライン
[実装のガイドライン...]

## 開始指示
最初のタスク（TASK-01-01）から実装を開始してください。
準備ができたら、"実装を開始します" と宣言してから作業を始めてください。"""


def generate_completeness_questions(missing_info: list[str]) -> str:
    """Generate questions for missing information."""
    if not missing_info:
        return ""

    questions = "\n特に以下の点が不明です：\n"
    questions += "\n".join(f"{i + 1}. {q}" for i, q in enumerate(missing_info))
    return questions


def format_traceability_report(matrix: dict) -> str:
    """Format a traceability matrix into a readable report."""
    lines = ["# トレーサビリティレポート\n"]

    # Summary statistics
    lines.append("## 概要")
    lines.append(f"- 要件数: {len(matrix.get('requirements', []))}")
    lines.append(f"- 設計要素数: {len(matrix.get('design_components', []))}")
    lines.append(f"- タスク数: {len(matrix.get('tasks', []))}\n")

    # Requirements to Design mapping
    if matrix.get("req_to_design"):
        lines.append("## 要件 → 設計 マッピング")
        for req_id, design_refs in sorted(matrix["req_to_design"].items()):
            if design_refs:
                lines.append(f"- **{req_id}** → {', '.join(sorted(design_refs))}")
            else:
                lines.append(f"- **{req_id}** → ⚠️ 設計参照なし")
        lines.append("")

    return "\n".join(lines)
