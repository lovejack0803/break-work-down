# 収集データの保存・読み込み・差分検出

MCP連携・ブラウザ履歴・Browser Useを問わず、収集したデータはすべて `data/` ディレクトリに保存し、次回実行時に再利用する。

---

## 保存先

```
data/
├── config.json                  ← ユーザー設定
├── collection_YYYY-MM-DD.json   ← 日付入りスナップショット（毎回作成）
└── latest.json                  ← 最新データで常に上書き（クイックアクセス用）
```

## JSONの構造

```json
{
  "collected_at": "2026-03-16T10:30:00+09:00",
  "sources": ["slack", "browser_chrome", "browser_use_kintone"],
  "analysis_scope": "individual",
  "budget_constraint": "zero",
  "organization_type": "npo",
  "user_profile": { "name": "...", "title": "...", "department": "...", "email": "..." },
  "estimated_tasks": [
    { "name": "受注処理・顧客対応", "frequency": "毎日", "peak_period": "", "source": "Slack報告、CRM履歴", "details": "..." }
  ],
  "tool_environment": [
    { "name": "Salesforce", "category": "CRM", "source": "browser_chrome" }
  ]
}
// analysis_scope: "individual" | "team" | "project"
// budget_constraint: "zero" | "low" | "high" | "undecided"
// organization_type: "" | "npo" | "public" | "enterprise" | "startup" | "freelance"
// peak_period: 年度末・月末等のピーク時期（空なら通年定常）
// その他のフィールドは収集状況に応じて自由に追加する
```

収集データがゼロ（MCP接続なし、ブラウザ履歴に業務関連なし）の場合でも、config.jsonとlatest.jsonは作成する。estimated_tasksをヒアリング結果から構築し、sourceを `"hearing"` として記録する。

## 保存・読み込み・差分検出（スクリプト実行）

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

## 差分検出が返す内容

- 新しく使い始めたツール / 使わなくなったツール
- アクセス頻度が大きく変わったツール（有意な変化）
- 業務一覧の増減
- 前回の `confirmed_question`（前回はどの問いを解こうとしていたか）

差分があれば「前回（○月○日）からの変化」としてユーザーに提示し、仮説構築の材料にする。
