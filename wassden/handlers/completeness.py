"""Completeness checking handler."""

from typing import Any


async def handle_check_completeness(args: dict[str, Any]) -> dict[str, Any]:
    """Check user input completeness and generate questions or requirements prompt."""
    user_input = args.get("userInput", "")

    # Analyze input for missing information
    missing_info: list[str] = []

    # Check for technology stack
    if not any(
        keyword in user_input
        for keyword in ["技術スタック", "technology", "言語", "フレームワーク", "framework", "language"]
    ):
        missing_info.append("使用技術・プログラミング言語・フレームワークは何ですか？")

    # Check for target users
    if not any(keyword in user_input for keyword in ["ユーザー", "user", "対象", "target"]):
        missing_info.append("想定ユーザー・ターゲット利用者は誰ですか？")

    # Check for constraints
    if not any(keyword in user_input for keyword in ["制約", "constraint", "制限", "limitation"]):
        missing_info.append("技術的制約・ビジネス制約はありますか？")

    # Check for scope
    if not any(keyword in user_input for keyword in ["スコープ", "scope", "範囲", "range"]):
        missing_info.append("プロジェクトの範囲・やらないことは明確ですか？")

    # Build the response prompt
    base_prompt = f"""以下のプロジェクト情報を確認し、適切に対応してください：

## 提供された情報
{user_input}

## あなたの判断と対応

以下の重要な情報がすべて含まれているかを確認してください：
1. 使用技術・プログラミング言語・フレームワーク
2. 想定ユーザー・ターゲット利用者
3. 技術的制約・ビジネス制約
4. プロジェクトの範囲・やらないこと
5. 十分な詳細情報（100文字以上の説明）

### 情報が不足している場合
不足している具体的な情報について質問してください。
"""

    if missing_info:
        base_prompt += f"""
特に以下の点が不明です：
{chr(10).join(f"{i + 1}. {q}" for i, q in enumerate(missing_info))}
"""

    base_prompt += """

### 情報が十分な場合
そのまま EARS 形式の requirements.md を作成してください：

---

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
2. 機能要件は「システムは...すること」の形式で記録
3. 測定可能で検証可能な表現を使用
4. 曖昧な表現（"適切に"、"十分に"など）は避ける
5. 文字数: 2000-5000文字程度

---

上記の指示に従って、情報が十分な場合は requirements.md を直接作成、不足している場合は質問を返してください。"""

    return {
        "content": [
            {
                "type": "text",
                "text": base_prompt,
            }
        ]
    }
