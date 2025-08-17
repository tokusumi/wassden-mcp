"""Requirements handling functions."""

from typing import Any

from wassden.lib import fs_utils, validate


async def handle_prompt_requirements(args: dict[str, Any]) -> dict[str, Any]:
    """Generate prompt for creating requirements.md."""
    project_description = args.get("projectDescription", "")
    scope = args.get("scope", "")
    constraints = args.get("constraints", "")

    prompt = f"""以下の指示に従って、EARS形式のrequirements.mdファイルを作成してください：

## プロジェクト情報
- 概要: {project_description}
- スコープ: {scope or "スコープ情報を分析して記載"}
- 制約: {constraints or "技術的・ビジネス制約を分析して記載"}

## 作成するファイル
ファイル名: specs/requirements.md

## 必須構造
以下の章立てに従って作成してください：

### 0. サマリー
プロジェクトの概要を3-5文で記載

### 1. 用語集
- **MCP (Model Context Protocol)**: [定義]
- **プロジェクト固有用語**: [定義]

### 2. スコープ
#### インスコープ
- [やること]

#### アウトオブスコープ
- [やらないこと]

### 3. 制約
- [技術的制約]
- [ビジネス制約]
- [環境制約]

### 4. 非機能要件（NFR）
- **NFR-01**: [性能要件]
- **NFR-02**: [セキュリティ要件]
- **NFR-03**: [可用性要件]
- **NFR-04**: [保守性要件]
- **NFR-05**: [その他要件]

### 5. KPI / 受入基準
- **KPI-01**: [測定可能な成功指標]
- **KPI-02**: [測定可能な成功指標]
- [追加のKPI...]

### 6. 機能要件（EARS）
Easy Approach to Requirements Syntax（EARS）に従って記載：
- **REQ-01**: システムは、[条件]のとき、[動作]すること
- **REQ-02**: システムは、[条件]のとき、[動作]すること
- [追加の要件...]

## 作成指示
1. 各REQ-IDは連番（REQ-01, REQ-02...）で作成
2. 機能要件は「システムは...すること」の形式で記載
3. 測定可能で検証可能な表現を使用
4. 曖昧な表現（"適切に"、"十分に"など）は避ける
5. 文字数: 2000-5000文字程度

このプロンプトに従って、高品質なrequirements.mdを作成してください。"""

    return {
        "content": [
            {
                "type": "text",
                "text": prompt,
            }
        ]
    }


async def handle_validate_requirements(args: dict[str, Any]) -> dict[str, Any]:
    """Validate requirements.md and generate fix instructions if needed."""
    requirements_path = args.get("requirementsPath", "specs/requirements.md")

    try:
        content = await fs_utils.read_file(requirements_path)
        validation_result = validate.validate_requirements(content)

        if validation_result["isValid"]:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"""✅ requirements.md の検証に成功しました！

## 検証結果
- 要件数: {validation_result["stats"]["totalRequirements"]}
- NFR数: {validation_result["stats"]["totalNFRs"]}
- KPI数: {validation_result["stats"]["totalKPIs"]}

## 構造チェック
{chr(10).join(f"✅ {section}" for section in validation_result["foundSections"])}

要件は正しい形式で記載されています。次のステップ（design.md の作成）に進むことができます。""",
                    }
                ]
            }
        fix_instructions = chr(10).join(f"- {issue}" for issue in validation_result["issues"])

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"""⚠️ requirements.md に修正が必要です：

## 検出された問題
{fix_instructions}

## 修正手順
以下の指示に従って requirements.md を修正してください：

{chr(10).join(f"{i + 1}. {issue}" for i, issue in enumerate(validation_result["issues"]))}

## 修正後の確認
修正が完了したら、再度 validate_requirements を実行して検証してください。""",
                }
            ]
        }
    except FileNotFoundError:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"""❌ エラー: {requirements_path} が見つかりません。

まず prompt_requirements または check_completeness を使用して requirements.md を作成してください。""",
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
