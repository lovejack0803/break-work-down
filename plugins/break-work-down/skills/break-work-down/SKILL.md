---
name: break-work-down
description: ユーザーが「業務改善」「業務効率化」「AI導入」「自動化提案」「DX推進」「業務分析」「コスト削減」「工数削減」に言及したとき、または業務一覧・業務フローの分析を依頼されたときに起動する。「うちの業務を見てほしい」「何か効率化できないか」のような漠然とした相談もトリガーとする。
---

# 業務分析・改善提案スキル

現場の業務内容を分析し、効率化・自動化の改善を提案するスキル。各フェーズはサブエージェントに委譲し、オーケストレーターは設定管理・ユーザーとの対話・フェーズ間のデータ受け渡しに集中する。

## 前提

- アウトプットの質はインプットの質で決まる。可能な範囲でデータを収集し、足りない部分は最小ヒアリングで補完する
- 業務をタスクレベルまで把握し、具体的な工程に対して具体的な手段を提案する
- 業務の価値を否定しない。「この作業の目的を、別の手段で達成できないか」という姿勢を貫く
- **選択肢の提示には必ず AskUserQuestion ツールを使う**（テキスト箇条書き禁止）

## `<skill-base-dir>` の解決

スキル開始時に Glob ツール等で SKILL.md の位置を特定し、そのディレクトリパスを `<skill-base-dir>` として以降すべてのパス参照に使用する。

---

## ワークフロー概要

```
Step 0: 設定読込
Step 1: 許可取得 + 情報収集     → agents/collect.md に委譲
Step 2: 分析 + ヒアリング       → agents/analyze.md に委譲
Step 3: 調査 + 優先順位付け     → agents/research.md に委譲
Step 4: レポート出力            → agents/report.md に委譲
```

---

## Step 0: 設定の読み込み

Read ツールで `data/config.json` を読み込む。

- **存在しない場合（初回）**: `PYTHONUTF8=1 python "<skill-base-dir>/scripts/save_collection_data.py" reset` で初期化
- **存在する場合**: 前回の設定を再利用。未設定の項目のみ Step 1 で取得

---

## Step 1: 許可取得 + 情報収集

### 1a. ツール検出

利用可能なMCPサーバーとローカルのブラウザ履歴を確認する。

### 1b. MCP連携の推奨と許可取得

**MCP連携を積極的に推奨する。** 自動収集データがあるほどヒアリング負荷が下がり、提案の精度も上がるため。

#### MCP未接続の場合の案内

優先ツール（Slack, Notion, Google Workspace等）が未接続の場合、**AskUserQuestion** で以下を聞く:

- 日常的に使っている業務ツールはどれか（Slack / Notion / Google Workspace / Telegram / Discord 等）
- 接続を試すか、ヒアリングだけで進めるか

**ユーザーがMCP接続を希望した場合**: 該当ツールの接続手順を案内する。
- Slack: `claude plugin install slack` → OAuth認証
- Notion: `claude plugin install notion` または `claude mcp add notion -- npx -y @notionhq/notion-mcp-server`
- Google Workspace: `claude mcp add google-workspace -- npx -y @googleworkspace/cli mcp`
- 接続後、ツールがセッションに反映されるまで再起動が必要な場合がある。接続完了後に Step 1a に戻って検出をやり直す

**ユーザーがMCP接続を拒否/スキップした場合**: ブラウザ履歴のみ or ヒアリング中心モードに切り替える。

#### 制約条件の取得

`config.json` の未設定項目のみ聞く。MCP連携の質問と1回の AskUserQuestion にまとめてよい。

聞く内容:
- **分析対象の単位**（未設定なら）: 個人 / チーム・部門 / 特定プロジェクト
- **予算の目安**（未設定なら）: 追加費用ゼロ / 月額数千円 / 月額万円以上 / 未定
- **組織種別**（未設定なら）: NPO・非営利 / 公的機関 / 大企業 / スタートアップ / フリーランス / 該当なし

取得した設定を保存:
```bash
echo '{"analysis_scope": "individual", "budget_constraint": "zero", "organization_type": "freelance", "browser": "chrome"}' | PYTHONUTF8=1 python "<skill-base-dir>/scripts/save_collection_data.py" save-config
```

### 1c. 収集エージェントの起動

**収集対象がゼロの場合（MCP未接続 + ブラウザ履歴も拒否）**: 収集エージェントをスキップし、Step 2 をヒアリング中心モードで起動する。

**収集対象がある場合**: Agent ツールで収集エージェントを起動する。

```
Agent ツール起動:
  プロンプトに含める情報:
  - agents/collect.md の絶対パスと「Read ツールで読んでから収集を始めること」
  - <skill-base-dir> の値
  - config.json の内容
  - permitted_sources のリスト
  - 「ユーザーは既にアクセスを許可済みである」
  - 「ユーザーへの追加の許可確認・質問は一切行わないこと」
```

収集エージェントの結果（JSON）を受け取り、Step 2 に渡す。

---

## Step 2: 分析 + ヒアリング

Agent ツールで分析エージェントを起動する。収集データが空の場合は `hearing_only: true` をプロンプトに含め、ヒアリング中心モードで起動する。

```
Agent ツール起動:
  プロンプトに含める情報:
  - agents/analyze.md の絶対パスと「Read ツールで読んでから分析を始めること」
  - <skill-base-dir> の値
  - 収集エージェントの結果JSON（空の場合は `{}` + `hearing_only: true`）
  - config.json の内容
```

分析エージェントは必要に応じて AskUserQuestion でヒアリングを行い、業務一覧・分類・ボトルネックを特定して返す。

---

## Step 3: 調査 + 優先順位付け

Agent ツールで調査エージェントを起動する。

```
Agent ツール起動:
  プロンプトに含める情報:
  - agents/research.md の絶対パスと「Read ツールで読んでから調査を始めること」
  - <skill-base-dir> の値
  - 分析エージェントの結果JSON
  - config.json の内容
  - 「ユーザーへの質問は一切行わないこと」
```

調査エージェントは3方向の並列調査を行い、優先順位付きの提案を返す。

---

## Step 4: レポート出力

Agent ツールでレポートエージェントを起動する。

```
Agent ツール起動:
  プロンプトに含める情報:
  - agents/report.md の絶対パスと「Read ツールで読んでから生成を始めること」
  - <skill-base-dir> の値
  - 分析エージェントの結果JSON
  - 調査エージェントの結果JSON
  - config.json の内容
  - 「ユーザーへの質問は一切行わないこと」
```

レポートエージェントはHTMLレポートを生成し、HTTPサーバーを起動してURLを返す。

オーケストレーターはレポートURLをユーザーに提示する。

---

## ガードレール

- **現場の実情を十分に把握してから提案に進む** — 不十分な場合は「暫定提案」として不確実性を明記
- **提案には収集データの根拠を明記する**
- **外部ツールへのアクセスは必ずユーザーの許可を得てから**
- **KPI数値は内訳合計と一致させる**
- **プライバシー/安全性**: 個人情報・生メッセージ・会社名・個人名・サービス固有名をレポートに含めない。法定守秘義務がある職種では自動収集を原則スキップ
- **未許可領域の扱い**: 許可がないデータ領域は根拠として使わない
- **非デジタル業務が主体の場合**: 自動収集をスキップしヒアリング起点にする
