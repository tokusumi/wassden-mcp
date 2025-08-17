"""Code analysis and implementation prompt generation."""

import re
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

### 4. 品質レビュー（重要）
**各TASK-ID完了時には必ず以下の手順でレビューを実施してください**：

1. **レビュープロンプト生成**:
   ```
   generate-review-prompt <TASK-ID>
   ```
   例: `generate-review-prompt TASK-01-01`

2. **自己レビュー実施**:
   生成されたレビュープロンプトに従って厳格な品質チェックを実行
   - 🚫 テスト改竄の検出（必須）
   - 🚫 TODO/FIXME禁止チェック（必須）
   - ✅ 要件トレーサビリティ確認
   - ✅ プロジェクト固有の品質基準実行

3. **合格判定**:
   全項目合格の場合のみ tasks.md にチェックマーク ✅ を追加

**重要**: レビューで不合格の場合は修正完了まで次のタスクに進まないでください。

### 5. 検証項目（基本）
各タスク完了時に確認：
- [ ] 関連するREQ-IDの要件を満たしている
- [ ] Designで定義されたインターフェースに準拠
- [ ] テストが通過する
- [ ] レビュープロンプトによる品質チェック完了

### 6. 進捗報告
各タスク完了時に以下を報告：
- 完了したTASK-ID
- 実装した機能の概要
- テスト結果
- 品質レビュー結果
- 次のタスクの開始準備状況

## 開始指示
最初のタスク（TASK-01-01）から実装を開始してください。
実装に必要な追加情報があれば質問してください。

**実装ワークフロー**:
1. TASK-ID を実装
2. `generate-review-prompt <TASK-ID>` でレビュープロンプト生成
3. レビュープロンプトに従って品質チェック実行
4. 全項目合格なら tasks.md にチェックマーク ✅ 追加
5. 次のTASK-IDに進む

準備ができたら、"実装を開始します" と宣言してから作業を始めてください。

**注意**: 各タスク完了時の品質レビューは必須です。レビューをスキップしないでください。"""

    return {
        "content": [
            {
                "type": "text",
                "text": prompt,
            }
        ]
    }


async def handle_generate_review_prompt(args: dict[str, Any]) -> dict[str, Any]:
    """Generate implementation review prompt for specific TASK-ID."""
    task_id = args.get("taskId")
    tasks_path = args.get("tasksPath", "specs/tasks.md")
    design_path = args.get("designPath", "specs/design.md")
    requirements_path = args.get("requirementsPath", "specs/requirements.md")

    if not task_id:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "❌ エラー: taskId パラメータが必要です。\n例: {'taskId': 'TASK-01-01'}",
                }
            ]
        }

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

    # Extract task info
    task_info = _extract_task_info(tasks, task_id)
    if not task_info:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ エラー: タスク {task_id} が tasks.md で見つかりません。",
                }
            ]
        }

    # Extract related requirements and test requirements
    related_reqs = _extract_related_requirements(task_info, requirements)
    related_trs = _extract_related_test_requirements(task_info, requirements)

    # Generate review prompt
    prompt = f"""# {task_id} 実装レビュープロンプト

## 📋 実装対象タスク

**TASK-ID**: {task_id}
**概要**: {task_info.get("summary", "N/A")}
**フェーズ**: {task_info.get("phase", "N/A")}

## 🎯 関連要件

### 機能要件 (REQ)
{_format_requirements_list(related_reqs)}

### テスト要件 (TR)
{_format_requirements_list(related_trs)}

## 🚫 品質ガードレール（厳格チェック）

### 1. テストケース改竄の検出
- **禁止事項**: テストを通すためのテストケース改竄
- **チェック方法**:
  - TR要件で定義されたテストシナリオと実際のテストコードを比較
  - `pytest.skip`, `@pytest.mark.skip`, `pass`の不正使用をチェック
  - テストの期待値を実装に合わせて変更していないかチェック
- **合格基準**: TR仕様通りのテストが実装され、実機能でテストが通過

### 2. 未実装検出（TODO/FIXME禁止）
- **禁止事項**: TODO/FIXMEコメントでの未実装放置
- **チェック方法**:
  - `# TODO`, `# FIXME`, `// TODO`, `/* TODO */`の検索
  - `NotImplementedError`の検索
  - `pass`文のみの関数/メソッドの検索
- **合格基準**: 全機能が完全実装済み、プレースホルダーなし

## 🔍 静的品質チェック（必須）

