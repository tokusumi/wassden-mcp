# Specification Document Format Standards

This document defines the standard format for specification documents in wassden. All documents must follow these formats for proper traceability and validation.

## 📋 Requirements Document (requirements.md)

### Structure
```markdown
# requirements.md

## 0. サマリー
- **背景/目的**: [プロジェクトの背景と達成したい目的]
- **対象ユーザー/主要シナリオ**: [誰がどのように使うか]

## 1. 用語集
- **Term**: Definition
- **MCP (Model Context Protocol)**: Definition

## 2. スコープ
### インスコープ
- [What to do]

### アウトオブスコープ
- [What not to do]

## 3. 制約
- Technical constraints
- Business constraints
- Environmental constraints

## 4. 非機能要件（NFR）
- **NFR-01**: Performance requirements
- **NFR-02**: Security requirements
- **NFR-03**: Availability requirements
- **NFR-04**: Maintainability requirements
- **NFR-05**: Other requirements

## 5. KPI / 受入基準
- **KPI-01**: Measurable success metric
- **KPI-02**: Measurable success metric

## 6. 機能要件（EARS）
- **REQ-01** - <要件タイトル>: システムは、[条件]のとき、[動作]すること
  - 受け入れ観点1
  - 受け入れ観点2
- **REQ-02** - <要件タイトル>: システムは、[条件]のとき、[動作]すること
  - 受け入れ観点1
  - 受け入れ観点2

## 7. テスト要件（Testing Requirements）
- **TR-01**: Test requirement description
- **TR-02**: Test requirement description
```

### Key Rules
- REQ-ID format: `REQ-\d{2}` (REQ-01 to REQ-99)
- NFR-ID format: `NFR-\d{2}` (NFR-01 to NFR-99)
- KPI-ID format: `KPI-\d{2}` (KPI-01 to KPI-99)
- TR-ID format: `TR-\d{2}` (TR-01 to TR-99)
- EARS format: "システムは、[condition]のとき、[action]すること"

## 🏗️ Design Document (design.md)

### Structure
```markdown
# design.md

## 1. アーキテクチャ概要
- **コンテキスト/依存関係/制約**: [システムの位置づけと制限事項]
- **全体図**: [コンポーネント/データフロー/シーケンスの概要]
[Requirements: REQ-01, REQ-02, ...]

## 2. コンポーネント設計
- **component-a**:
  - **役割**: [コンポーネントの責務]
  - **要件**: [REQ-01, REQ-02]
  - **入出力**: [インターフェース定義]
  - **例外・リトライ**: [エラーハンドリング方針]
  - **可観測性**: [ログ、メトリクス、トレース]

- **component-b**:
  - **役割**: [コンポーネントの責務]
  - **要件**: [REQ-03]
  - **入出力**: [インターフェース定義]
  - **例外・リトライ**: [エラーハンドリング方針]
  - **可観測性**: [ログ、メトリクス、トレース]

## 3. データモデル
[Data structures and models]

## 4. API/インターフェース
- **tool_name**:
  - **概要**: [機能説明]
  - **エンドポイント**: [URL/パス]
  - **リクエスト/レスポンス**: [形式と例]
  - **エラー**: [エラーコードと対処]
  - **モジュール境界**: [責任分界点]

## 5. 非機能・品質
- **パフォーマンス**: Details [NFR-01]
- **セキュリティ**: Details [NFR-02]
- **可用性**: Details [NFR-03]

## 6. テスト戦略
- **単体/結合/E2E の役割分担**: [各レベルでの検証内容]
- **test-scenario**: [重要なテストケース]
  - **テストデータ方針**: [テストデータの準備方法]
  - **観測可能な合否基準**: [成功/失敗の判定基準]

## 7. トレーサビリティ (必須)
- REQ-XX ⇔ **component-name**
- TR-XX ⇔ **test-scenario**

## 8. フロー設計
- **主要シーケンス**: [正常系の処理フロー]
- **状態遷移**: [状態管理とトランジション]
- **バックプレッシャー/キュー処理**: [負荷制御メカニズム]

## 9. 障害・エッジケース
- **フェイルパターン**: [想定される障害]
- **フォールバック**: [代替処理]
- **タイムアウト/リトライ方針**: [時間制限と再試行戦略]

## 10. セキュリティ & コンプライアンス
- **認証/認可**: [アクセス制御方式]
- **データ保護**: [暗号化、マスキング]
- **監査ログ**: [記録対象と保持期間]
- **秘密管理**: [シークレットの取り扱い]

## 11. リスクと対応 (Optional)
- **Risk**: Description → Mitigation
```

### Key Rules
- Component format: `**component-name**` (bold, kebab-case)
- REQ references: `[REQ-01, REQ-02]` in brackets
- NFR references: `[NFR-01]` in brackets
- Component names must be consistent across documents

## 📝 Tasks Document (tasks.md)

