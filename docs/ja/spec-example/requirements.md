# requirements.md

## 0. サマリー

Agent向けSpec-Driven Development支援MCPツール

- Agentが受託した開発依頼に対して、段階的プロンプト生成により品質の高いSpec作成を支援
- Requirements → Design → Tasks → Code の各段階で適切なプロンプトを提供
- 生成物のValidation実行と再生成指示によるPDCAサイクル形成
- Traceability管理により変更時の影響波及を最小化

## 1. 用語集

- **MCP (Model Context Protocol)**: Agent-IDE間ツール連携標準プロトコル
- **Agent**: Claude Code等のAI開発アシスタント
- **Spec-Driven Development**: 仕様主導開発手法
- **Prompt Generation**: Agent向け作業指示プロンプト自動生成
- **Validation**: 生成物品質検証とフィードバック機能
- **Traceability**: 要件-設計-タスク間の双方向対応関係管理
- **PDCA**: Plan-Do-Check-Act 継続改善サイクル
- **EARS**: Easy Approach to Requirements Syntax 要件記述形式
- **WBS**: Work Breakdown Structure 作業分解構造

## 2. スコープ

### インスコープ

- Agent向けプロンプト生成機能（Requirements/Design/Tasks/Code各段階）
- 生成物Validation機能と再生成指示機能
- 情報不足時のユーザー向け質問生成機能
- Traceability管理と変更影響分析機能
- Agent作業品質向上のガイダンス機能

### アウトオブスコープ

- 直接的なファイル生成・編集機能
- Agent以外のクライアント向け機能
- 実際のコード実装機能
- プロジェクト管理機能
- バージョン管理機能

## 3. 制約

- Python 3.12+環境での動作
- FastMCP使用必須
- Claude Code, Cursor, VS Code MCP対応版での動作保証
- プロンプト応答は10,000文字以内
- リアルタイム応答性能（< 1秒）

## 4. 非機能要件（NFR）

- **NFR-01**: 応答時間 < 1秒（プロンプト生成・検証処理）
- **NFR-02**: プロンプト品質の一貫性（EARS準拠、WBS準拠）
- **NFR-03**: Traceability完全性（要件⇔設計⇔タスク双方向追跡）
- **NFR-04**: Agent向けガイダンスの明確性（作業手順・注意事項）
- **NFR-05**: エラーハンドリング充実（不正入力・不完全データ対応）

## 5. KPI / 受入基準

- **KPI-01**: Agent作業プロンプト生成成功率 99%以上
- **KPI-02**: 生成物Validation精度 95%以上（偽陽性/偽陰性最小化）
- **KPI-03**: Traceability完全性 100%（欠損・循環依存なし）
- **KPI-04**: Agent作業効率向上 50%以上（従来手法比）
- **KPI-05**: 情報不足検出率 90%以上（適切な質問生成）

## 6. 機能要件（EARS）

- **REQ-01**: システムは、Agentから初回依頼を受信したとき、情報充足性を分析し、不足情報に対するユーザー向け質問プロンプトを生成すること
- **REQ-02**: システムは、十分な情報が提供されたとき、EARS形式requirements.md生成用のAgent向けプロンプトを提供すること
- **REQ-03**: システムは、requirements.mdを受信したとき、構造・内容を検証し、不備があれば修正指示プロンプトを生成すること
- **REQ-04**: システムは、有効なrequirements.mdに基づき、design.md生成用のAgent向けプロンプトを提供すること
- **REQ-05**: システムは、design.mdを受信したとき、構造・内容・トレーサビリティを検証し、不備があれば修正指示プロンプトを生成すること
- **REQ-06**: システムは、有効なdesign.mdに基づき、WBS形式tasks.md生成用のAgent向けプロンプトを提供すること
- **REQ-07**: システムは、tasks.mdを受信したとき、構造・内容・依存関係を検証し、不備があれば修正指示プロンプトを生成すること
- **REQ-08**: システムは、有効なtasks.mdに基づき、段階的コード実装用のAgent向けプロンプト（注意事項付き）を提供すること
- **REQ-09**: システムは、任意のspec変更時、影響を受ける項目を特定し、併せて修正させるプロンプトを生成すること
- **REQ-10**: システムは、現在のtraceability状況をレポート形式で提供すること

## 7. テスト要件（Testing Requirements）

- **TR-01**: プロンプト生成内容検証（期待される指示・注意事項が含まれていること）
- **TR-02**: Validation精度検証（正常/異常ケースでの適切な判定）
- **TR-03**: 質問生成品質検証（情報不足検出・適切な質問文生成）
- **TR-04**: Traceability管理精度検証（対応関係完全性・変更影響分析）
- **TR-05**: パフォーマンステスト（応答時間要件確認）
- **TR-06**: プロンプト文字数制限テスト（10,000文字以内）
- **TR-07**: Agent統合テスト（実際のAgent応答確認）