### プロジェクト品質基準の特定と実行
このプロジェクトで定義されている品質チェックコマンドを特定し、実行してください：

#### 1. 品質チェックコマンドの調査
以下を順番に確認し、このプロジェクトの品質基準を特定してください：
- `CLAUDE.md` ファイルの Commands セクション
- `Makefile` の lint/format/test/check ターゲット
- `package.json` の scripts セクション（Node.js）
- `pyproject.toml` の tool設定（Python）
- `README.md` の開発手順

#### 2. 必須チェック項目
特定した品質チェックを **全て実行** し、**全てPASS** することを確認：
- **フォーマッター**: コードスタイルの統一
- **リンター**: 静的コード解析
- **型チェッカー**: 型安全性確認（TypeScript/Python等）
- **テスト実行**: 単体テスト・結合テスト
- **総合チェック**: 上記を統合したコマンド

#### 3. 実行例（プロジェクトに応じて調整）
```bash
# 例1: Python プロジェクト
make check          # または
uv run ruff format && uv run ruff check && uv run mypy . && uv run pytest

# 例2: Node.js プロジェクト
npm run check       # または
npm run format && npm run lint && npm run typecheck && npm test

# 例3: Go プロジェクト
make test           # または
go fmt ./... && go vet ./... && go test ./...
```

#### 4. 合格基準
- **全コマンドが正常終了**（exit code 0）
- **警告・エラーが0件**
- **テストカバレッジが既存水準を維持**

## 📊 設計準拠性チェック

### 期待ファイル構成
{_extract_file_structure_from_design(design)}

### 期待インターフェース
{_extract_interfaces_from_design(design)}

## ✅ 合格判定基準（全項目必須）

以下の全項目をチェックし、**全てPASS**した場合のみ合格としてください：

1. [ ] 🚫 テストケース改竄なし（TR仕様通りのテスト実装）
2. [ ] 🚫 TODO/FIXME/未実装なし（完全実装済み）
3. [ ] ✅ 関連REQ全て実装済み（機能要件充足）
4. [ ] ✅ 関連TR全てテスト済み（テスト要件充足）
5. [ ] ✅ 設計書準拠（ファイル構成・インターフェース）
6. [ ] ✅ 品質チェック全PASS（linter/formatter/test）

**重要**: 品質ガードレール（項目1,2）は絶対条件です。
これらに違反している場合は他が完璧でも不合格とし、修正してから再レビューしてください。

## 📝 レビュー実行指示

1. 上記チェック項目を順番に確認
2. 各項目の結果を詳細に報告
3. 不合格項目があれば具体的な修正内容を提案
4. **全項目合格の場合のみ**: tasks.md の {task_id} 行に ✅ を追加

## 📈 レビュー完了後の次ステップ

合格判定後：
1. tasks.md の {task_id} 行にチェックマーク ✅ を追加
2. 次のタスクID確認（依存関係考慮）
3. 次のタスクの実装開始準備

不合格の場合：
1. 指摘事項の修正実施
2. 修正完了後に再度このレビューを実行
3. 全項目合格まで繰り返し
"""

    return {
        "content": [
            {
                "type": "text",
                "text": prompt,
            }
        ]
    }


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
    for line in lines:
        if req_id in line and ("システムは" in line or "テスト" in line):
            # Extract requirement text
            return line.strip()
    return None


def _format_requirements_list(requirements: list[str]) -> str:
    """Format requirements list for display."""
    if not requirements:
        return "なし"

    return "\n".join(f"- {req}" for req in requirements)


def _extract_file_structure_from_design(design_content: str) -> str:
    """Extract expected file structure from design.md."""
    # Simple extraction - look for file/module sections
    lines = design_content.split("\n")

    structure_lines = [
        line.strip()
        for line in lines
        if any(keyword in line.lower() for keyword in ["ファイル", "file", "モジュール", "module", "構成"])
    ]

    return "\n".join(structure_lines) if structure_lines else "設計書から構成情報を確認してください"


def _extract_interfaces_from_design(design_content: str) -> str:
    """Extract expected interfaces from design.md."""
    # Simple extraction - look for interface/API sections
    lines = design_content.split("\n")

    interface_lines = [
        line.strip()
        for line in lines
        if any(
            keyword in line.lower()
            for keyword in ["api", "インターフェース", "interface", "関数", "function", "メソッド", "method"]
        )
    ]

    return "\n".join(interface_lines) if interface_lines else "設計書からインターフェース情報を確認してください"
