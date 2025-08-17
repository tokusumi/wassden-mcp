# タスクバリデーション要件

## 概要

tasks.mdのDAG（有向非環グラフ）要件と循環依存検出、「非コーディング作業の除外」範囲を定義します。

## TASK-ID形式

### 基本形式
```regex
^TASK-\d{2}(-\d{2}){1,2}$
```

### 有効例
- `TASK-01-01`: メインタスク.サブタスク
- `TASK-01-02`: メインタスク.サブタスク  
- `TASK-01-01-01`: メインタスク.サブタスク.詳細タスク
- `TASK-02-03-05`: メインタスク.サブタスク.詳細タスク

### 無効例  
- `TASK-00-01`: 00は無効
- `TASK-01`: サブタスクが必須
- `TASK-1-1`: ゼロパディング必須
- `task-01-01`: 大文字小文字厳密

## DAG（有向非環グラフ）要件

### 循環依存検出

**実装ロジック**:
```python
# 依存関係の抽出
dependencies = {}
for line in content.split("\n"):
    if "依存" in line or "Depends on" in line:
        parts = line.split(":")
        if len(parts) == 2:
            task_match = re.search(r"\bTASK-\d{2}(?:-\d{2}){0,2}\b", parts[0])
            if task_match:
                task_id = task_match.group(0)
                dep_ids = re.findall(r"\bTASK-\d{2}(?:-\d{2}){0,2}\b", parts[1])
                dependencies[task_id] = dep_ids

# 循環依存チェック（簡易版）
for task_id, deps in dependencies.items():
    for dep in deps:
        if dep in dependencies and task_id in dependencies[dep]:
            errors.append(f"Circular dependency detected: {task_id} <-> {dep}")
```

### 依存関係記述形式

```markdown
**TASK-01-01**: 基盤実装
- 依存: なし

**TASK-01-02**: API実装  
- 依存: TASK-01-01

**TASK-02-01**: フロントエンド実装
- 依存: TASK-01-02, TASK-01-03
```

## トレーサビリティ要件

### 100%カバレッジ必須

**重要**: 全ての要件（REQ-ID）と設計要素（design components）は、必ずtasks.mdで参照されなければなりません。

- **要件参照**: 各REQ-IDは最低1つのタスクで参照されること
- **設計参照**: 各設計コンポーネントは最低1つのタスクで参照されること
- **参照漏れ**: 1つでも未参照があればバリデーションエラー

### 参照形式例

```markdown
- **TASK-01-01**: 認証システム実装 [REQ-01, REQ-05]
  - 関連: [auth-service, database-layer]
```

## 非コーディング作業の除外範囲

### 除外対象

以下は「実装タスク」として扱わず、依存関係チェックから除外：

1. **調査・研究タスク**
   - 技術調査
   - ライブラリ評価
   - パフォーマンス分析

2. **文書作成タスク**  
   - 仕様書作成
   - マニュアル作成
   - API文書作成

3. **環境・インフラタスク**
   - CI/CD設定
   - デプロイ環境構築
   - 監視設定

4. **レビュー・承認タスク**
   - コードレビュー
   - 設計レビュー  
   - 承認プロセス

### 判定基準

タスク名に以下のキーワードが含まれる場合は非コーディング作業：

```python
NON_CODING_KEYWORDS = [
    "調査", "research", "investigate",
    "文書", "document", "manual", 
    "レビュー", "review", "approve",
    "設定", "config", "setup", "deploy",
    "分析", "analyze", "evaluation"
]
```

### 除外例

```markdown
**TASK-00-01**: 技術調査 (除外)
**TASK-00-02**: 要件文書作成 (除外)  
**TASK-01-01**: 認証モジュール実装 (含む)
**TASK-01-02**: API エンドポイント実装 (含む)
**TASK-00-03**: デプロイ設定 (除外)
```

## 必須セクション

tasks.mdには以下のセクションが必要：

1. **概要**: プロジェクト全体のタスク概要
2. **タスク一覧**: 各タスクの詳細定義
3. **依存関係**: タスク間の依存関係
4. **マイルストーン**: 重要な完了時点

## バリデーション処理

### 1. 構造チェック
- 必須セクションの存在確認
- TASK-ID形式の検証

### 2. 依存関係チェック  
- 循環依存の検出
- 存在しないタスクへの参照チェック

### 3. 一意性チェック
- 重複TASK-IDの検出（定義部分のみ）

## エラー例

```
❌ Duplicate TASK-IDs found: TASK-01-01, TASK-02-01
❌ Invalid TASK-ID format: TASK-1-01  
❌ Circular dependency detected: TASK-01-01 <-> TASK-01-02
❌ Missing required section: 依存関係
❌ Requirements not referenced in tasks: REQ-03, REQ-05
❌ Design components not referenced in tasks: api-gateway, auth-service
```

## バリデーション成功例

```
✅ tasks.md の検証に成功しました！

## 検証結果
- タスク数: 8
- 依存関係数: 6
- 未参照要件: 0件
- 未参照設計要素: 0件

タスクドキュメントは正しい形式で記載されています。実装フェーズに進むことができます。
```