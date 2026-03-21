# ブラウザ履歴収集

ブラウザ履歴はローカルの履歴DBから直接取得する。日常的に使うWebツールのアクセス頻度から業務パターンを推定できる。

---

## ブラウザの選択

Step 1bの許可質問で、どのブラウザの履歴を参照するかをユーザーに確認する。`config.json` の `browser` に設定済みなら質問をスキップする。

| 選択肢 | 説明 |
|---|---|
| **Chrome** | Chromeのみ参照 |
| **Edge** | Edgeのみ参照 |
| **両方** | Chrome・Edge両方を参照（情報量が最大） |
| **参照しない** | ブラウザ履歴の収集をスキップ |

ユーザーの回答を `config.json` の `browser` に保存する（`"chrome"` / `"edge"` / `"both"` / `"none"`）。

## スクリプト実行

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

## プライバシーへの配慮

- ブラウザ履歴の生URLは保存しない。ドメイン＋カテゴリ＋アクセス回数のみ保存

---

## ハマりどころ

### 1. 収集データの解釈の精度

ブラウザ履歴で「Salesforce 200回/月」と出ても、200回すべてが受注処理とは限らない（ダッシュボード確認、レポート閲覧等も含む）。アクセス回数は「その業務ツールをどれだけ使っているか」の指標であり、「その業務にどれだけ時間がかかっているか」の直接指標ではない。時間の推定にはヒアリングでの補完が必要。
