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

### カバーの構成

カバーはコンパクトにする。「業務改善レポート」（テンプレート固定） + メタ情報（1行）のみ。サブタイトルやバッジは不要。

### テンプレート変数一覧

| 変数 | 用途 | 形式・例 |
|---|---|---|
| `{{COVER_META}}` | カバーのメタ情報 | `組織名 部署名 — YYYY年M月D日` |
| `{{TITLE}}` | HTMLの`<title>` | `業務改善レポート — 組織名` |
| `{{AGENT_NAME}}` | フッターのエージェント名 | `CLAUDE CODE` / `MANUS` / `DEVIN` 等 |
| `{{DATE}}` | フッターの日付 | `2026-03-20` |
| `{{SECTIONS}}` | セクションHTML挿入箇所 | （セクションHTML全体） |

### 共通パート（全パターン）

```
【全体像パート】
1. カバー（タイトル + メタ情報1行）
2. Before / After（現状の業務フロー → 提案後の業務フロー。ビフォーアフター形式で並べる）

【詳細パート】
→ パターンA〜Eに応じて構成が変わる（後述）

【まとめパート】
N. まとめ（KPIカード（分析結果に応じた枚数で） + 次のアクション3つ）
```

**セクション2「Before / After」**: レポートの最も重要なセクション。現状の業務フローと提案後のフローを**2カラム縦フロー型**で左右に並べて提示する。読み手が「今どうなっていて、どう変わるのか」を一目で把握できる状態を作る。これがレポート全体のコンテキストになる。

Before / After のレイアウト:
- **2カラム横並び**: 左=Before（現状フロー）、右=After（提案後フロー）。中央に矢印アイコン
- **縦方向のステップカード**: 各カラム内でSTEP 1→2→3…と**縦に並べる**（横フローにしない）
- **ボトルネック強調**: Beforeのボトルネック工程は暖色（peach系）の背景+左ボーダーで強調し、頻度・時間のバッジを右上に表示
- **自動化ハイライト**: Afterの自動化工程は peach（暖色）系の背景+左ボーダーで強調し、「削減 Xh/月」のラベルと使用ツールバッジを表示
- **変更なし工程**: グレー系の控えめなスタイル。「そのまま」と明記
- **カラム下部にサマリー**: Beforeは「合計 ○○h/月、うち自動化可能 ○○h」、Afterは「月○○h削減 → ○○作業へ」

Before / After の設計ルール:
- **Afterは最も推奨する形を1つだけ提示する**: 複数の改善案がある場合でも推奨案に絞る
- **フローは1業務を目安に**: ボトルネックを含む主要業務1つをBefore/Afterで図解し、残りはテーブルで補足
- **ステップ数は3〜6が目安**: 多すぎると視認性が落ちる。7以上になる場合は工程をまとめる
- **レスポンシブ**: 768px以下では2カラム→1カラム（Before上、After下）に切り替え