### Structure (WBS Format - Recommended)
```markdown
# tasks.md

## 1. 概要
[WBS overview and project approach]

## 2. タスク一覧
### Phase 1: Foundation
- [ ] **TASK-01-01**: Task name
  - **REQ**: [REQ-01, REQ-02]
  - **DC**: **component-name**
  - **依存**: なし
  - **受け入れ観点**:
    - 観点1: [検証可能な条件]
    - 観点2: [検証可能な条件]
  - **手順** (Optional):
    1. Step 1
    2. Step 2

- [ ] **TASK-01-02**: Task name
  - **REQ**: [TR-01]
  - **DC**: **test-scenario**
  - **依存**: TASK-01-01
  - **受け入れ観点**:
    - 観点1: [検証可能な条件]

### Phase 2: Implementation
- [ ] **TASK-02-01**: Task name
  - **REQ**: [REQ-04]
  - **DC**: **component-a**, **component-b**
  - **依存**: TASK-01-02
  - **受け入れ観点**:
    - 観点1: [検証可能な条件]

## 3. 依存関係
```
TASK-01-01 → TASK-01-02 → TASK-02-01
```

## 4. マイルストーン
- **M1**: Phase 1 completion (TASK-01-XX完了)
- **M2**: Phase 2 completion (TASK-02-XX完了)

## 5. リスクと対策
- **リスク**: [Description]
  - 影響タスク: TASK-XX-XX
  - 対策: [Mitigation]
```


### Key Rules
- Task format: `- [ ] **TASK-\d{2}-\d{2}**: Task name`
- Task status: `- [x]` (completed) or `- [ ]` (pending)
- Component references: **DC**: `**component-name**` (must match design.md)
- REQ references: **REQ**: `[REQ-01]` in brackets
- Dependencies: `依存: TASK-XX-XX` or `依存: なし`
- Acceptance criteria: `受け入れ観点` with verifiable conditions

## 🔗 Traceability Rules

### Requirements → Design
- Every REQ-XX must be referenced in design.md with format: `[REQ-01]`
- Every TR-XX must be referenced in design.md with format: `[TR-01]`
- References must appear near **component-name** or **test-scenario** definitions
- Check Traceability section (Section 7) for complete mapping
- Example: `REQ-01 authentication is handled by **auth-service**`
- Example: `TR-01 is covered by **test-scenario**`

### Design → Tasks  
- Every **component-name** must be referenced in tasks.md
- Every **test-scenario** must be referenced in tasks.md
- References must use exact same formatting via DC field
- Example: `**DC**: **auth-service**` or `**DC**: **test-scenario**`

### Pattern Matching
```python
# Requirements ID
r"\bREQ-\d{2}\b"  # REQ-01 to REQ-99

# Test Requirements ID  
r"\bTR-\d{2}\b"   # TR-01 to TR-99

# Design Components and Test Scenarios
r"\*\*([a-zA-Z0-9_-]+)\*\*"  # **component-name** or **test-scenario**

# Tasks (checkbox format)
r"- \[[x ]\] (\d+(?:\.\d+)*)"  # - [x] 1.0 or - [ ] 1.2.3

# Tasks (WBS format)
r"\bTASK-\d{2}(?:-\d{2}){0,2}\b"  # TASK-01 or TASK-01-01
```

## ✅ Validation Rules

### Requirements Validation
1. All sections (0-7) must be present
2. Summary must include 背景/目的 and 対象ユーザー/主要シナリオ
3. REQ-IDs must be unique and sequential with title
4. Each REQ must have acceptance criteria (受け入れ観点)
5. EARS format must be followed for functional requirements
6. NFR/KPI/TR IDs must be unique

### Design Validation
1. All requirements must be referenced in components
2. Component names must use kebab-case format (**component-name**)
3. Each component must specify: 役割, 要件, 入出力, 例外・リトライ, 可観測性
4. APIs must define: 概要, エンドポイント, リクエスト/レスポンス, エラー, モジュール境界
5. Test strategy must include: 役割分担, 主要シナリオ, テストデータ方針, 合否基準
6. Traceability section (Section 7) is mandatory
7. Must include フロー設計, 障害・エッジケース, セキュリティ sections

### Tasks Validation
1. Each task must specify: REQ, DC, 依存, 受け入れ観点
2. All components from design must be referenced via DC field
3. Task IDs must follow format: TASK-XX-XX
4. Dependencies must form valid DAG (no circular references)
5. All tasks must reference requirements via REQ field
6. Acceptance criteria (受け入れ観点) must be verifiable
7. Tasks must use checkbox format: `- [ ] **TASK-01-01**: Task name`

### Traceability Validation
1. 100% requirement coverage in design components (REQ-XX → **component-name**)
2. 100% test requirement coverage in design (TR-XX → **test-scenario**)
3. 100% component coverage in tasks (**component-name** → DC field)
4. 100% test scenario coverage in tasks (**test-scenario** → DC field)
5. Valid dependency DAG (no cycles)
6. Consistent naming across documents
7. Traceability section (Section 7) completeness verification

## 🔄 Change Management

When specifications change:
1. Update the changed document
2. Run `analyze-changes` to identify impacts
3. Update affected documents based on analysis
4. Validate all documents
5. Verify traceability completeness

## 📝 Examples

See `/docs/spec-example/` for complete examples:
- `requirements.md` - Full requirements example
- `design.md` - Full design example
- `tasks.md` - Full tasks example

These examples demonstrate proper formatting, cross-references, and traceability.