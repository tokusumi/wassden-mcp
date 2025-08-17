"""Code analysis and implementation prompt generation."""

from typing import Any

from wassden.lib import fs_utils


async def handle_prompt_code(args: dict[str, Any]) -> dict[str, Any]:
    """Generate implementation prompt from tasks, design, and requirements."""
    tasks_path = args.get("tasksPath", "specs/tasks.md")
    design_path = args.get("designPath", "specs/design.md")
    requirements_path = args.get("requirementsPath", "specs/requirements.md")

    # Read all spec files
    try:
        tasks = await fs_utils.read_file(tasks_path)
        design = await fs_utils.read_file(design_path)
        requirements = await fs_utils.read_file(requirements_path)
    except FileNotFoundError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ エラー: {e!s}\n\n必要な仕様書ファイルが見つかりません。",
                }
            ]
        }

    prompt = f"""以下の仕様書に基づいて、段階的に実装を進めてください：

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

### 1. 実装順序
Tasks.mdのTASK-IDの順序に従って実装を進めてください：
1. Phase 1のタスクから開始
2. 依存関係を考慮して順次実装
3. 各タスク完了後にテストを実行

### 2. 品質基準
- **コーディング規約**: プロジェクトの既存コードスタイルに従う
- **テスト**: 各機能に対して単体テストを作成
- **ドキュメント**: 主要な関数/クラスにはdocstringを追加
- **エラーハンドリング**: 適切な例外処理を実装

### 3. トレーサビリティ
実装時は以下をコメントで明記：
```
// Implements: REQ-XX, TASK-YY-ZZ
```

### 4. 検証項目
各タスク完了時に確認：
- [ ] 関連するREQ-IDの要件を満たしている
- [ ] Designで定義されたインターフェースに準拠
- [ ] テストが通過する
- [ ] コードレビューの準備ができている

### 5. 進捗報告
各タスク完了時に以下を報告：
- 完了したTASK-ID
- 実装した機能の概要
- テスト結果
- 次のタスクの開始準備状況

## 開始指示
最初のタスク（TASK-01-01）から実装を開始してください。
実装に必要な追加情報があれば質問してください。

準備ができたら、"実装を開始します" と宣言してから作業を始めてください。"""

    return {
        "content": [
            {
                "type": "text",
                "text": prompt,
            }
        ]
    }