```html
<!-- Before / After の実装例（2カラム縦フロー型） -->
<div class="ba-columns">
  <!-- Before（左カラム） -->
  <div class="ba-col ba-before">
    <div class="ba-col-header ba-before-header">現状の業務フロー（ボトルネックあり）</div>
    <div class="ba-steps">
      <div class="ba-step">
        <div class="ba-step-title">STEP 1</div>
        <div class="ba-step-body">各部署からExcelで売上データを受領</div>
      </div>
      <div class="ba-step-arrow">▼</div>
      <div class="ba-step bottleneck">
        <div class="ba-step-title">STEP 2 <span class="bn-label">⚠ 最大ボトルネック</span></div>
        <span class="ba-badge badge-warn">8h/月</span>
        <div class="ba-step-body">手動でExcelを統合・集計<br><span class="ba-step-detail">→ 5部署×3シートを手作業でコピペ集約<br>→ 数値ミスの手戻りが月2-3回発生</span></div>
      </div>
      <div class="ba-step-arrow">▼</div>
      <div class="ba-step bottleneck">
        <div class="ba-step-title">STEP 3 <span class="bn-label">⚠ ボトルネック</span></div>
        <span class="ba-badge badge-warn">6h/月</span>
        <div class="ba-step-body">PowerPointでレポート作成<br><span class="ba-step-detail">→ グラフ・表を毎月手作業で更新<br>→ フォーマット崩れの修正に時間を取られる</span></div>
      </div>
      <div class="ba-step-arrow">▼</div>
      <div class="ba-step">
        <div class="ba-step-title">STEP 4</div>
        <div class="ba-step-body">上長レビュー → 修正 → 経営会議で報告</div>
      </div>
    </div>
    <div class="ba-col-summary ba-before-summary">
      月次レポート作成だけで 推定 20h/月<br>うち自動化できる部分は約 12h
    </div>
    <div class="ba-legend"><span class="legend-dot bottleneck-dot"></span> 自動化できる工程（時間を取られている）</div>
  </div>

  <!-- 中央矢印 -->
  <div class="ba-center-arrow">→<br><span class="ba-center-label">自動化</span></div>

  <!-- After（右カラム） -->
  <div class="ba-col ba-after">
    <div class="ba-col-header ba-after-header">提案後のフロー（自動化で12h/月削減）</div>
    <div class="ba-steps">
      <div class="ba-step automated">
        <div class="ba-step-title">自動化 1位 <span class="ba-step-saving">削減 8h/月</span></div>
        <span class="ba-badge badge-tool">GAS + API連携</span>
        <div class="ba-step-body"><strong>売上データの自動集約</strong><br><span class="ba-step-detail">各部署のスプレッドシートをGASで自動統合。手動コピペと数値ミスをゼロに。</span></div>
      </div>
      <div class="ba-step-arrow">▼</div>
      <div class="ba-step automated">
        <div class="ba-step-title">自動化 2位 <span class="ba-step-saving">削減 4h/月</span></div>
        <span class="ba-badge badge-tool">ダッシュボード化</span>
        <div class="ba-step-body"><strong>月次レポートをダッシュボードに置き換え</strong><br><span class="ba-step-detail">Looker Studioで常時更新。PowerPoint作成自体が不要に。</span></div>
      </div>
      <div class="ba-step-arrow">▼</div>
      <div class="ba-step unchanged">
        <div class="ba-step-body"><strong>そのまま</strong><br>上長レビュー → 経営会議で報告（現行通り）</div>
      </div>
    </div>
    <div class="ba-col-summary ba-after-summary">
      月12時間を削減 → 分析・企画業務へ<br>Google Workspace内で実現可能、追加費用ゼロ
    </div>
    <div class="ba-legend"><span class="legend-dot automated-dot"></span> 自動化された工程 <span class="legend-dot unchanged-dot"></span> 現行維持</div>
  </div>
</div>
```

CSSクラス:
```css
/* === Before / After 2カラム縦フロー === */
.ba-columns {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 20px;
  margin: 32px 0;
  align-items: start;
}
.ba-col {
  border-radius: 8px;
  padding: 0;
  overflow: hidden;
}
.ba-col-header {
  padding: 14px 20px;
  font-family: 'Noto Serif JP', serif;
  font-weight: 700;
  font-size: 0.92em;
  text-align: center;
  letter-spacing: 1px;
}
.ba-before-header { background: var(--charcoal); color: #fff; }
.ba-after-header { background: var(--peach-deep); color: #fff; }
.ba-steps { padding: 20px; }

/* ステップカード */
.ba-step {
  background: var(--paper);
  border: 1px solid var(--border);
  border-left: 4px solid var(--border);
  padding: 14px 18px;
  position: relative;
}
.ba-step.bottleneck {
  background: rgba(224, 122, 95, 0.08);
  border-left: 4px solid var(--peach);
}
.ba-step.bottleneck .ba-step-title { color: var(--peach-deep); font-weight: 700; }
.ba-step.automated {
  background: rgba(224, 122, 95, 0.06);
  border-left: 4px solid var(--peach);
}
.ba-step.unchanged {
  background: rgba(138, 149, 165, 0.06);
  border-left: 4px solid var(--border);
  color: var(--charcoal-soft);
}
.ba-step-title { font-size: 0.82em; font-weight: 700; margin-bottom: 6px; }
.ba-step-body { font-size: 0.88em; line-height: 1.7; }
.ba-step-detail { font-size: 0.85em; color: var(--charcoal-soft); }
.ba-step-saving { color: var(--peach-deep); font-weight: 700; }
.bn-label { color: var(--peach); font-size: 0.9em; }
.ba-step-arrow { text-align: center; color: var(--mist); font-size: 0.9em; padding: 4px 0; }

/* バッジ（右上） */
.ba-badge {
  position: absolute;
  top: 10px; right: 10px;
  font-size: 0.7em;
  padding: 3px 10px;
  border-radius: 2px;
  font-weight: 700;
}
.badge-warn { background: var(--peach); color: #fff; }
.badge-tool { background: var(--charcoal); color: #fff; }

/* カラム下部サマリー */
.ba-col-summary {
  margin: 0 20px 16px;
  padding: 14px 18px;
  text-align: center;
  font-size: 0.88em;
  font-weight: 700;
  border-radius: 4px;
}
.ba-before-summary { background: rgba(224, 122, 95, 0.10); color: var(--peach-deep); }
.ba-after-summary { background: rgba(224, 122, 95, 0.10); color: var(--peach-deep); }

/* 凡例 */
.ba-legend { padding: 0 20px 16px; font-size: 0.75em; color: var(--charcoal-soft); }
.legend-dot { display: inline-block; width: 10px; height: 10px; margin-right: 4px; vertical-align: middle; }
.bottleneck-dot { background: rgba(224, 122, 95, 0.3); border-left: 3px solid var(--peach); }
.automated-dot { background: rgba(224, 122, 95, 0.3); border-left: 3px solid var(--peach); }
.unchanged-dot { background: rgba(138, 149, 165, 0.15); border-left: 3px solid var(--border); }

/* 中央矢印 */
.ba-center-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 1.6em;
  color: var(--peach);
  font-weight: 900;
  padding-top: 200px;
}
.ba-center-label { font-size: 0.4em; letter-spacing: 2px; margin-top: 4px; }

/* レスポンシブ: 768px以下で1カラム */
@media (max-width: 768px) {
  .ba-columns { grid-template-columns: 1fr; }
  .ba-center-arrow {
    padding-top: 0;
    flex-direction: row;
    gap: 8px;
    font-size: 1.2em;
  }
  .ba-center-arrow::before { content: '▼'; }
}
```

