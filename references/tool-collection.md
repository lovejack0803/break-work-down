# ツール別自動収集手順

Step 1c で許可されたツールごとに実行する収集手順。

---

## ツール優先度の定義

業務内容の把握に使うツールは優先度で2段階に分類する。

### 優先ツール（業務内容把握向き） — 積極的に収集

| ツール | MCP識別パターン | 業務把握の価値 |
|---|---|---|
| **Slack** | `slack_*` ツール群 | 日常業務・依頼・報告の実態がリアルタイムで記録される |
| **Notion** | `notion_*` ツール群 / MCPリソース | 業務フロー・マニュアル・プロジェクト構造が可視化されている |
| **Google Drive** | `gdrive_*` / `google_drive_*` / Google関連リソース | ドキュメント・スプレッドシートに業務プロセスが記録されている |
| **Google Calendar** | `gcal_*` / `google_calendar_*` / Google関連リソース | 定例会議・業務の時間配分パターンが分かる |
| **ブラウザ履歴** | ローカルファイル（Chrome/Edge） | 日常的に使うWebツールのアクセス頻度から業務パターンを推定できる |

### 補助ツール — ユーザーが希望した場合のみ使用

| ツール | MCP識別パターン | 補助扱いの理由 |
|---|---|---|
| n8n / Zapier / Make | `n8n*` / `zapier*` / `make*` | 自動化設定の確認には使えるが、業務の実態把握には向かない |
| GitHub / GitLab | `github*` / `gitlab*` | 開発作業の記録はあるが、業務全体の把握には偏りが生じる |
| その他のMCP | 上記以外 | 業務内容把握との親和性を個別に判断 |

**Step 1b の許可質問には優先ツールのみ表示する。補助ツールは質問に含めず、ユーザーが「他のツールも見てほしい」と明示した場合のみ使用する。**

---

## 接続方法の共通原則

各優先ツールには複数の接続方法がある。Step 1b でユーザーに**どの方法で接続するか**を選んでもらう。MCPが検出済みならそれを使い、未検出なら代替手段を提示する。「後で接続する」も常に選択肢に含める。

---

## Slack

Slackは業務の実態が最も生々しく記録される場所。

### 接続方法

| 方法 | セットアップ | 読める情報 |
|------|-------------|-----------|
| **A. 公式MCP（推奨）** | `claude plugin install slack` → OAuth認証 | メッセージ検索、チャンネル履歴、ユーザー情報、ファイル |
| **B. スクリプト（Bot Token）** | Slack App作成 → Bot Token取得 → スクリプト実行 | チャンネル履歴、ユーザー情報（※検索APIはBot Tokenでは使えない） |
| **C. 後で接続する** | — | スキップ。ブラウザ履歴等の他ソースで業務を推定 |

**方法A: 公式 Slack MCP（推奨）**

Slack公式のMCPサーバー（`https://mcp.slack.com/mcp`）。OAuth認証で簡単に接続できる。

セットアップ: `claude plugin install slack` を実行し、ブラウザでOAuth認証するだけ。
**注意**: プラグインインストール後、MCPツールがセッションに反映されるまでClaude Codeの再起動が必要な場合がある。インストール直後にSlackツールが使えない場合は、先にブラウザ履歴等の他ソースで収集を進め、次回セッションでSlack収集を実行する。

```
収集手順:
① メッセージ検索で直近2週間のユーザー発言を取得
② 主要チャンネル（3-5件）の直近の会話を取得
③ ユーザープロフィール（役職・部署）を取得
④ ファイル共有パターンを確認
```

**方法B: スクリプト経由（Bot Token）**

MCPが使えない場合、Bot TokenがあればWeb APIで直接収集できる。

```bash
PYTHONUTF8=1 python "<skill-base-dir>/scripts/collect_slack.py" --token xoxb-YOUR-TOKEN --days 14 --limit 5
```

Bot Token の取得手順（ユーザーにテキストで案内）:
1. https://api.slack.com/apps →「Create New App」→「From scratch」
2. 「OAuth & Permissions」→ Bot Token Scopes: `channels:read`, `channels:history`, `groups:read`, `groups:history`, `users:read`
3. 「Install to Workspace」→ `xoxb-...` トークンをコピー

---

## Notion

業務フロー・マニュアル・プロジェクト構造がNotionに記録されていることが多い。

### 接続方法

| 方法 | セットアップ | 読める情報 |
|------|-------------|-----------|
| **A. 公式MCP（推奨）** | Integration Token取得 → MCP設定 | ページ、データベース、コメント |
| **B. Claude Code Notionプラグイン** | `claude plugin install notion` | 同上 + スラッシュコマンド |
| **C. スクリプト（Integration Token）** | Integration Token取得 → スクリプト実行 | ページ、データベース（MCP不要） |
| **D. 後で接続する** | — | スキップ |

