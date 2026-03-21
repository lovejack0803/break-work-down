# break-work-down

現場の業務を分析し、効率化・自動化の改善を提案する Plugin です。

Slack・ブラウザ履歴・Google Workspace・Notion 等と連携して業務データを自動収集し、タスクレベルの具体的な改善提案を行います。

## 特徴

- **仮説駆動の自動データ収集** — MCP サーバー経由で Slack / Google Workspace / Notion / ブラウザ履歴などから業務データを収集
- **タスクレベルの粒度** — 「営業業務を効率化」ではなく「CRM への手入力 30 分/日 → API 連携で自動化」のように具体的に提案
- **目的起点の分析** — 作業の「目的」を問い直し、🗑️ 廃止 / 📉 簡素化 / 🔄 手段変更 / 🔧 自動化 の 4 分類で整理
- **並列サブエージェント** — ツール調査・AI 活用調査・スキル検索を並列実行し、最適な改善手段を提案
- **HTML レポート出力** — Before / After 比較付きの視覚的なレポートを自動生成

## デモ

[![デモ動画](https://img.shields.io/badge/Demo-YouTube-red)](https://youtube.com/watch?v=XXXXXXXXXXXX)

<!-- TODO: デモ動画の URL を差し替えてください -->

**レポート出力例:**

![レポートスクリーンショット](docs/screenshot-report.png)

<!-- TODO: スクリーンショット画像を docs/screenshot-report.png に配置してください -->

## インストール

Claude Code で以下の 2 ステップを実行してください:

```
/plugin marketplace add lovejack0803/break-work-down
/plugin install break-work-down@break-work-down
```

## 使い方

Claude Code のチャットで以下のように話しかけてください:

```
業務を分析して改善提案をしてほしい
```

プラグインが自動的に以下のワークフローを実行します:

1. **初期化** — 設定の読み込み・前回データの引き継ぎ
2. **自動収集** — 利用可能な MCP ツールを検出し、許可を得たうえでデータ収集
3. **業務マッピング** — 収集データからタスク一覧・ボトルネック仮説を作成
4. **ギャップ補完ヒアリング** — データ不足の箇所のみユーザーに質問
5. **分析** — 各業務の目的・手段を評価し 4 分類に整理
6. **改善手段リサーチ** — ツール / AI / スキルの 3 軸で並列調査
7. **レポート出力** — 優先順位付き HTML レポートを生成

## 対応ツール

| ツール | MCP パターン | 収集内容 |
|--------|-------------|---------|
| Slack | `slack_*` | チャンネル分析・メッセージパターン |
| Google Workspace | `google_*` | Drive / Calendar / Docs / Sheets |
| Notion | `notion_*` | ページ・データベース・ワークフロー |
| Telegram | `telegram_*` | グループメッセージ・レポートパターン |
| Discord | `discord_*` | チャンネルメッセージ・サポートパターン |
| ブラウザ履歴 | ローカル | Chrome / Edge の Web ツール利用状況 |
| Browser Use | `browser-use` CLI | MCP 非対応 Web アプリの画面情報 |

## プロジェクト構成

```
plugins/break-work-down/
├── .claude-plugin/
│   └── plugin.json          # プラグイン定義
└── skills/break-work-down/
    ├── SKILL.md             # メインスキル定義
    ├── data/
    │   └── config.json      # 永続設定
    ├── analyze/             # 分析フレームワーク・ヒアリングフロー
    ├── collect/             # MCP ツール連携・ブラウザ履歴・Browser Use
    ├── propose/             # 改善提案 (ツール / AI / スキル検索)
    ├── report/              # HTML レポートテンプレート
    └── scripts/             # Python ユーティリティ (履歴収集・データ保存)
```

## ライセンス

MIT