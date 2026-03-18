# スプレッドシート生成ガイド

## 概要

HTMLレポートの数値データを `.xlsx` ファイルとしてエクスポートする。ユーザーが数字を自分で調整・試算できる「触る資料」。Google スプレッドシートおよびExcelの両方で開ける。

## いつ生成するか

以下の場合に**提案**する:
- 「数字をいじりたい」「試算を自分で調整したい」と言われた場合
- 業務一覧やROI試算をデータとして手元に残したい場合
- 「上に共有したい」「稟議に使いたい」と言われた場合

## 生成方法

`openpyxl` を使用してPythonで生成する。

```bash
pip install openpyxl
```

## シート構成

### シート1: 業務一覧（必須）

業務トップ5とその分析結果。

| 列 | 内容 | 備考 |
|----|------|------|
| A | # | 連番 |
| B | 業務名 | |
| C | 頻度 | 日次/週次/月次 |
| D | 1回あたりの時間 | 分単位 |
| E | 月間合計時間 | **計算式**: =D×頻度換算 |
| F | 分類 | 定常/例外/対人 |
| G | 自動化余地 | A/B/C |
| H | メモ | ボトルネックの説明等 |

### シート2: 削減効果の試算（必須）

ユーザーが値を変えると結果が自動更新される設計。

```
■ 入力セル（ユーザーが変更する想定）
- 1回あたりの作業時間（分）
- 月間の実施回数
- 自動化率（%）
- 定着率（%）← デフォルト 0.7

■ 計算セル（自動更新）
- 月間削減時間 = 作業時間 × 回数 × 自動化率 × 定着率
- 年間削減時間 = 月間削減時間 × 12
```

入力セルはセル背景色を薄い黄色（`FFF8E1`）にして「ここを変更してください」と分かるようにする。

### シート3: 業務削減提案（任意）

Step 4 で検討した廃止・統合・頻度削減の一覧。

| 列 | 内容 |
|----|------|
| A | 対象業務 |
| B | 削減アプローチ | 🗑️廃止 / 🔗統合 / 📉頻度削減 |
| C | 具体的な内容 |
| D | 想定削減効果 |
| E | 進め方 |

## スタイル

```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# カラーパレット（HTMLレポートと統一）
HEADER_BG = "2C2C34"      # charcoal
HEADER_FG = "FFFFFF"
ACCENT = "E07A5F"         # peach
INPUT_BG = "FFF8E1"       # 薄い黄色（入力セル）
BORDER_COLOR = "E8E2DA"

# ヘッダー行
header_font = Font(name="Yu Gothic", bold=True, color=HEADER_FG, size=10)
header_fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type="solid")

# 本文
body_font = Font(name="Yu Gothic", size=10)

# 入力セル
input_fill = PatternFill(start_color=INPUT_BG, end_color=INPUT_BG, fill_type="solid")

# 罫線
thin_border = Border(
    bottom=Side(style="thin", color=BORDER_COLOR)
)
```

## 生成コードの骨格

```python
import openpyxl
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# --- シート1: 業務一覧 ---
ws1 = wb.active
ws1.title = "業務一覧"

headers = ["#", "業務名", "頻度", "1回あたり(分)", "月間合計(時間)", "分類", "自動化余地", "メモ"]
for col, header in enumerate(headers, 1):
    cell = ws1.cell(row=1, column=col, value=header)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

# データ行を挿入（業務データから生成）
for i, task in enumerate(tasks, 2):
    ws1.cell(row=i, column=1, value=i-1)
    ws1.cell(row=i, column=2, value=task["name"])
    ws1.cell(row=i, column=3, value=task["frequency"])
    ws1.cell(row=i, column=4, value=task["minutes_per_time"])
    # E列は計算式
    ws1.cell(row=i, column=5).value = f"=D{i}*{task['monthly_count']}/60"
    ws1.cell(row=i, column=5).number_format = "0.0"
    ws1.cell(row=i, column=6, value=task["category"])
    ws1.cell(row=i, column=7, value=task["rank"])
    ws1.cell(row=i, column=8, value=task["note"])

# 列幅の自動調整
for col in range(1, len(headers) + 1):
    ws1.column_dimensions[get_column_letter(col)].width = 16

# --- シート2: 削減効果の試算 ---
ws2 = wb.create_sheet("削減効果の試算")
# 入力セル + 計算式を配置（上記の設計に従う）

# --- 保存 ---
wb.save("output/業務分析レポート.xlsx")
```

## 重要な注意点

- **計算式を必ず入れる** — 値をベタ書きせず、ユーザーが数字を変えたら結果が連動する設計にする
- **入力セルを視覚的に区別する** — 薄い黄色背景 + セルコメントで「この値を変更できます」と案内
- **HTMLレポートとデータを一致させる** — 同じ分析結果から両方を生成し、数値の齟齬を防ぐ
- **ファイル名は日本語で** — `業務分析レポート.xlsx` のように、何のファイルか一目で分かる名前にする