**方法A: 公式 Notion MCP（`@notionhq/notion-mcp-server`）**

Notion公式のMCPサーバー。Integration Tokenが必要。

セットアップ:
1. https://www.notion.so/profile/integrations → 新しいインテグレーション作成
2. トークン（`ntn_...`）をコピー
3. 対象ページ/データベースをインテグレーションに共有（ページメニュー →「接続を追加」）
4. Claude Code で MCP 設定:
   ```
   claude mcp add notion -- npx -y @notionhq/notion-mcp-server
   ```
   環境変数 `NOTION_TOKEN` にトークンを設定

```
収集手順:
① ワークスペースのページ構造を取得
② 最近更新されたページ（上位10件）の内容を読む
③ データベースがあればスキーマと直近のエントリを確認
④ 業務フロー・マニュアル・議事録を特定
```

**方法B: Claude Code Notionプラグイン**

`claude plugin install notion` で導入可能。MCP + スラッシュコマンドがセットで使える。OAuth認証対応。

**方法C: スクリプト経由（Integration Token）**

MCPが使えない場合、Integration TokenがあればREST APIで直接収集できる。

```bash
PYTHONUTF8=1 python "<skill-base-dir>/scripts/collect_notion.py" --token ntn_YOUR_TOKEN --limit 20
```

オプション:
- `--include-content`: 上位5ページの内容サマリを取得（API呼び出し増加）
- `--include-entries`: データベースの直近エントリを取得（API呼び出し増加）

Integration Token の取得手順（ユーザーにテキストで案内）:
1. https://www.notion.so/profile/integrations →「新しいインテグレーション」
2. トークン（`ntn_...`）をコピー
3. 対象ページのメニュー →「接続を追加」→ 作成したインテグレーションを選択

---

## Google Workspace（Drive + Calendar）

ドキュメント・スプレッドシートの業務プロセスと、カレンダーの会議パターンから業務構造を把握する。

### 接続方法

| 方法 | セットアップ | 読める情報 |
|------|-------------|-----------|
| **A. 公式 gws CLI MCP（推奨）** | Google Cloud OAuth設定 → `gws mcp` 起動 | Drive, Calendar, Sheets, Docs, Gmail 等 |
| **B. コミュニティMCP** | OAuth設定 → MCP設定 | Drive, Calendar（パッケージによる） |
| **C. スクリプト（Access Token）** | Access Token取得 → スクリプト実行 | Drive, Calendar（MCP不要） |
| **D. 後で接続する** | — | スキップ |

**方法A: Google 公式 Workspace CLI（`@googleworkspace/cli`）**

Google公式のCLI。Drive, Calendar, Sheets, Docs, Gmail 等を一括カバー。

セットアップ:
1. Google Cloud Console でOAuthデスクトップアプリ認証情報を作成
2. `claude mcp add google-workspace -- npx -y @googleworkspace/cli mcp`
3. 初回実行時にブラウザでOAuth認証

**方法B: コミュニティMCP**

`@aaronsb/google-workspace-mcp`（軽量、Drive+Calendar+Gmail）や `google_workspace_mcp`（12サービス対応）など。

**方法C: スクリプト経由（Access Token）**

MCPが使えない場合、OAuth Access TokenがあればREST APIで直接収集できる。

```bash
PYTHONUTF8=1 python "<skill-base-dir>/scripts/collect_google_workspace.py" --token ya29.ACCESS_TOKEN --days 14
```

オプション:
- `--skip-drive`: Drive収集をスキップ
- `--skip-calendar`: Calendar収集をスキップ
- `--drive-limit N`: Drive取得件数上限（デフォルト: 20）
- `--cal-limit N`: Calendar取得件数上限（デフォルト: 50）

Access Token の取得手順（ユーザーにテキストで案内）:
- 方法1: `gcloud auth application-default print-access-token`（gcloud CLI導入済みの場合）
- 方法2: https://developers.google.com/oauthplayground/ でスコープ `drive.readonly` + `calendar.readonly` を選択し、トークンを取得

### Drive の収集手順

```
① ファイル一覧を取得（最近更新されたもの上位20件）
   → ファイル名・更新日時・種類を確認

② タイトルから業務カテゴリを推定:
   - 「進捗管理」「報告書」「議事録」→ プロジェクト管理系
   - 「マニュアル」「手順書」→ 定型業務の存在を示唆
   - 「集計」「分析」「売上」→ データ集計・レポート系

③ 頻繁に更新されているファイル（週1以上）を3-5件読み込む

収集する情報: ファイル名・更新頻度・種類・内容の要約
保存しない情報: ファイル全文・個人情報・財務データの詳細
```

