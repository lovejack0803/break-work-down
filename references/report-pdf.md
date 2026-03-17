# PDF生成ガイド

## 概要

PDFはHTMLレポートから変換して生成する。専用のPDF生成ライブラリは使わない。HTMLレポートが既に印刷対応CSS（`@media print`）を含んでいるため、そのまま高品質なPDFになる。

## いつ生成するか

以下の場合にPDF出力を**提案**する:
- 「メールで送りたい」「印刷したい」「社内稟議に添付したい」と言われた場合
- HTMLファイルを直接共有できない環境の場合

## 生成方法

### 方法1: ブラウザ変換（推奨・確実）

ユーザーに以下を案内する:

```
HTMLファイルをブラウザで開き、Ctrl+P（⌘+P）→「PDFとして保存」を選択してください。
レイアウトは「横向き」、余白は「なし」または「最小」がおすすめです。
```

HTMLレポートの `@media print` が自動で適用され、ホバーエフェクトの無効化・背景白化・改ページ制御が効く。

### 方法2: スクリプト変換（自動化が必要な場合）

```bash
# Playwrightを使用（Node.js）
npm install playwright
```

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // HTMLファイルを開く
  await page.goto(`file://${process.argv[2]}`, { waitUntil: 'networkidle' });

  // PDF生成
  await page.pdf({
    path: process.argv[3] || 'output/report.pdf',
    format: 'A4',
    landscape: false,
    printBackground: true,  // 背景色を含める
    margin: { top: '12mm', bottom: '12mm', left: '10mm', right: '10mm' },
  });

  await browser.close();
})();
```

```bash
node generate-pdf.js output/report.html output/report.pdf
```

### 方法3: Python（weasyprint）

```bash
pip install weasyprint
```

```python
from weasyprint import HTML
HTML(filename="output/report.html").write_pdf("output/report.pdf")
```

注意: weasyprintはGoogle Fontsの読み込みに対応しているが、環境によってはフォントが正しく表示されない場合がある。方法1または方法2を推奨。

## 重要な注意点

- **PDFのためにHTMLレポートを修正しない** — `@media print` で制御する
- **方法1（ブラウザ変換）を最初に提案する** — 追加ツール不要で最も確実
- **スクリプト変換は「n8nワークフローに組み込みたい」等の自動化ニーズがある場合のみ提案する**
