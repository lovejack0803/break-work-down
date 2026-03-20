# ローカル収集（ブラウザ履歴・データ保存）

MCP不要でローカルスクリプトを使って収集するデータソースと、収集データの保存・差分検出の手順。

---

## ブラウザ履歴

ブラウザ履歴はローカルの履歴DBから直接取得する。日常的に使うWebツールのアクセス頻度から業務パターンを推定できる。

### ブラウザの選択

Step 1bの許可質問で、どのブラウザの履歴を参照するかをユーザーに確認する。`config.json` の `browser` に設定済みなら質問をスキップする。

| 選択肢 | 説明 |
|---|---|
| **Chrome** | Chromeのみ参照 |
| **Edge** | Edgeのみ参照 |
| **両方** | Chrome・Edge両方を参照（情報量が最大） |
| **参照しない** | ブラウザ履歴の収集をスキップ |

ユーザーの回答を `config.json` の `browser` に保存する（`"chrome"` / `"edge"` / `"both"` / `"none"`）。

### スクリプト実行

```bash
# Chromeのみ
PYTHONUTF8=1 python "<skill-base-dir>/scripts/collect_browser_history.py" --browser chrome --days 14 --limit 50

# Edgeのみ
PYTHONUTF8=1 python "<skill-base-dir>/scripts/collect_browser_history.py" --browser edge --days 14 --limit 50

# 「両方」の場合は2回実行して結果をマージする
```

スクリプトが行うこと:
1. 指定ブラウザの履歴DBを検出
2. SQLite backup APIで一時コピー（ブラウザ起動中のロック回避）
3. 直近N日間のアクセス頻度上位を取得
4. ドメイン別にグルーピング、業務ツール/プライベートを自動分類
5. プライベートサイトを除外し、業務関連のみJSON出力

**注意**: Windows環境では `PYTHONUTF8=1` を必ず付ける。

### プライバシーへの配慮

- ブラウザ履歴の生URLは保存しない。ドメイン＋カテゴリ＋アクセス回数のみ保存

---

## 収集データの保存

MCP連携・ブラウザ履歴を問わず、収集したデータはすべて `data/` ディレクトリに保存し、次回実行時に再利用する。

### 保存先

```
data/
├── config.json                  ← ユーザー設定
├── collection_YYYY-MM-DD.json   ← 日付入りスナップショット（毎回作成）
└── latest.json                  ← 最新データで常に上書き（クイックアクセス用）
```

### JSONの構造

```json
{
  "collected_at": "2026-03-16T10:30:00+09:00",
  "sources": ["slack", "browser_chrome"],
  "user_profile": { "name": "...", "title": "...", "department": "...", "email": "..." },
  "estimated_tasks": [
    { "name": "受注処理・顧客対応", "frequency": "毎日", "source": "Slack報告、CRM履歴", "details": "..." }
  ],
  "tool_environment": [
    { "name": "Salesforce", "category": "CRM", "source": "browser_chrome" }
  ]
}
// その他のフィールドは収集状況に応じて自由に追加する
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

# 初期状態にリセット（config.jsonを初期化し、collection_*.json / latest.json を全削除）
PYTHONUTF8=1 python "<skill-base-dir>/scripts/save_collection_data.py" reset
```

差分検出が返す内容:
- 新しく使い始めたツール / 使わなくなったツール
- アクセス頻度が大きく変わったツール（有意な変化）
- 業務一覧の増減
- 前回の `confirmed_question`（前回はどの問いを解こうとしていたか）

差分があれば「前回（○月○日）からの変化」としてユーザーに提示し、仮説構築の材料にする。

---

## ハマりどころ

### 1. 収集データの解釈の精度

ブラウザ履歴で「Salesforce 200回/月」と出ても、200回すべてが受注処理とは限らない（ダッシュボード確認、レポート閲覧等も含む）。アクセス回数は「その業務ツールをどれだけ使っているか」の指標であり、「その業務にどれだけ時間がかかっているか」の直接指標ではない。時間の推定にはヒアリングでの補完が必要。
