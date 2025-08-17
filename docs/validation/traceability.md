# トレーサビリティ要件

## 概要

REQ↔DESIGN↔TASKの必須リンク条件と、実装で使用されているトレーサビリティ検証ルールを定義します。

## トレーサビリティルール

### 1. Requirements → Design

**必須条件**: 
- design.mdは全てのREQ-IDを参照すること
- 未参照の要件がある場合はバリデーションエラー

**実装**:
```python
# design.mdで参照されているREQ-ID
referenced_reqs = set(re.findall(r"\bREQ-\d{2}\b", design_content))

# requirements.mdの全REQ-ID
all_reqs = set(re.findall(r"\bREQ-\d{2}\b", requirements_content))

# 未参照の要件をチェック
missing_refs = list(all_reqs - referenced_reqs)
if missing_refs:
    errors.append(f"Missing references to requirements: {', '.join(sorted(missing_refs))}")
```

### 2. Design → Tasks

**必須条件**:
- tasks.mdは関連するDESIGN要素を参照すること
- 各タスクは設計根拠を明確にすること

**検証方法**:
- 現在は構造チェックのみ実装
- 将来的にDESIGN-ID導入予定

### 3. Tasks → Code

**必須条件**:
- 実装時にTASK-IDとの対応を明確にすること
- コミットメッセージやPRでTASK-ID参照推奨

## ID参照パターン

### Requirements内での参照
```markdown
## 2. 機能要件

- **REQ-01**: システムはユーザー認証機能を提供すること
- **REQ-02**: システムはAPIエンドポイントを公開すること
```

### Design内での参照
```markdown
## アーキテクチャ

認証システム（REQ-01を実現）は以下の構成とする：
- JWT トークン認証（REQ-01, REQ-03）
- セッション管理（REQ-01）

## API設計

RESTful API（REQ-02）の詳細仕様：
```

### Tasks内での参照  
```markdown
## タスク一覧

**TASK-01-01**: 認証モジュール実装
- 対応要件: REQ-01
- 設計参照: アーキテクチャ > 認証システム

**TASK-02-01**: API エンドポイント実装  
- 対応要件: REQ-02
- 設計参照: API設計
```

## バリデーション要件

**100%カバレッジ必須**: 全ての要件とデザイン要素は必ず参照されること

### 例外扱い

以下の場合のみ例外として扱う：

1. **プロトタイプ段階**: 部分的な実装での一時的な未参照
2. **段階的実装**: 将来のリリースで実装予定の要件  
3. **非実装要件**: 調査・検討のみで実装不要な要件

例外処理時は明示的にコメント記載：

```markdown
<!-- REQ-05: 次期リリース対応予定のため一時的に未実装 -->
```

## チェック項目

### Requirements段階
- [ ] 全REQ-IDが一意である
- [ ] REQ-IDが正しい形式（REQ-01～REQ-99）
- [ ] 必須セクションが存在する

### Design段階  
- [ ] requirements.mdの全REQ-IDを参照している
- [ ] 必須セクション（アーキテクチャ、コンポーネント設計、データ、API、非機能、テスト）が存在する
- [ ] REQ-ID参照が文書内に存在する

### Tasks段階
- [ ] 全TASK-IDが一意である  
- [ ] TASK-IDが正しい形式（TASK-XX-XX）
- [ ] 循環依存が存在しない
- [ ] 必須セクション（概要、タスク一覧、依存関係、マイルストーン）が存在する