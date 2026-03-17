# PPTXスライド生成ガイド

## 概要

PptxGenJS を使い、コンサルティングレポートをスライド形式で出力する。
pptxスキル（`C:/dev/Vault/anthropic-skills/skills/pptx`）のPptxGenJSガイドとスクリプトを参考にする。

## セットアップ

```bash
npm init -y && npm install pptxgenjs
```

```javascript
const pptxgen = require("pptxgenjs");
let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
```

## スライド構成（10〜15枚目安）

| # | スライド | 内容 |
|---|---------|------|
| 1 | 表紙 | タイトル、対象名、日付 |
| 2 | エグゼクティブサマリー | KPI数値（削減時間、提案数、ROI） |
| 3 | 業務一覧 | 抽出した全業務のテーブル |
| 4 | 分類結果 | 定常/例外/対人の分類と割合 |
| 5 | ランク分布 | A/B/Cランクの分布と主要業務 |
| 6〜N | 提案詳細 | 各提案1枚（ツール、手順、削減時間） |
| N+1 | セキュリティ評価 | リスクマトリクス一覧 |
| N+2 | 導入ロードマップ | 優先度順のタイムライン |
| 最終 | Next Steps | 次のアクション |

## 規模パターン別カラー

HTMLレポートと同じカラーテーマを使う。PptxGenJSではhexカラーに `#` を付けない。

### 個人パターン（ウォームピーチ系）

```javascript
const COLORS = {
  primary: "E07A5F",      // peach
  primaryDeep: "C4603F",
  accent: "6B8F71",       // sage
  accentDeep: "4D7053",
  third: "8A6C8A",        // plum
  text: "2C2C34",         // charcoal
  textLight: "4A4A56",
  mist: "8A95A5",
  bg: "FDF8F3",
  paper: "FFFFFF",
  white: "FFFFFF"
};
```

### チームパターン（ダークインク+テラコッタ系）

```javascript
const COLORS = {
  primary: "C4553A",      // terracotta
  primaryLight: "E8715A",
  accent: "2A6F6F",       // teal
  accentDeep: "1B4D4D",
  third: "B8860B",        // gold
  thirdLight: "D4A836",
  text: "1A1A2E",         // ink
  textLight: "3A3A5C",
  slate: "64748B",
  bg: "FAF8F4",
  paper: "FFFFFF",
  white: "FFFFFF"
};
```

### 会社パターン（ネイビー+コッパー系）

```javascript
const COLORS = {
  primary: "B87333",      // copper
  primaryLight: "D4915C",
  highlight: "9B2335",    // crimson
  highlightSoft: "C04050",
  navy: "0D1B2A",
  navyMid: "1B2D45",
  navySoft: "324A6E",
  text: "0D1B2A",
  textLight: "5A6577",    // steel
  bg: "F5F4F0",           // ivory
  paper: "FFFFFF",
  white: "FFFFFF",
  platinum: "E8EAEF"
};
```

## 共通デザインルール

### フォント

```javascript
const FONT = {
  title: { fontFace: "Yu Gothic UI", fontSize: 28, bold: true, color: COLORS.primary },
  subtitle: { fontFace: "Yu Gothic UI", fontSize: 18, color: COLORS.textLight },
  heading: { fontFace: "Yu Gothic UI", fontSize: 22, bold: true, color: COLORS.text },
  body: { fontFace: "Yu Gothic UI", fontSize: 14, color: COLORS.text },
  caption: { fontFace: "Yu Gothic UI", fontSize: 11, color: COLORS.textLight }
};
```

### レイアウト

- マージン: 上下左右 0.5インチ
- コンテンツ領域: 幅 9インチ、高さ 6.5インチ（16:9）
- セクション間: 0.3〜0.5インチ

### 表紙スライドの例

```javascript
let slide = pres.addSlide();
// 背景色
slide.background = { color: COLORS.primary };
// タイトル
slide.addText("AI業務自動化 提案レポート", {
  x: 0.5, y: 2.0, w: 9.0, h: 1.5,
  fontSize: 36, fontFace: "Yu Gothic UI", bold: true,
  color: COLORS.white, align: "center"
});
// 対象名・日付
slide.addText("株式会社〇〇 様\n2026年3月15日", {
  x: 0.5, y: 4.0, w: 9.0, h: 1.0,
  fontSize: 18, fontFace: "Yu Gothic UI",
  color: COLORS.primaryLight, align: "center"
});
```

### 提案カードスライドの例

```javascript
let slide = pres.addSlide();
// ヘッダーバー
slide.addShape(pres.ShapeType.rect, {
  x: 0, y: 0, w: 10, h: 0.8,
  fill: { color: COLORS.primary }
});
slide.addText("提案 1: 月次レポート自動生成", {
  x: 0.5, y: 0.1, w: 9.0, h: 0.6,
  fontSize: 22, fontFace: "Yu Gothic UI", bold: true,
  color: COLORS.white
});

// KPIボックス（3つ横並び）
const kpis = [
  { label: "削減時間", value: "月 8時間" },
  { label: "導入難易度", value: "低" },
  { label: "概算コスト", value: "無料" }
];
kpis.forEach((kpi, i) => {
  const x = 0.5 + i * 3.1;
  slide.addShape(pres.ShapeType.rect, {
    x: x, y: 1.2, w: 2.8, h: 1.2,
    fill: { color: COLORS.primaryLight },
    rectRadius: 0.1
  });
  slide.addText(kpi.value, {
    x: x, y: 1.3, w: 2.8, h: 0.7,
    fontSize: 24, fontFace: "Yu Gothic UI", bold: true,
    color: COLORS.primary, align: "center"
  });
  slide.addText(kpi.label, {
    x: x, y: 1.9, w: 2.8, h: 0.4,
    fontSize: 12, fontFace: "Yu Gothic UI",
    color: COLORS.textLight, align: "center"
  });
});
```

## 重要な注意点（PptxGenJS の落とし穴）

- hexカラーに `#` を付けない（ファイル破損の原因）
- 8桁hexで透明度を指定しない（`opacity` プロパティを使う）
- オプションオブジェクトを使い回さない（PptxGenJS が内部で変更する）
- 各プレゼンテーションで新しい `pptxgen()` インスタンスを作る
- `ROUNDED_RECTANGLE` にアクセントボーダーを付けない（`RECTANGLE` + `rectRadius` を使う）
