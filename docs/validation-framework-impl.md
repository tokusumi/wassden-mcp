# Wassden Validation Framework 実装計画

## 概要

wassden (https://github.com/tokusumi/wassden-mcp) のMCPベース仕様駆動開発ツールキットに対する、品質検証フレームワークの実装計画。

## 検証対象

1. **Clarify-first（聞き返し）**: 仕様の構造適合と品質向上の効果検証
2. **Validate→再生成ループ**: 生成能力の底上げ効果検証

---

## 1. 先行研究サマリ（評価観点の根拠）

### 要件品質の基準
国際標準 ISO/IEC/IEEE 29148 は「良い要件」の特性（正確・一義・完全・一貫・検証可能など）を規定  
参考: [IEEE Xplore](https://ieeexplore.ieee.org/document/9944698)

### EARSテンプレート
EARS（Easy Approach to Requirements Syntax）は自然文要件を軽く制約し、曖昧さを低減する書式。準拠率は形式適合の客観指標として利用可能  
参考: [IEEE Xplore](https://ieeexplore.ieee.org/document/7092950)

### 曖昧さ/匂い検出
QuARSやRequirements Smellsの研究では曖昧語や弱い表現の自動検出に基づく品質評価が提案されている  
参考: [IEEE Xplore](https://ieeexplore.ieee.org/document/8588475), [Springer](https://link.springer.com/chapter/10.1007/978-3-030-30446-1_5)

### Clarify-firstの効果
質問の期待価値（EVPI）を計算し、どの質問が改善を最大化するかを評価する手法が提案されている  
参考: [arXiv](https://arxiv.org/abs/2305.19918)

### Validate→再生成ループ
自己フィードバックや再生成（Self-Refine, Reflexion）は多様なタスクで精度向上を示している  
参考: [arXiv](https://arxiv.org/abs/2303.17651), [arXiv](https://arxiv.org/abs/2303.11366)

## 2. 評価したい効果の定義（仮説）

### H1: Clarify-first
聞き返しありは、なしに比べ以下の改善が期待される：
- EARS準拠率 ↑
- 曖昧語/匂い ↓
- 非機能要件・用語集・制約・KPIの網羅率 ↑
- 下流（設計/コード生成）成功率 ↑

### H2: Validate→再生成
再生成ループは、単発生成に比べ以下の改善が期待される：
- EARS準拠率・匂いスコア改善
- テスト/ビルドの通過率 ↑
- 人手修正コスト ↓

## 3. 実験デザイン（再現可能・反事実比較）

### 3.1 因子計画（2×2要因計画）

- **因子A**: Clarify-first（ON/OFF）
- **因子B**: Validate→再生成（ON/OFF, 最大3ループ）

4条件をランダム割付し、各お題について独立実行。主効果と交互作用を推定。

### 3.2 データセット

- **お題**: 30〜100件、分野・粒度を層化
- **回答**: clarify回答セットを標準化
- **金標**: 専門家が作成したEARS準拠 requirements.md  
  （ISO/IEC/IEEE 29148を参照: [IEEE Xplore](https://ieeexplore.ieee.org/document/9944698)）

### 3.3 サンプルサイズ

準拠率0.60→0.75を検出（α=0.05, 力0.8, 2群）するには各群約152試行が必要。繰り返し実行で補完。

## 4. 主要指標（自動+人手の両輪）

### 4.1 構造適合

- **EARS準拠率**: パターン（Ubiquitous/Event-Driven/State-Driven/Optional/Unwanted）への形式マッチ割合  
  参考: [IEEE Xplore](https://ieeexplore.ieee.org/document/7092950)
- **章立て網羅率**: requirements.md の所定セクション有無＋空要素率

### 4.2 言語品質

- **曖昧語密度**: QuARS辞書で検出件数/1000語  
  参考: [IEEE Xplore](https://ieeexplore.ieee.org/document/8588475)
- **ISO特性の近似**: 29148準拠の一義性/検証可能性を自動判定

### 4.3 下流影響

- **設計/コード生成後の品質**: lint/型/最小テストの通過率、再生成回数
- **Self-Refine等の外的エビデンス**: 改善効果の確認  
  参考: [arXiv](https://arxiv.org/abs/2303.17651)

### 4.4 効率

- clarify回答に要した人手時間
- トークン数、実行時間、APIコスト、質問回数

### 4.5 Clarify-first固有

- **質問貢献度**: 質問後のEARS準拠率や匂い減少の改善量を計算し、EVPI近似でランキング  
  参考: [arXiv](https://arxiv.org/abs/2305.19918)

## 5. 統計計画

- **主指標**: EARS準拠率、匂い密度、下流成功率
- **モデル**: 混合効果モデル（お題IDをランダム効果）、固定効果=Clarify, Validate, 交互作用
- **多重比較補正**: Holm–Bonferroni
- **再現性対策**: 盲検評価、シード固定、温度固定、複数seed平均

## 6. Clarify-first改善の学術的アップデート方針

1. **質問発火のゲーティング**: EARS予測スコアや匂い密度が低い場合のみ質問を発火
2. **質問予算最適化**: EVPI近似で改善が見込める上位k問を選択  
   参考: [arXiv](https://arxiv.org/abs/2305.19918)
3. **質問テンプレ学習**: EARS欠落、非機能抜け、用語不整合ごとに定型質問を用意
4. **回答の取り込み**: 回答を即時反映→不足のみ再質問

## 7. Validate→再生成ループの学術的アップデート方針

1. **検証器の多面化**: EARS適合、匂い閾値、章立て網羅、トレーサビリティを合格ラインに設定
2. **自己フィードバック生成**: 失敗ログを箇条書き改善指示に変換し、次プロンプトへ差し戻し  
   参考: [arXiv](https://arxiv.org/abs/2303.11366)
3. **早期停止と冷却**: 同じ失敗を繰り返す場合はテンプレ切替やデコード多様化
4. **上限制御**: 3回で打ち切り、未達は人手レビューに回す

## 8. 具体的な主要メトリクス定義

- **EARS準拠率** = EARSパターン一致要件数/機能要件総数
- **匂い密度** = 曖昧語・助動詞誤用などの検出件数/1000語  
  参考: [IEEE Xplore](https://ieeexplore.ieee.org/document/8588475)
- **非機能網羅率** = ISO 29148に基づくNFRカテゴリのカバレッジ  
  参考: [IEEE Xplore](https://ieeexplore.ieee.org/document/9944698)
- **下流成功率** = lint/型/テスト/静的検査の通過割合
- **Clarify効果** = (clarifyあり−なし)/なし
- **Validate効果** = 初回と最終の差分
- **質問EVPI近似** = 質問後の期待スコア改善−質問前の期待値

## 9. 脅威と対策

- **データ漏洩**: お題はオリジナル中心。公開例題は変形
- **評価者バイアス**: 盲検化、複数評価者＋κ係数
- **モデル揺らぎ**: 温度/バージョン/seed固定、複数seed平均
- **汎化性**: ドメイン・難易度・言語で層化

---

# 最終版実装計画

## 全体アーキテクチャ（更新版）

```
wassden-mcp/
├── wassden/
│   ├── handlers/                     # 既存: requirements (includes completeness) / design / tasks
│   ├── lib/
│   │   ├── validate.py               # 入口: EARS/Smell/Structure/Trace を統合
│   │   ├── validate_ears.py          # ★EARSは初版Ubiquitousのみ
│   │   ├── smells/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # ISmellBackend 抽象化
│   │   │   ├── languagetool.py       # ★標準: LanguageTool バックエンド
│   │   │   └── adapters.md           # バックエンド選定と制約の技術ノート
│   │   ├── doc_structure.py          # 章立て網羅/空要素/Traceとの接続
│   │   ├── experiment.py             # 実験ランナー（★devエクストラ装着時のみ有効）
│   │   ├── metrics.py                # 指標スキーマ
│   │   ├── report.py                 # md/jsonレポート出力（★手動実行前提）
│   │   └── i18n.py
│   ├── tools/                        # MCPツール定義
│   │   └── definitions.py            # dev機能は★条件付き登録
│   ├── server.py
│   └── cli.py                        # devサブコマンドは★条件付き公開
├── experiments/                      # ★devパッケージにのみ同梱
│   ├── briefs/
│   └── gold/
├── docs/
│   ├── validation/ears.md
│   ├── validation/smells_backend.md  # ★LanguageTool統合ガイド
│   └── experiments/README.md         # ★手動実験ガイド
└── pyproject.toml                     # ★extras: dev を追加
```

---

## 1. インストールと機能ゲーティング（★devエクストラ）

- **既定（uvx経由）**: 本体機能のみ（プロンプト生成・通常検証・トレーサ）。コマンドは現行のまま維持  
  `uvx --from git+https://github.com/tokusumi/wassden-mcp wassden ...`

- **実験系**: Clarify/Validateループ、実験ランナー、メトリクス収集、レポート  
  `pip install "wassden[dev]"` の時だけ有効化。`pyproject.toml` に `extras.dev` として依存関係・エントリを定義  
  例：`pip install -U "wassden[dev]"`

### 実装ポイント

**pyproject.toml**
- `optional-dependencies.dev = ["language-tool-python>=2.8", "pandas", "rich", ...]`

**cli.py / tools/definitions.py**
- `importlib.metadata` で `wassden[dev]` の依存（例：`language_tool_python`）存在確認
- 存在しない場合：
  - dev系サブコマンド（`run-experiment`, `report-experiment`）を未登録（隠し）
  - MCPツールのdev機能も未公開

これにより **uvxの導入方法は変更しない** まま、実験機能は **devインストール時のみ** 露出。

---

## 2. Smell検出バックエンド（辞書自作をやめる）

### 既定バックエンド: LanguageTool

**Pythonラッパー**: `language-tool-python`  
多言語のスタイル/文法ルールに基づく検出が可能で、HTTP API/ローカルサーバの双方を利用可。日本語を含む多数言語をサポート（言語ごとのルール充実度は差あり）

- [PyPIパッケージ](https://pypi.org/project/language-tool-python/)
- [言語サポート状況](https://dev.languagetool.org/languages)
- [公式サイト](https://languagetool.org/)
- [HTTP APIドキュメント](https://languagetool.org/http-api/)

### 拡張候補（任意・後日検討）

**Paska**: 要件スメル検出＋改善提案の研究ツール（arXiv/IEEE TSE、コード配布あり）  
必要なら別プロセス連携の追加アダプタとして実装可能（多言語の実用性は要確認）

- [arXiv論文](https://arxiv.org/abs/2305.07097)
- [ACM Digital Library](https://dl.acm.org/doi/abs/10.1109/TSE.2024.3361033)
- [コード](https://figshare.com/articles/code/Paska_-_Automated_Smell_Detection_and_Recommendation_in_Natural_Language_Requirements/22731707)

### 備考

古典的なQuARS系は参考実装として文献リンクのみdocsに記載（直接統合はしない方針）
- [QuARS Tool](https://www.sei.cmu.edu/documents/754/2005_005_001_14603.pdf)
- [QuARS NLP](https://ceur-ws.org/Vol-2376/NLP4RE19_paper07.pdf)

### 実装詳細

**wassden/lib/smells/base.py**
```python
class ISmellBackend:
    def analyze(text: str, lang: str) -> SmellReport
```

**wassden/lib/smells/languagetool.py**
- `language_tool_python.LanguageToolPublicAPI` or local serverで`matches`を取得
- 「弱モダリティ/曖昧語/未定指示/定量基準欠如/禁止語」等にマップ変換（LTの`ruleId`や`category`を当社カテゴリへ正規化）
- **多言語対応**: `lang='ja'|'en'|auto`。auto時は簡易言語判定後にLTを切替

**docs/validation/smells_backend.md**
- LanguageToolのルールカバレッジと制約
- サーバ起動／API利用手順
- 速度チューニング（ローカルサーバ/バッチ処理の推奨）
  参考: [Stack Overflow](https://stackoverflow.com/questions/72500635/how-to-speed-up-language-tool-python-library-use-case)

これにより「辞書管理なし」で**多言語**のスメル検出を実装し、将来別バックエンド（例：Paska）を差し替え可能な形にします。

---

## 3. EARS準拠判定（初版は**Ubiquitous**のみに限定）

### ターゲット: Ubiquitous要件のみ

- **日本語例**: `システムは … すること。`
- **英語例**: `The system shall … .`

### 実装: `validate_ears.py`

- **抽出単位**: 「機能要件」セクション配下の箇条書き1行＝1要件（柔軟に前処理）
- **完全一致要件**: 述部終止/shallをチェック

### 出力例

```json
{
  "ears": {
    "pattern": "ubiquitous",
    "total": 24,
    "matched": 18,
    "rate": 0.75,
    "violations": [
      {"line": 120, "reason": "missing shall/すること"},
      {"line": 138, "reason": "not starting with 'The system ...' / 'システムは'"}
    ]
  }
}
```

今回は **他のEARSパターン（Event/State/Optional/Unwanted）は未対応**。  
将来 `--ears=all` フラグで拡張予定という位置づけにドキュメント化。

---

## 4. 実験ランナー（dev限定・手動運用前提）

> 予算配慮により **CI連携は行わない**。実行は手動で都度回す運用に最適化。

### CLI

```
wassden run-experiment \
  --from user|requirements|design \
  --clarify on|off \
  --validate-loops 0..3 \
  --input path_or_text \
  --lang auto|ja|en \
  --seed 42 \
  --out-dir .wassden/experiments/2025-08-21T10-00-00 \
  [--gold requirements|design|tasks:path]    # 任意
```

### ふるまい

1. `--from` に応じて生成対象（requirements / design / tasks）を決定
2. Clarify-first `on` の時は**既存の質問テンプレ**（上限k件）で**一括質問→回答取り込み**
3. Validate→再生成は `--validate-loops N` 回まで。**合格ライン**（Ubi-EARS率 / Smell閾値 / 章立て空要素）を満たせば早期停止
4. **コスト記録**（時間/トークン）と**メトリクス**を `metrics.json`、最終成果物をmdに保存
5. **レポート**は `wassden report-experiment --run-dir ... --format md|json` で生成（棒グラフはテキスト表現）

---

## 5. バリデーション指標（更新）

### 主指標

- `ears_ubiquitous.rate`（準拠率・今回の唯一のEARS指標）
- `smell.per_1000w` と `smell.by_category`（LanguageTool結果のカテゴリ正規化）
- `downstream_proxy.success`（Trace整合などの疑似下流成功）

### 補助

- 章立て網羅率（NFR/用語/制約/KPI/受入基準）・空要素率
- 実行時間・トークン・APIコスト
- Clarify質問数・Validateループ回数

---

## 6. CLI / MCPツール公開範囲（更新）

### ベース（常時）

- `prompt-requirements` (includes completeness check) / `prompt-*` / `validate-requirements|design|tasks` / `get-traceability` / `analyze-changes` …（現行通り）

### dev（`wassden[dev]`導入時のみ）

- `run-experiment`（3段の因子実験）
- `report-experiment`（集計と可視化）

MCPの `tools/definitions.py` でも同様に、devバックエンドが見つからない場合は**未登録**にしてツールパレットに出さない。

---

## 7. セキュリティと既定ふるまい（不変）

- **READ-ONLY**ポリシーは堅持。実験ランナーも**生成物はout-dirのみ**に保存
- 既定のユースケース（uvx経由）は**従来どおり安全運用**。dev機能は意図的にopt-in

---

## 8. ドキュメント（更新）

### README.md

- **インストール章**に「dev機能は `pip install "wassden[dev]"` でのみ有効」と明記（uvxの手順は現状維持）
- SmellバックエンドはLanguageToolを既定とし、API/ローカルの起動手順・利用制限を案内  
  言語サポート一覧とルール充実度の差について注記: [言語サポート状況](https://dev.languagetool.org/languages)

### docs/validation/smells_backend.md

- LanguageToolのセットアップ（Pythonラッパー／HTTP API）と運用Tips  
  - [PyPIパッケージ](https://pypi.org/project/language-tool-python/)
  - [HTTP API](https://languagetool.org/http-api/)
  - [高速化Tips](https://stackoverflow.com/questions/72500635/how-to-speed-up-language-tool-python-library-use-case)
- 参考研究（Paska/TSE 2024）リンクを付記し、将来アダプタとしての位置づけを説明  
  [ACM Digital Library](https://dl.acm.org/doi/abs/10.1109/TSE.2024.3361033)

### docs/validation/ears.md

- 初版は**Ubiquitousのみ**対応、書式例（ja/en）と違反理由の定義を簡潔に記載

### docs/experiments/README.md

- 手動実行のガイド（因子指定、seed固定、成果物の読み方）

---

## 9. 既存機能との整合

- 既存のトレーサビリティ・プロンプト群・MCPツールは**非変更**
- **Smell検出が辞書方式から外部ライブラリ方式へ**切り替わるのみ（内部の標準カテゴリに正規化）
- EARSは**Ubiquitous限定**で軽量・堅牢に。拡張は将来版へ

---

## まとめ

この計画により：

- **導入手順（uvx）は現状維持**
- 実験系は **`pip install "wassden[dev]"`の明示opt-in** でのみ有効
- **Smellは外部ライブラリ（LanguageTool）** に統一
- **EARSはUbiquitous限定** でシンプルに開始
- **CI依存は廃し手動運用** に最適化

という4点の要望をすべて満たす実装となります。