### Calendar の収集手順

```
① 直近2週間〜1ヶ月のイベント一覧を取得

② 定例パターンを分類:
   - 毎日 → 朝会、報告等
   - 毎週 → 週次MTG、振り返り等
   - 参加人数が多い → 横断的な共有・意思決定

③ 会議の時間帯から推定:
   - 午前に集中 → 午後が作業時間
   - 「準備」「レビュー」が多い → 事前準備コストが高い

収集する情報: タイトル・参加者数・頻度・所要時間
保存しない情報: プライベートな予定の詳細
```

---

## ブラウザ履歴（スクリプト実行）

ブラウザ履歴は常にローカルスクリプトで収集する（MCP不要）。

```bash
PYTHONUTF8=1 python "<skill-base-dir>/scripts/collect_browser_history.py" --days 14 --limit 50
```

スクリプトが行うこと:
1. Chrome/Edgeの履歴DBを自動検出
2. SQLite backup APIで一時コピー（ブラウザ起動中のロック回避）
3. 直近N日間のアクセス頻度上位を取得
4. ドメイン別にグルーピング、業務ツール/プライベートを自動分類
5. プライベートサイトを除外し、業務関連のみJSON出力

**注意**: Windows環境では `PYTHONUTF8=1` を必ず付ける。

---

## 収集データの保存

収集したデータはスキルの `data/` ディレクトリに保存し、次回実行時に再利用する。

### 保存先

```
<skill-base-dir>/data/
├── collection_YYYY-MM-DD.json   ← 日付入りスナップショット（毎回作成）
└── latest.json                  ← 最新データで常に上書き（クイックアクセス用）
```

### JSONの構造

```json
{
  "collected_at": "2026-03-16T10:30:00+09:00",
  "sources": ["slack", "browser_chrome"],
  "user_profile": {
    "name": "...",
    "title": "...",
    "department": "...",
    "email": "..."
  },
  "estimated_tasks": [
    {
      "name": "受注処理・顧客対応",
      "frequency": "毎日",
      "source": "Slack報告、CRM履歴",
      "details": "受注データ入力、問い合わせ対応、見積作成"
    }
  ],
  "tool_environment": [
    {
      "name": "Salesforce",
      "category": "CRM",
      "source": "browser_chrome",
      "access_count": 250,
      "url_pattern": "*.salesforce.com"
    }
  ],
  "channels": [
    {
      "id": "C01EXAMPLE",
      "name": "営業チーム",
      "relevance": "主要業務チャンネル"
    }
  ],
  "browser_top_domains": [
    {
      "domain": "company.salesforce.com",
      "total_visits": 250,
      "category": "CRM"
    }
  ],
  "hearing_results": {
    "constraints": ["ITスキルが低め", "予算が限られている"],
    "pain_points": ["受注処理・顧客対応", "月次レポート作成"],
    "time_estimate": "1日の半分以上"
  },
  "hypothesis": "受注データの入力がCRMとスプレッドシートで二重管理になっており、1日3時間以上のボトルネックになっている",
  "confirmed_question": "毎日3時間以上を受注データの転記・集計・レポート作成に費やしている。特にCRMとスプレッドシート間の二重入力と、月次レポートのための手動集計が重い"
}
```

### 保存・読み込み・差分検出（スクリプト実行）

`scripts/save_collection_data.py` を使用する:

```bash
# 保存（Step 1e完了時、Step 3完了時に追記データで再実行）
echo '<収集データJSON>' | PYTHONUTF8=1 python "<skill-base-dir>/scripts/save_collection_data.py" save

# 前回データの読み込み（Step 1d）
PYTHONUTF8=1 python "<skill-base-dir>/scripts/save_collection_data.py" load

# 差分検出（2回目以降、新データとlatest.jsonを比較）
echo '<新しい収集データJSON>' | PYTHONUTF8=1 python "<skill-base-dir>/scripts/save_collection_data.py" diff
```

差分検出が返す内容:
- 新しく使い始めたツール / 使わなくなったツール
- アクセス頻度が大きく変わったツール（±50%以上の変化）
- 業務一覧の増減
- 前回の `confirmed_question`（前回はどの問いを解こうとしていたか）

差分があれば「前回（○月○日）からの変化」としてユーザーに提示し、仮説構築の材料にする。

### プライバシーへの配慮

- ブラウザ履歴の生URLは保存しない。ドメイン＋カテゴリ＋アクセス回数のみ保存
- 外部ツール（Slack・Discord等）から取得したメッセージの本文は保存しない。チャンネル名＋業務パターンの要約のみ
- ユーザーが明示的に削除を依頼した場合は `data/` ごと削除する