**まとめセクション**: 以下の2要素を最後に集約する:
1. **KPIカード**: 改善タスク数・時間変化・追加コスト等（分析結果に応じた枚数で）
2. **今週やること**: すぐ着手できる具体的アクション3つ

レポートを読み終えた後に「まず何をすればいいか」がすぐ分かる状態にする。

---

## 詳細パートの構成方針

詳細パートのセクション構成は固定ではなく、**分析結果とユーザーの特性に応じてその場で最適な構成を判断する**。以下の2軸と設計原則に基づいて判断すること。

### 判断の2軸

**軸1: 手段の見直し vs 仕組み化の比率** — Step 4の結果から判定する。
- 🔄手段変更 + 📉簡素化 + 🗑️不要 = 見直し件数
- 🔧仕組み化 = 仕組み化件数
- 見直しが多ければ手段変更の提案がメイン、仕組み化が多ければツール提案がメイン、混合なら両方

**軸2: ユーザーのITリテラシー** — 収集データとヒアリングから判定する。
- n8n / Zapier / GitHub / API系ツールを使いこなしている → **高い**（技術的な詳細を深掘り、実装レベルの提案）
- それ以外 → **普通〜低い**（手順書レベルの説明、代替案やフォールバックが重要）

### セクション設計の原則

1. **目的から手段を問い直した結果は必ず含める。** 見直し余地が大きければメインセクションとして深掘りし、小さければ「検討したが限定的」と簡潔に記載する。スキップしない。これがスキルの核心原則のガードレール

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

