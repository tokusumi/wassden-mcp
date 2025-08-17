"""Design handling functions."""

import contextlib
from typing import Any

from wassden.lib import fs_utils, validate


async def handle_prompt_design(args: dict[str, Any]) -> dict[str, Any]:
    """Generate prompt for creating design.md from requirements."""
    requirements_path = args.get("requirementsPath", "specs/requirements.md")

    try:
        requirements = await fs_utils.read_file(requirements_path)
    except FileNotFoundError:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"❌ エラー: Requirements file not found: {requirements_path}\n\n"
                    "まず requirements.md を作成してください。",
                }
            ]
        }

    prompt = f"""以下のrequirements.mdに基づいて、design.mdファイルを作成してください：

## Requirements内容
```markdown
{requirements}
```

## 作成するファイル
ファイル名: specs/design.md

## 必須構造
以下の章立てに従って作成してください：

### 1. アーキテクチャ概要
システムの全体構成とアプローチを説明
[Requirements: REQ-XX, REQ-YY, ...] ← 対応する要件IDを明記

### 2. コンポーネント設計
- **component-name**: 機能説明 [REQ-XX]
- **component-name**: 機能説明 [REQ-YY]

### 3. データモデル
TypeScript interfaceまたは図式でデータ構造を定義

### 4. API（MCPツール）
- **tool_name** → 機能説明
- **tool_name** → 機能説明

### 5. 非機能・品質
- **パフォーマンス**: [NFR対応]
- **セキュリティ**: [NFR対応]
- **可用性**: [NFR対応]

### 6. テスト戦略
#### 6.1 単体テスト
#### 6.2 統合テスト
#### 6.3 E2Eテスト
#### 6.4 パフォーマンステスト

### 7. トレーサビリティ
REQ-XX⇔component⇔task の対応関係を明記

### 8. リスクと対応
- **リスク1**: 説明 → 対応策
- **リスク2**: 説明 → 対応策

## 作成指示
1. 各章で関連するREQ-IDを [REQ-XX] 形式で明記
2. 技術的実装方針を具体的に記載
3. 非機能要件（NFR）との対応を明確にする
4. 文字数: 3000-6000文字程度
5. すべての要件がdesignのどこかで言及されていること

このプロンプトに従って、トレーサビリティが確保された高品質なdesign.mdを作成してください。"""

    return {
        "content": [
            {
                "type": "text",
                "text": prompt,
            }
        ]
    }


async def handle_validate_design(args: dict[str, Any]) -> dict[str, Any]:
    """Validate design.md structure and traceability."""
    design_path = args.get("designPath", "specs/design.md")
    requirements_path = args.get("requirementsPath", "specs/requirements.md")

    try:
        design_content = await fs_utils.read_file(design_path)

        # Try to read requirements for traceability check
        requirements_content = None
        with contextlib.suppress(FileNotFoundError):
            requirements_content = await fs_utils.read_file(requirements_path)

        validation_result = validate.validate_design(design_content, requirements_content)

        if validation_result["isValid"]:
            stats = validation_result.get("stats", {})
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"""✅ design.md の検証に成功しました！

## 検証結果
- 参照要件数: {stats.get("referencedRequirements", 0)}

デザインドキュメントは正しい形式で記載されています。次のステップ（tasks.md の作成）に進むことができます。""",
                    }
                ]
            }
        fix_instructions = chr(10).join(f"- {issue}" for issue in validation_result["issues"])

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"""⚠️ design.md に修正が必要です：

## 検出された問題
{fix_instructions}

## 修正手順
以下の指示に従って design.md を修正してください：

{chr(10).join(f"{i + 1}. {issue}" for i, issue in enumerate(validation_result["issues"]))}

## 修正後の確認
修正が完了したら、再度 validate_design を実行して検証してください。""",
                }
            ]
        }
    except FileNotFoundError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"""❌ エラー: {e!s}

まず prompt_design を使用して design.md を作成してください。""",
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
