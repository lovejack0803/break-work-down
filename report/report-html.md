# HTMLレポート生成ガイド

## 概要

**単一の静的HTMLファイル**として出力する。React/ビルドツールは使わない。HTML + CSS + インラインスタイルのみで完結させる。

外部依存はGoogle Fontsのみ:
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700;900&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap" rel="stylesheet">
```

## ベーススタイル

```css
body {
  font-family: 'Zen Kaku Gothic New', sans-serif;
  line-height: 1.9;      /* 1.8〜1.9程度。詰まりすぎない行間 */
  font-weight: 400;
  overflow-x: hidden;
}

/* 見出し・数値 → Noto Serif JP */
/* 本文 → Zen Kaku Gothic New */
```

---

## レポート構成

ゴールは「読み手がまず全体像を掴み、次に各提案の詳細を理解し、最後に次の一歩を決められる」こと。全業務を網羅的に並べるのではなく、**1位の提案に深掘り**する構成にする。

構成は**「全体像 → 詳細 → まとめ」**の3部構成。全体像パートとまとめパートは全パターン共通。**詳細パートはパターンによって変化する。**

### 共通パート（全パターン）

```
【全体像パート】
1. カバー（タイトル、対象バッジ、サブタイトル、日付）
2. 業務の全体像（業務フローマップ + 時間消費トップ5テーブル。ボトルネック箇所をマーク）

【詳細パート】
→ パターンA〜Eに応じて構成が変わる（後述）

【まとめパート】
N. まとめ（KPIカード3〜4個 + 次のアクション3つ）
```

**セクション2「業務の全体像」**: 最初に業務フローのテキスト図解を提示し、ボトルネック箇所を視覚的にマークする。読み手が「自分の業務のどこに問題があるのか」を一目で把握できる状態を作る。これがレポート全体のコンテキストになる。

**まとめセクション**: KPIカード（ボトルネック数・削減可能時間・追加コスト等）と、今週中にやるべき具体的アクション3つを最後に集約する。レポートを読み終えた後に「で、何をすればいい？」がすぐ分かる状態にする。

---

## 詳細パートの構成方針

詳細パートのセクション構成は固定ではなく、**分析結果とユーザーの特性に応じてその場で最適な構成を判断する**。以下の2軸と設計原則に基づいて判断すること。

### 判断の2軸

**軸1: 削減 vs 仕組み化の比率** — Step 4の結果から判定する。
- 🗑️廃止 + 🔗統合 + 📉頻度削減 = 削減件数
- 🔧仕組み化 = 仕組み化件数
- 削減が多ければ削減提案がメイン、仕組み化が多ければツール提案がメイン、混合なら両方

**軸2: ユーザーのITリテラシー** — 収集データとヒアリングから判定する。
- n8n / Zapier / GitHub / API系ツールを使いこなしている → **高い**（技術的な詳細を深掘り、実装レベルの提案）
- それ以外 → **普通〜低い**（手順書レベルの説明、代替案やフォールバックが重要）

### セクション設計の原則

1. **業務削減の検討結果は必ず含める。** 削減余地が大きければメインセクションとして深掘りし、小さければ「検討したが限定的」と簡潔に記載する。スキップしない。これがスキルの核心原則のガードレール

2. **分析で出てきた提案にだけセクションを割く。** ツール提案がないのに「使用ツール」セクションを作らない。削減だけで完結するなら仕組み化セクションは不要

3. **セクション名は内容に合わせて具体化する。** 汎用的な名前（「つまずきポイント」等）を避け、何についてのセクションかが名前だけで分かるようにする。例:
   - 削減が主なら「現場で起きがちな抵抗と対策」
   - ツール導入が主でベーシックなら「導入時のよくある困りごと」
   - 技術的な実装が主なら「実装時のハマりどころ」

4. **リテラシーに合わせて深さを変える。**
   - 高い: API設計・ワークフロー構成等の技術詳細、ツール比較は性能・拡張性軸で。フォールバックは不要（自分で判断できる）
   - 普通〜低い: 「ここをクリック → 次にこう操作」レベルの手順。フォールバック（うまくいかない場合のプランB）を含める。「誰に頼むか」の導入サポートも検討する

5. **1位の提案に深掘りセクションを割く。** 2位・3位は概要のみ。深掘りの粒度はリテラシーに合わせる

---

## CSSコンポーネント

CSSは「デザイントークン（必須）」と「コンポーネント参考実装（目安）」の2層で構成する。デザイントークン（カラーパレット、フォントファミリー、border-radius方針）は厳密に守ること。コンポーネントのpadding・margin・gap・font-size・animationの具体的な数値は参考値であり、視覚的バランスを維持する範囲で調整してよい。

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
  max-width: 880px;
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
  max-width: 520px;
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

ステップカード色: 1=peach, 2=sage, 3=plum

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


---

## カラーパレット（ウォームピーチ系）

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
カバー下線: `linear-gradient(90deg, var(--peach), var(--sage), var(--plum))`

トーン: 「あなたの仕事がどう楽になるか」「明日から始められる」「〜してみましょう」

---

## デザイン原則

- **AIスロップを避ける**: 紫グラデーション、過度な角丸、中央揃えの乱用、Inter/游ゴシックの安易な使用をしない
- **データを主役にする**: 装飾より可読性。KPIは大きく、本文は0.88〜0.93em
- **ホバーは控えめ**: `translateY(-2px)` + 微妙なbox-shadow変化
- **角丸は最小限**: `border-radius: 2px;` をベースに。丸すぎない
- **印刷対応**: `@media print` でホバー無効化、背景白
- **レスポンシブ**: 768px以下でグリッドを1カラムに
- **ファイルサイズ**: 30〜50KB以内に収める。画像は使わない

---

## ハマりどころ

実際の運用で発見した問題点・失敗パターンをここに蓄積する。

（まだ記録なし）
