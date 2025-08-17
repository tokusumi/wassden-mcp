"""Tasks handling functions."""

import contextlib
from typing import Any

from wassden.lib import fs_utils, validate


async def handle_prompt_tasks(args: dict[str, Any]) -> dict[str, Any]:
    """Generate prompt for creating tasks.md from design."""
    design_path = args.get("designPath", "specs/design.md")
    requirements_path = args.get("requirementsPath", "specs/requirements.md")

    try:
        design = await fs_utils.read_file(design_path)
        requirements = await fs_utils.read_file(requirements_path)
    except FileNotFoundError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ エラー: {e!s}\n\n必要なファイルが見つかりません。",
                }
            ]
        }

    prompt = f"""以下のdesign.mdとrequirements.mdに基づいて、WBS形式のtasks.mdファイルを作成してください：

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
以下の章立てに従って作成してください：

### 1. 概要
プロジェクトのタスク分解構造（WBS）の概要

### 2. タスク一覧
#### Phase 1: 基盤構築
- **TASK-01-01**: [タスク名] (工数: Xh)
  - 詳細: [具体的な作業内容]
  - 関連: [REQ-XX], [component-name]
  - 依存: なし

- **TASK-01-02**: [タスク名] (工数: Xh)
  - 詳細: [具体的な作業内容]
  - 関連: [REQ-YY], [component-name]
  - 依存: TASK-01-01

#### Phase 2: 機能実装
- **TASK-02-01**: [タスク名] (工数: Xh)
  - 詳細: [具体的な作業内容]
  - 関連: [REQ-ZZ], [component-name]
  - 依存: TASK-01-XX

#### Phase 3: テスト・品質保証
- **TASK-03-01**: [タスク名] (工数: Xh)
  - 詳細: [具体的な作業内容]
  - 関連: [全REQ]
  - 依存: TASK-02-XX

### 3. 依存関係
```
TASK-01-01 → TASK-01-02 → TASK-02-01
                       ↘
                         TASK-03-01
```

### 4. マイルストーン
- **M1**: Phase 1完了 (TASK-01-XX完了時点)
- **M2**: Phase 2完了 (TASK-02-XX完了時点)
- **M3**: リリース準備完了 (TASK-03-XX完了時点)

### 5. リスクと対策
- **リスク**: [リスク内容]
  - 影響タスク: TASK-XX-XX
  - 対策: [対策内容]

## 作成指示
1. TASK-IDは階層構造（TASK-フェーズ-連番）で作成
2. 各タスクで関連するREQ-IDとコンポーネントを明記
3. 依存関係を明確にし、循環依存を避ける
4. 工数見積もりを現実的に設定
5. 文字数: 2000-4000文字程度

このプロンプトに従って、実行可能で管理しやすいtasks.mdを作成してください。"""

    return {
        "content": [
            {
                "type": "text",
                "text": prompt,
            }
        ]
    }


async def handle_validate_tasks(args: dict[str, Any]) -> dict[str, Any]:
    """Validate tasks.md structure and dependencies."""
    tasks_path = args.get("tasksPath", "specs/tasks.md")
    requirements_path = args.get("requirementsPath", "specs/requirements.md")
    design_path = args.get("designPath", "specs/design.md")

    try:
        tasks_content = await fs_utils.read_file(tasks_path)

        # Try to read requirements and design for traceability check
        requirements_content = None
        design_content = None

        with contextlib.suppress(FileNotFoundError):
            requirements_content = await fs_utils.read_file(requirements_path)

        with contextlib.suppress(FileNotFoundError):
            design_content = await fs_utils.read_file(design_path)

        validation_result = validate.validate_tasks(tasks_content, requirements_content, design_content)

        if validation_result["isValid"]:
            stats = validation_result.get("stats", {})
            missing_req_refs = stats.get("missingRequirementReferences", [])
            missing_design_refs = stats.get("missingDesignReferences", [])

            traceability_info = ""
            if missing_req_refs:
                traceability_info += f"\n- 未参照要件: {len(missing_req_refs)}件"
            if missing_design_refs:
                traceability_info += f"\n- 未参照設計要素: {len(missing_design_refs)}件"

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"""✅ tasks.md の検証に成功しました！

## 検証結果
- タスク数: {stats.get("totalTasks", 0)}
- 依存関係数: {stats.get("dependencies", 0)}{traceability_info}

タスクドキュメントは正しい形式で記載されています。実装フェーズに進むことができます。""",
                    }
                ]
            }
        fix_instructions = chr(10).join(f"- {issue}" for issue in validation_result["issues"])

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"""⚠️ tasks.md に修正が必要です：

## 検出された問題
{fix_instructions}

## 修正手順
以下の指示に従って tasks.md を修正してください：

{chr(10).join(f"{i + 1}. {issue}" for i, issue in enumerate(validation_result["issues"]))}

## 修正後の確認
修正が完了したら、再度 validate_tasks を実行して検証してください。""",
                }
            ]
        }
    except FileNotFoundError:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"""❌ エラー: {tasks_path} が見つかりません。

まず prompt_tasks を使用して tasks.md を作成してください。""",
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ エラーが発生しました: {e!s}",
                }
            ]
        }
