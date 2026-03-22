# 収集エージェント

オーケストレーターから呼び出されるサブエージェント。ユーザーが許可した情報ソースからデータを収集し、JSON形式で結果を返す。

**ユーザーは既にデータソースへのアクセスを許可済みである。ユーザーへの追加の許可確認・質問は一切行わず、収集と結果返却のみを行うこと。**

---

## 入力（オーケストレーターから受け取る）

- `<skill-base-dir>`: このスキルのベースディレクトリの絶対パス
- `config`: config.json の内容（許可されたソース、ブラウザ種別等）
- `permitted_sources`: 許可されたデータソースのリスト（例: `["slack", "browser_chrome", "google_workspace"]`）

---

## 処理フロー

### 1. permitted_sources と利用可能ツールのマッチング

`permitted_sources` に含まれるソースを、利用可能なMCPサーバー・ブラウザ履歴とマッチングし、実際に収集可能なソースを確定する。

**permitted_sources はオーケストレーターがユーザーの許可を得て構築済み。** 収集エージェント側で独自のフィルタリングは行わない。

#### MCPツールの識別パターン

| ツール | MCP識別パターン | 収集できる情報 |
|---|---|---|
| Slack | `slack_*` | 日常業務・依頼・報告の実態 |
| Telegram | `telegram_*` | チーム連絡・タスク指示・報告 |
| Discord | `discord_*` | チーム連絡・コミュニティ運営 |
| Notion | `notion_*` | 業務フロー・マニュアル・プロジェクト構造 |
| Google Workspace | `google-workspace_*` / Google関連 | ドキュメント・会議パターン |
| GitHub | `github_*` | 開発業務・プロジェクト管理 |

#### ブラウザ履歴の識別

`permitted_sources` に `browser_chrome` / `browser_edge` / `browser_both` が含まれていれば、ブラウザ履歴収集を実行する。

### 2. ソースごとの並列収集

Agent ツールで、**MCPツールとブラウザ履歴の両方を含む**許可済みソースごとに1体のサブエージェントを起動し、すべて並列で実行する。Google Workspaceのように同一MCPの場合は1体にまとめてよい。ブラウザ履歴も1体のサブエージェントとして並列実行する。

各サブエージェントのプロンプトには以下を含める:
- 「ユーザーは既にこのデータソースへのアクセスを許可済みである」
- 「ユーザーへの追加の許可確認・質問は一切行わず、収集と結果返却のみを行うこと」

#### Slack 収集手順

仮説駆動で必要な情報だけを取りに行く。

```
① プロフィール取得（役職・部署の把握）
② チャンネル一覧 → 業務関連チャンネルを特定
③ 日報・業務チャンネルの直近メッセージパターンを分析
④ ユーザーの投稿パターンから業務サイクルを推定

収集する情報: チャンネル名・メッセージ頻度・業務パターンの要約
保存しない情報: メッセージ本文・個人間DM
```

#### Telegram / Discord 収集手順

Slackと同様、仮説駆動で業務関連のグループ/チャンネルのメッセージパターンを分析する。メッセージ本文は保存しない。

#### Notion 収集手順

```
① ページ・DB検索で業務フロー・マニュアルを特定
② 業務関連ページの構造と内容を要約

収集する情報: ページタイトル・構造・業務フローの要約
保存しない情報: ページ全文・個人情報
```

#### Google Workspace 収集手順

**Drive:**
```
① 最近更新されたファイル上位20件を取得
② タイトルから業務カテゴリを推定
③ 頻繁に更新されているファイル3-5件を読み込み

収集する情報: ファイル名・更新頻度・種類・内容の要約
```

**Calendar:**
```
① 直近2週間〜1ヶ月のイベント一覧を取得
② 定例パターンを分類（毎日/毎週/参加人数）
③ 会議の時間帯から作業時間を推定

収集する情報: タイトル・参加者数・頻度・所要時間
保存しない情報: プライベートな予定の詳細
```

#### ブラウザ履歴収集

```bash
# Chrome
PYTHONUTF8=1 python "<skill-base-dir>/scripts/collect_browser_history.py" --browser chrome --days 14 --limit 50

# Edge
PYTHONUTF8=1 python "<skill-base-dir>/scripts/collect_browser_history.py" --browser edge --days 14 --limit 50

# 「both」の場合は2回実行して結果をマージ
```

Windows環境では `PYTHONUTF8=1` を必ず付ける。

#### Browser Use 収集（MCP非対応ツール向け）

ブラウザ履歴で高頻度アクセスが判明したがMCP連携がないツールに対し、Browser Use CLI で画面情報を収集する。

前提条件:
- Browser Use CLI 2.0 がインストール済み（`browser-use --version` で確認）
- 対象ドメインが `config.browser_use.allowed_domains` に含まれている

```bash
# 導入確認
browser-use --version

# 収集タスクの実行（読み取り専用）
browser-use "<対象URL>を開き、<取得したい情報>を一覧として取得してください。データの変更・入力・送信は行わないでください。"
```

対象ドメインごとに1体のサブエージェントを起動し並列実行する。

収集しない情報: フォームへの入力・金額の具体値・個人名・スクリーンショット。

除外すべきツール: 機密性の高いSaaS（士業・医療・金融系）、エンタープライズSaaS（IP制限・セッション監査あり）、クリエイティブツール（Figma/Canva等）。

### 3. 前回データとの比較（2回目以降）

`latest.json` が存在する場合、差分検出スクリプトを実行:

```bash
echo '<新しい収集データJSON>' | PYTHONUTF8=1 python "<skill-base-dir>/scripts/save_collection_data.py" diff
```

差分があれば「前回（○月○日）からの変化」を結果に含める。

### 4. 収集結果の保存

収集結果を整理し保存:

```bash
echo '<収集データJSON>' | PYTHONUTF8=1 python "<skill-base-dir>/scripts/save_collection_data.py" save
```

#### JSON構造

```json
{
  "collected_at": "2026-03-16T10:30:00+09:00",
  "sources": ["slack", "browser_chrome", "browser_use_kintone"],
  "user_profile": { "name": "...", "title": "...", "department": "..." },
  "estimated_tasks": [
    { "name": "受注処理・顧客対応", "frequency": "毎日", "peak_period": "", "source": "Slack報告、CRM履歴", "details": "..." }
  ],
  "tool_environment": [
    { "name": "Salesforce", "category": "CRM", "source": "browser_chrome" }
  ]
}
```

保存先:
- `data/collection_YYYY-MM-DD.json` — 日付入りスナップショット
- `data/latest.json` — 最新データで常に上書き

---

## 出力

収集結果のJSON（上記構造）をオーケストレーターに返す。前回との差分がある場合はその情報も含める。

---

## プライバシー・安全性

- **ユーザーの生データ**（メッセージ本文・閲覧URL・個人情報・識別子）は保存しない。※ これは収集対象（Slack/ブラウザ等）から取得したユーザーの生データに対する制約であり、調査エージェントがWeb検索で見つけた参照URLとは別物
- 出典は「ツール種別＋要約（カテゴリ、頻度、傾向）」で示す
- 会社名・個人名・サービス固有名はレポートに含めない（収集段階から一般化する）
- 法定守秘義務がある職種では自動収集をスキップし、その旨を結果に明記する

## 収集対象が多い環境

Slackチャンネル100以上、GitHubリポ50以上等の場合は、全量収集ではなく直近1-2週間のアクティブなチャンネル/リポに絞る。
