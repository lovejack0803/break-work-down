# HTMLレポート生成ガイド

## 概要

**単一の静的HTMLファイル**として出力する。React/ビルドツールは使わない。HTML + CSS + インラインスタイルのみで完結させる。

外部依存はGoogle Fontsのみ:
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
```

## 共通ベーススタイル（全パターン共通）

```css
body {
  font-family: 'Zen Kaku Gothic New', sans-serif;
  line-height: 1.9;      /* 1.7や1.75ではなく1.9 */
  font-weight: 400;
  overflow-x: hidden;
}

/* 見出し・数値 → Noto Serif JP */
/* 本文 → Zen Kaku Gothic New */
```

---

## レポート構成（全パターン共通）

ゴールは「読み手が3分で要点を掴み、最初の一歩を踏み出せる」こと。全業務を網羅的に並べるのではなく、**1位の提案に深掘り**する構成にする。

```
1. カバー（タイトル、対象バッジ、サブタイトル、日付）
2. 3分で読めるまとめ（KPIカード3〜4個。「なくせる業務」の数と削減時間を含む）
3. 業務トップ5（時間消費が多い順のテーブル）
4. 💡 業務削減提案（廃止・統合・頻度削減。ツール不要で実現できる改善）
5. 仕組み化候補トップ3（業務削減で対処できない残存業務。ステップカード形式）
6. 1位の深掘り（具体的な作業フロー、入力/出力、始め方の3ステップ）
7. 使用ツール（必要最小限のテーブル。コスト付き）
8. つまずきやすいポイント（よくある困りごと × 背景 × 回避策のテーブル）
9. [会社パターンのみ] ROI試算 / PoC計画 / Go/No-Go基準 / リスク評価
10. 次のアクション（今週中にやること3つ。業務削減アクションを最上位に）
```

**セクション4「業務削減提案」を目立たせる**: これがレポート最大のインパクトになることが多い。廃止・統合・頻度削減それぞれについて、対象業務・根拠・想定削減効果・段階的な進め方を示す。ツール導入不要でコストゼロの改善であることを強調する。

**個人パターン**: セクション8の後に「簡易代替案」を追加（メインツールが使えない場合の無料代替手段）
**チームパターン**: セクション8の後に「運用ルール例」を追加（やってOK/守ること + 迷ったときのフローチャート）
**会社パターン**: セクション6の後に「ROI試算」「導入ロードマップ」「PoC計画」「Go/No-Go判定基準」「リスクと対策」を追加

---

## CSSコンポーネント

### カバーセクション

カバーには `.cover-inner` ラッパーを入れて max-width を揃える。`::before` で装飾的なグラデーション円を入れ、`::after` で下部に3色ライン。

```css
.cover {
  padding: 80px 40px 70px;
  position: relative;
  overflow: hidden;
  animation: coverFade 0.8s ease-out;
}
.cover::before {
  content: '';
  position: absolute;
  top: -100px; right: -80px;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(accent1, 0.15) 0%, transparent 65%);
  pointer-events: none;
}
.cover::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent3));
}
.cover-inner {
  max-width: 880px;  /* 会社パターンは960px */
  margin: 0 auto;
  position: relative;
  z-index: 1;
}
.target-badge {
  display: inline-block;
  border: 1.5px solid;
  padding: 5px 22px;
  font-size: 0.82em;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 24px;
  font-weight: 500;
  animation: fadeUp 0.6s ease-out 0.2s both;
}
.cover h1 {
  font-family: 'Noto Serif JP', serif;
  font-size: 3em;
  font-weight: 900;
  letter-spacing: 0.05em;
  margin-bottom: 14px;
  animation: fadeUp 0.6s ease-out 0.35s both;
}
.cover .subtitle {
  font-size: 1.05em;
  font-weight: 400;
  line-height: 1.7;
  max-width: 520px;  /* チーム560px、会社640px */
  animation: fadeUp 0.6s ease-out 0.5s both;
}
.cover .meta {
  margin-top: 32px;
  font-size: 0.78em;
  letter-spacing: 1px;
  animation: fadeUp 0.6s ease-out 0.65s both;
}
```

### セクションヘッダー

セクション番号（大きな数字）とh2を**横並び（flex）**で表示し、下線を引く。これがレポート全体の視覚的リズムを作る。

```css
.section {
  margin: 56px 0;
  animation: fadeUp 0.5s ease-out both;
}
.section-header {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 28px;
  padding-bottom: 14px;
  border-bottom: 2px solid var(--ink);  /* パターンのメインテキスト色 */
}
.section-header .num {
  font-family: 'Noto Serif JP', serif;
  font-size: 2.2em;
  font-weight: 900;
  color: var(--accent1);  /* パターンのアクセント色 */
  line-height: 1;
}
.section-header h2 {
  font-family: 'Noto Serif JP', serif;
  font-size: 1.2em;
  font-weight: 700;
  letter-spacing: 0.02em;
}
```

HTMLの書き方:
```html
<div class="section">
  <div class="section-header">
    <div class="num">1</div>
    <h2>3分で読めるまとめ ― 何がどう楽になるか</h2>
  </div>
  <!-- セクション内容 -->