CSSは「デザイントークン（必須）」と「コンポーネント参考実装（目安）」の2層で構成する。デザイントークン（カラーパレット、フォントファミリー、border-radius方針）は基本的に守る。ブランドカラー等の要件がある場合は調整してよい。コンポーネントのpadding・margin・gap・font-size・animationの具体的な数値は参考値であり、視覚的バランスを維持する範囲で調整してよい。

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
.cover h1 {
  font-family: 'Noto Serif JP', serif;
  font-size: 3em;
  font-weight: 900;
  letter-spacing: 0.05em;
  margin-bottom: 14px;
  animation: fadeUp 0.6s ease-out 0.35s both;
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

- **文章より構造で見せる**: 説明文を連ねるのではなく、テーブル・フロー図・比較カード・箇条書きで構造化する。「読む」より「見てわかる」を優先。文章が必要な場面（根拠の説明、ニュアンスの補足）でも、先に構造で全体像を示してから補足文を添える
- **AIスロップを避ける**: 紫グラデーション、過度な角丸、中央揃えの乱用、Inter/游ゴシックの安易な使用をしない
- **データを主役にする**: 装飾より可読性。KPIは大きく、本文は0.88〜0.93em
- **ホバーは控えめ**: `translateY(-2px)` + 微妙なbox-shadow変化
- **角丸は最小限**: `border-radius: 2px;` をベースに。丸すぎない
- **印刷対応**: `@media print` でホバー無効化、背景白
- **レスポンシブ**: 768px以下でグリッドを1カラムに
- **ファイルサイズ**: 30〜50KB以内に収める。画像は使わない

---

## ハマりどころ

### 1. KPI数値の一貫性

レポート内の削減時間は**端数を四捨五入せず、内訳の合計と一致させる**こと。KPIカードに「25h」と書いて内訳が24.8hだと信頼性が下がる。KPIカードの値は内訳の合計をそのまま使い、端数があればそのまま表示する（例: 24.8h）。

### 2. 手段の見直し提案の根拠の明示

手段変更・簡素化・不要の提案には「なぜ今の手段が目的に対して最善でないと判断したか」の根拠を必ず書く。収集データから得た事実（例: Slackで週次集計への言及が月次会議前の週にしかない）を具体的に引用する。「実際には使われていない」のような断定だけでは読み手が判断できない。

### 3. フロー図解のメリハリ

テキストベースのフロー図解では、ボトルネック以外の工程が全て同じ見た目になりがち。`.ok` クラスを正常工程に適用し、ボトルネック工程との視覚的コントラストを確保すること。工程数が多い場合はボトルネック周辺だけ抜き出して表示し、全工程の詳細はテーブルに任せる。

### 4. テンプレートの使い方

template.html のプレースホルダー（`{{TITLE}}`等）を置換して使う。CSSは template.html に含まれているので、セクションHTMLだけを `{{SECTIONS}}` に挿入すれば完成する。CSS全体を毎回書き直さない。ただし、レポート固有のCSSが必要な場合は `<style>` ブロックをセクション内に追加してよい。**最終出力のHTMLに `{{...}}` が残っていないことを必ず確認する。** 変数一覧は「テンプレート変数一覧」セクションを参照。

### 5. セクション数と情報密度のバランス

「その他の候補」のような低優先セクションに項目が1〜2件しかない場合、独立セクションにせず前のセクションの末尾にカード1枚で収める。セクションを分ける判定基準: 3件以上の提案がある or 深掘り説明が必要（始め方のステップが3つ以上）。

### 6. フロー図解が長くなる問題

業務フローが3つ以上ある場合、全フローをflow-boxに並べると冗長になる。対策:
- ボトルネックを含むフロー2つまでをflow-boxで図解
- 残りのフローはテーブルの「ボトルネック工程」列で説明を兼ねる
- flow-boxのフローは「ボトルネック周辺の3〜5工程」に絞り、前後は省略記号（…）で示す

### 7. 複数ツール候補がある場合の比較

レポート内でツールを推奨する際、同カテゴリに複数の候補がある場合は信頼度（提供継続性、無料プランの安定性、日本語対応等）も比較材料に含める。1つのツールだけを挙げるとそのツールが終了・変更された場合にレポート全体の信頼性が損なわれるため、代替候補を併記するか、選定理由を明記する。

### 8. analysis-framework.md の分類活用

業務一覧テーブルには「分類」列（定常/例外/対人）を含めること。この分類が Step 4 の手段の見直しの判断根拠になる。定常業務は自動化候補、例外業務はルール化候補、対人業務は周辺作業の切り出し候補。分類がレポートに出ていないと、提案の論理的根拠が弱くなる。

**分類列は「ヘッダーだけ書いて値が空」になりがち。** テーブルの各行に必ず「定常」「例外」「対人」のいずれかを記入すること。空セルにしない。

### 9. セクション番号のフォーマット統一

セクション番号は **`1`, `2`, `3`...** のアラビア数字をそのまま使う（ゼロパディング `01` は使わない）。HTMLタグは `<div class="num">` で統一する（`<span>` は使わない）。テンプレートのCSSは `.section-header .num` で定義されているため、タグの種類は見た目に影響しないが、マークアップの一貫性のため `<div>` に揃える。

### 10. テーブルのカラム幅の必須指定

`table-layout: fixed` を使っているため、`<th>` に `style="width:XX%"` を必ず指定すること。幅指定がないと列幅が予測不能になり、長いテキストで崩れる。目安:
- 業務名: 20-25%
- 分類: 8-12%
- 頻度: 10-14%
- 時間: 12-15%
- ボトルネック/備考: 25-35%
合計が100%になるよう調整する。

### 11. ネクストアクションのヘッダーテキスト

`.next-action h3` のテキストは **「今週やること」を推奨**する。対象者や状況に応じて調整してよい（例: 短期プロジェクトなら「明日やること」、長期なら「今月の最初の一歩」等）。ただしレポートの全体トーンが日本語のため、英語ヘッダー（「Next Actions」等）は避ける。
