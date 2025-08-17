# CLI リファレンス

## 概要

wassdenのコマンドライン インターフェース（CLI）の使用方法とMCPサーバー起動オプションを説明します。

## インストールと基本使用

```bash
# インストール
pip install wassden

# ヘルプ表示
wassden --help

# バージョン確認
wassden --version
```

## MCPサーバー起動

### 基本コマンド

```bash
wassden start-mcp-server [OPTIONS]
```

### Transport オプション

wassdenは3つのトランスポート方式をサポート：

#### 1. STDIO (デフォルト)
標準入出力を使用。Claude Code等のMCPクライアントで最も一般的。

```bash
# デフォルト（STDIO）
wassden start-mcp-server

# 明示的にSTDIO指定
wassden start-mcp-server --transport stdio
```

#### 2. SSE (Server-Sent Events)
HTTP Server-Sent Eventsを使用。Webブラウザー対応。

```bash
# SSE（デフォルト: 127.0.0.1:3001）
wassden start-mcp-server --transport sse

# カスタムホスト・ポート
wassden start-mcp-server --transport sse --host 0.0.0.0 --port 8080
```

#### 3. Streamable HTTP
HTTPストリーミングを使用。高性能が必要な場合。

```bash
# Streamable HTTP（デフォルト: 127.0.0.1:3001）
wassden start-mcp-server --transport streamable-http

# カスタムホスト・ポート  
wassden start-mcp-server --transport streamable-http --host localhost --port 5000
```

### パラメーター詳細

| オプション | 型 | デフォルト値 | 説明 |
|-----------|----|-----------|----|
| `--transport` | enum | `stdio` | トランスポート方式（stdio/sse/streamable-http） |
| `--host` | string | `127.0.0.1` | HTTPホスト（SSE/streamable-http時のみ） |
| `--port` | int | `3001` | HTTPポート（SSE/streamable-http時のみ） |

## Claude Code設定例

Claude Codeでwassdenを使用する場合の設定例：

### claude_desktop_config.json

```json
{
  \"mcpServers\": {
    \"wassden\": {
      \"command\": \"wassden\",
      \"args\": [\"start-mcp-server\"],
      \"env\": {}
    }
  }
}
```

### カスタムポート使用時

```json
{
  \"mcpServers\": {
    \"wassden-sse\": {
      \"command\": \"wassden\", 
      \"args\": [\"start-mcp-server\", \"--transport\", \"sse\", \"--port\", \"8080\"],
      \"env\": {}
    }
  }
}
```

## バリデーションコマンド

### Requirements検証

```bash
# デフォルトパス（specs/requirements.md）
wassden validate-requirements

# カスタムパス
wassden validate-requirements --requirementsPath ./my-requirements.md
```

### Design検証

```bash  
# デフォルトパス
wassden validate-design

# カスタムパス
wassden validate-design --designPath ./design.md --requirementsPath ./requirements.md
```

**重要**: design.mdは全要件（REQ-ID）を参照する必要があります。1つでも未参照があるとエラーになります。

### Tasks検証

```bash
# デフォルトパス（specs/tasks.md）
wassden validate-tasks

# カスタムパス
wassden validate-tasks --tasksPath ./my-tasks.md
```

**重要**: tasks.mdは100%トレーサビリティが必須です：
- 全要件（REQ-ID）が参照されている必要があります
- 全設計コンポーネントが参照されている必要があります
- 1つでも未参照があるとエラーになります

## 開発環境での起動

### 開発サーバー（リロード有効）

```bash
# uvでの開発モード起動
uv run wassden start-mcp-server

# ホットリロード（開発時）
uv run --reload wassden start-mcp-server --transport sse --port 3001
```

### デバッグモード

```bash
# ログレベル設定（環境変数）
WASSDEN_LOG_LEVEL=DEBUG wassden start-mcp-server

# 詳細出力
wassden start-mcp-server --verbose
```

## パフォーマンス指標

### ベンチマーク結果
- **Throughput**: 198,406+ requests/second
- **Latency**: <0.01ms average response time
- **Transport**: STDIO推奨（最高性能）
- **Validation**: 100%トレーサビリティチェック対応

### 推奨設定

| 用途 | Transport | 設定例 |
|------|-----------|--------|
| Claude Code連携 | stdio | `wassden start-mcp-server` |
| Web開発 | sse | `--transport sse --port 3001` |
| 高性能API | streamable-http | `--transport streamable-http --host 0.0.0.0` |
| 厳密な品質管理 | stdio | 100%トレーサビリティ検証 |

## トラブルシューティング

### ポート使用中エラー
```bash
# ポート変更
wassden start-mcp-server --transport sse --port 3002
```

### 権限エラー  
```bash
# ユーザー権限で低番号ポート回避
wassden start-mcp-server --transport sse --port 8080
```

### Claude Code接続エラー
```bash
# STDIO確認（最も安定）
wassden start-mcp-server --transport stdio
```

### バリデーションエラー

#### 未参照要件エラー
```
❌ Requirements not referenced in tasks: REQ-03, REQ-05
```
**解決方法**: tasks.mdで該当要件を参照するタスクを追加

#### 未参照設計要素エラー  
```
❌ Design components not referenced in tasks: api-gateway
```
**解決方法**: tasks.mdで該当コンポーネントを参照するタスクを追加

#### 循環依存エラー
```
❌ Circular dependency detected: TASK-01-01 <-> TASK-01-02
```
**解決方法**: tasks.mdの依存関係を見直して循環を解消