</div>
```

### フッター

全幅ダーク背景のフッター。

```css
.footer {
  background: var(--ink);
  color: rgba(255, 255, 255, 0.35);
  text-align: center;
  padding: 22px;
  margin-top: 60px;
  font-size: 0.78em;
  letter-spacing: 1.5px;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  box-sizing: border-box;
}
```

### KPIカード
```css
.kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.kpi-card {
  background: var(--paper);
  padding: 22px 16px;
  text-align: center;
  border: 1px solid var(--border);
  position: relative;
  overflow: hidden;
}
.kpi-card::before { /* 上部の色付きライン */
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.kpi-card .value {
  font-family: 'Noto Serif JP', serif;
  font-size: 1.8em;
  font-weight: 900;
}
```
チームと会社パターンは4カラム（`repeat(4, 1fr)`）にする。

### カード（共通）

```css
.card {
  background: var(--paper);
  border-radius: 2px;
  padding: 26px 28px;
  box-shadow: 0 1px 3px var(--shadow), 0 8px 24px rgba(ink, 0.04);
  margin-bottom: 18px;
  border: 1px solid var(--border);
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}
.card:hover {
  box-shadow: 0 2px 8px var(--shadow), 0 16px 40px rgba(ink, 0.08);
  transform: translateY(-2px);
}
```

### ステップカード（候補トップ3用）

ホバー時は横にスライドする。左ボーダーで色分け。

```css
.step-card {
  background: var(--paper);
  padding: 22px 26px;
  border: 1px solid var(--border);
  margin-bottom: 16px;
  display: flex;
  gap: 18px;
  align-items: flex-start;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.step-card:hover {
  transform: translateX(4px);
  box-shadow: -4px 0 12px rgba(ink, 0.06);
}
.step-num {
  font-family: 'Noto Serif JP', serif;
  font-size: 1.8em;
  font-weight: 900;
  line-height: 1;
  flex-shrink: 0;
  width: 44px;
  text-align: center;
}
```

色分け: 個人=peach/sage/plum、チーム=terracotta/gold/teal、会社=crimson/copper/navy-soft

### ハイライト・ヒント・アラート
```css
.highlight {
  background: var(--paper);
  border-left: 4px solid var(--accent1);
  padding: 20px 24px;
}
.tip {
  background: rgba(accent2, 0.06);
  border-left: 4px solid var(--accent2);
  padding: 16px 22px;
}
```

### ロードマップ（タイムライン）
```css
.roadmap { position: relative; padding-left: 44px; }
.roadmap::before { /* 縦線 */
  content: '';
  position: absolute; left: 16px; top: 8px; bottom: 8px;
  width: 2px; background: var(--ink);
}
.roadmap-item::before { /* 丸ドット */
  content: '';
  position: absolute; left: -36px; top: 8px;
  width: 12px; height: 12px;
  border: 2.5px solid var(--accent1);
  background: var(--bg);
}
```

### ネクストアクション
```css
.next-action {
  background: var(--ink);
  color: #fff;
  padding: 28px 32px;
  position: relative;
}
.next-action::before { /* 上部グラデーションライン */ }
.next-action li::before { content: '—'; color: var(--accent1); }
```

### テーブル
```css
table { width: 100%; border-collapse: collapse; font-size: 0.88em; table-layout: fixed; word-break: break-word; }
th { background: var(--ink); color: #fff; padding: 12px 14px; }
td { padding: 12px 14px; border-bottom: 1px solid var(--border); }
tr:nth-child(even) { background: rgba(bg, 0.6); }
```

### アニメーション
```css
@keyframes coverFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
```

### 印刷・レスポンシブ
```css
@media print {
  .card, .step-card { break-inside: avoid; }
  .card:hover { transform: none; box-shadow: none; }
  body { background: #fff; }
}
@media (max-width: 768px) {
  .grid-2, .kpi-grid { grid-template-columns: 1fr; }
}
```

---

## 規模パターン別カラー

### 個人パターン（ウォームピーチ系）

カバーは明るいグラデーション背景。温かみのある親しみやすい印象。

```css
:root {
  --charcoal: #2c2c34;
  --charcoal-soft: #4a4a56;
  --warm-bg: #fdf8f3;
  --paper: #ffffff;
  --peach: #e07a5f;        /* メインアクセント */
  --peach-deep: #c4603f;
  --sage: #6b8f71;          /* セカンドアクセント */
  --sage-deep: #4d7053;
  --plum: #8a6c8a;          /* サードアクセント */
  --mist: #8a95a5;
  --border: #e8e2da;
  --shadow: rgba(44, 44, 52, 0.07);
}
```

カバー: `background: linear-gradient(160deg, #fdf8f3 0%, #fce8db 40%, #f5d5c3 100%); color: var(--charcoal);`
`::before`のグラデーション: `rgba(224, 122, 95, 0.15)`
セクション番号: `color: var(--peach);`
テーブルヘッダー: `background: var(--charcoal);`
ステップカード色: 1=peach, 2=sage, 3=plum
カバー下線: `linear-gradient(90deg, var(--peach), var(--sage), var(--plum))`

トーン: 「あなたの仕事がどう楽になるか」「明日から始められる」「〜してみましょう」

### チームパターン（ダークインク+テラコッタ系）

カバーはダーク背景。落ち着きと信頼感。

```css
:root {
  --ink: #1a1a2e;
  --ink-soft: #3a3a5c;
  --cream: #faf8f4;
  --paper: #ffffff;
  --terracotta: #c4553a;    /* メインアクセント */
  --terracotta-light: #e8715a;
  --teal: #2a6f6f;          /* セカンドアクセント */
  --teal-deep: #1b4d4d;
  --gold: #b8860b;          /* サードアクセント */
  --gold-light: #d4a836;
  --slate: #64748b;
  --border: #e8e4de;
  --shadow: rgba(26, 26, 46, 0.08);
}
```

カバー: `background: var(--ink); color: var(--cream);`
`::before`のグラデーション: `rgba(196, 85, 58, 0.15)`
セクション番号: `color: var(--terracotta);`
テーブルヘッダー: `background: var(--ink); color: var(--cream);`
ステップカード色: 1=terracotta, 2=gold, 3=teal
カバー下線: `linear-gradient(90deg, var(--terracotta), var(--gold), var(--teal))`
KPIカード: 4カラム

トーン: 「チームの生産性を底上げする」「小さく始めて確実に成果を出す」「〜を推奨します」

### 会社パターン（ネイビー+コッパー系）

カバーはネイビー背景。権威と信頼のフォーマル感。

```css
:root {
  --navy: #0d1b2a;
  --navy-mid: #1b2d45;
  --navy-soft: #324a6e;
  --silver: #c4c9d4;
  --platinum: #e8eaef;
  --ivory: #f5f4f0;
  --paper: #ffffff;
  --copper: #b87333;        /* メインアクセント */
  --copper-light: #d4915c;
  --crimson: #9b2335;       /* ハイインパクト */
  --crimson-soft: #c04050;
  --steel: #5a6577;
  --border: #dcdee3;
  --shadow: rgba(13, 27, 42, 0.08);
}
```

カバー: `background: var(--navy); color: var(--platinum);`
`::before`のグラデーション: `rgba(184, 115, 51, 0.1)`
セクション番号: `color: var(--copper);`
テーブルヘッダー: `background: var(--navy); color: var(--platinum);`
カバー下線: `linear-gradient(90deg, var(--copper), var(--copper-light), var(--copper))`
KPIカード: 4カラム
コンテナ幅: `max-width: 960px;`（個人・チームは880px）

追加要素:
- 優先マトリクス（CSSグリッド + absolute positionのドット）
- ROI試算テーブル（削減時間の赤字表示）
- Go/No-Go判定（2カラムグリッド）
- バッジ: `badge-high`=crimson, `badge-mid`=copper, `badge-low`=navy-soft
- Phase バッジ: アウトライン（border + color、背景transparent）

トーン: 「生産性向上と品質強化のための実行計画」「〜を提言いたします」「PoC（お試し検証）」（専門用語には括弧で注釈）

---

## デザイン原則

- **AIスロップを避ける**: 紫グラデーション、過度な角丸、中央揃えの乱用、Inter/游ゴシックの安易な使用をしない
- **データを主役にする**: 装飾より可読性。KPIは大きく、本文は0.88〜0.93em
- **ホバーは控えめ**: `translateY(-2px)` + 微妙なbox-shadow変化
- **角丸は最小限**: `border-radius: 2px;` をベースに。丸すぎない
- **印刷対応**: `@media print` でホバー無効化、背景白
- **レスポンシブ**: 768px以下でグリッドを1カラムに
- **ファイルサイズ**: 30〜50KB以内に収める。画像は使わない
