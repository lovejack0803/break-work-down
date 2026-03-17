# ツール別自動収集手順

Step 1c で許可されたツールごとに実行する収集手順。

---

## Slack（MCP: `slack_*` ツール群）

Slackは業務の実態が最も生々しく記録される場所。

```
① slack_read_user_profile（user_id未指定 = 自分自身）
   → 役職、部署、タイムゾーンを把握

② slack_search_channels でユーザーの名前・部署に関連するチャンネルを検索
   → 業務に関わるチャンネルを特定

③ slack_read_channel で主要チャンネルの直近の会話を取得（3-5チャンネル）
   → 話題の頻出パターン、依頼・報告の流れを分析

④ slack_search_public / slack_search_public_and_private で:
   - from:ユーザーID で直近2週間の発言を検索
   - "依頼", "確認", "報告", "議事録", "レポート" などのキーワードで検索
   → ユーザーの業務パターンを把握

⑤ slack_search_public で content_types="files" を指定
   → 共有ファイルの種類から業務内容を推定
```

## Discord（MCP: `discord_*` ツール群）

Slackと同様のアプローチ。チャンネル一覧 → 最近のメッセージ → ユーザーの発言パターンの順で収集。

## Google Drive / Google Sheets（MCPリソース or 専用ツール）

```
- ListMcpResourcesTool で Google 関連リソースを取得
- ReadMcpResourceTool で最近更新されたファイル一覧を取得
- 業務に関連しそうなドキュメント・スプレッドシートの内容を読む
```

## Notion（MCP: `notion_*` ツール群 or MCPリソース）

```
- ページ構造・データベース一覧を取得
- 最近更新されたページの内容を読む
- ワークスペースの全体像から業務構造を把握
```

## ブラウザ履歴（スクリプト実行）

ブラウザ履歴から、ユーザーが日常的にアクセスしているWebサービス・ツールを特定できる。

**スクリプトで実行する**（インラインPython/sqlite3は使わない）:

```bash
PYTHONUTF8=1 python "<skill-base-dir>/scripts/collect_browser_history.py" --days 14 --limit 50
```

スクリプトが自動で行うこと:
1. Chrome/Edgeの履歴DBを自動検出
2. DBを一時ファイルにコピー（ブラウザ起動中のロック回避）
3. 直近N日間のアクセス頻度上位を取得
4. ドメイン別にグルーピングし、業務ツール/プライベートを自動分類
5. プライベートなサイトを除外し、業務関連のみJSON出力
6. 一時ファイルを自動削除

出力はJSON形式で `domains` 配列にドメイン・アクセス回数・カテゴリが含まれる。

**注意**: Windows環境では `PYTHONUTF8=1` を必ず付ける（cp932エンコーディングエラー回避）。

## カレンダー / メール / タスク管理（MCPリソースがあれば）

```
- 定例会議のパターン、頻度、参加者
- メールの送受信パターン
- タスクの種類と状態
```

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
    "scale": "チーム全体",
    "constraints": ["ITスキルが低め", "予算が限られている"],
    "pain_points": ["受注処理・顧客対応", "月次レポート作成"],
    "time_estimate": "1日の半分以上"
  },
  "hypothesis": "受注データの入力がCRMとスプレッドシートで二重管理になっており、5名×3時間/日のボトルネックになっている",
  "confirmed_question": "営業チーム5名が毎日3時間以上を受注データの転記・集計・レポート作成に費やしている。特にCRMとスプレッドシート間の二重入力と、月次レポートのための手動集計が重い"
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
