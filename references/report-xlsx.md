# Excelワークブック生成ガイド

## 概要

openpyxl を使い、コンサルティングレポートの数値データ・分析結果を編集可能なExcelワークブックとして出力する。

HTMLレポートが「読む資料」であるのに対し、Excelは**「触る資料」** — ユーザーが数値を変更してシミュレーションしたり、アクション管理に使い続けるためのもの。

## いつ生成するか

以下の場合にExcel出力を**提案**する（HTMLレポートは常に必須、Excelは任意）:
- ユーザーが「数字を自分でいじりたい」「ROIを上に報告する」と言った場合
- 会社パターンの場合（PoC管理・効果測定にスプレッドシートが必要になることが多い）
- アクション管理表として使い続ける用途がある場合

## セットアップ

```bash
pip install openpyxl
```

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
```

## ワークブック構成（シート構成）

| # | シート名 | 内容 | 想定用途 |
|---|---------|------|---------|
| 1 | サマリー | KPI数値、提案概要、主要な結論 | 全体像の把握 |
| 2 | 業務分析 | 業務トップ5のテーブル（時間・頻度・自動化余地） | 現状把握、追加分析 |
| 3 | ROI試算 | 削減時間・コスト・投資額・回収期間の計算式付き | 数値変更でシミュレーション |
| 4 | アクション管理 | Next Action + PoC計画のチェックリスト | 進捗トラッキング |
| 5 | セキュリティ評価 | ツール別セキュリティ比較（会社パターンのみ） | 稟議添付資料 |

個人パターンではシート2〜3のみ、チームパターンではシート1〜4、会社パターンでは全シート。

---

## 規模パターン別カラー

HTMLレポートと同じカラーテーマを使う。openpyxlではhexカラーに `#` を付けない（6桁hex）。

### 個人パターン（ウォームピーチ系）

```python
COLORS = {
    "primary": "E07A5F",
    "primary_deep": "C4603F",
    "accent": "6B8F71",
    "third": "8A6C8A",
    "text": "2C2C34",
    "text_light": "4A4A56",
    "bg": "FDF8F3",
    "header_bg": "2C2C34",
    "header_text": "FFFFFF",
    "border": "E8E2DA",
    "highlight_bg": "FFF3ED",
}
```

### チームパターン（ダークインク+テラコッタ系）

```python
COLORS = {
    "primary": "C4553A",
    "primary_light": "E8715A",
    "accent": "2A6F6F",
    "third": "B8860B",
    "text": "1A1A2E",
    "text_light": "64748B",
    "bg": "FAF8F4",
    "header_bg": "1A1A2E",
    "header_text": "FFFFFF",
    "border": "E8E4DE",
    "highlight_bg": "FFF5F2",
}
```

### 会社パターン（ネイビー+コッパー系）

```python
COLORS = {
    "primary": "B87333",
    "primary_light": "D4915C",
    "highlight": "9B2335",
    "navy": "0D1B2A",
    "navy_soft": "324A6E",
    "text": "0D1B2A",
    "text_light": "5A6577",
    "bg": "F5F4F0",
    "header_bg": "0D1B2A",
    "header_text": "E8EAEF",
    "border": "DCDEE3",
    "highlight_bg": "FDF5F0",
}
```

---

## 共通スタイル定義

```python
def create_styles(colors):
    """パターン共通のスタイルセットを生成"""
    return {
        "header": {
            "font": Font(name="Yu Gothic UI", size=11, bold=True, color=colors["header_text"]),
            "fill": PatternFill(start_color=colors["header_bg"], end_color=colors["header_bg"], fill_type="solid"),
            "alignment": Alignment(horizontal="center", vertical="center", wrap_text=True),
            "border": Border(
                bottom=Side(style="thin", color=colors["border"])
            ),
        },
        "body": {
            "font": Font(name="Yu Gothic UI", size=10, color=colors["text"]),
            "alignment": Alignment(vertical="center", wrap_text=True),
            "border": Border(
                bottom=Side(style="thin", color=colors["border"])
            ),
        },
        "title": {
            "font": Font(name="Yu Gothic UI", size=16, bold=True, color=colors["primary"]),
        },
        "subtitle": {
            "font": Font(name="Yu Gothic UI", size=11, color=colors["text_light"]),
        },
        "kpi_value": {
            "font": Font(name="Yu Gothic UI", size=24, bold=True, color=colors["primary"]),
            "alignment": Alignment(horizontal="center", vertical="center"),
        },
        "kpi_label": {
            "font": Font(name="Yu Gothic UI", size=9, color=colors["text_light"]),
            "alignment": Alignment(horizontal="center", vertical="center"),
        },
        "highlight_row": {
            "fill": PatternFill(start_color=colors["highlight_bg"], end_color=colors["highlight_bg"], fill_type="solid"),
        },
        "number": {
            "font": Font(name="Yu Gothic UI", size=10, color=colors["text"]),
            "alignment": Alignment(horizontal="right", vertical="center"),
            "number_format": '#,##0',
        },
        "percent": {
            "font": Font(name="Yu Gothic UI", size=10, color=colors["text"]),
            "alignment": Alignment(horizontal="right", vertical="center"),
            "number_format": '0%',
        },
        "hours": {
            "font": Font(name="Yu Gothic UI", size=10, color=colors["text"]),
            "alignment": Alignment(horizontal="right", vertical="center"),
            "number_format": '#,##0"h"',
        },
        "reduction": {
            "font": Font(name="Yu Gothic UI", size=10, bold=True, color=colors["highlight"]),
            "alignment": Alignment(horizontal="right", vertical="center"),
            "number_format": '▲#,##0"h"',
        },
    }
```

---

## シート別の実装例

### シート1: サマリー

```python
ws = wb.active
ws.title = "サマリー"
ws.sheet_properties.tabColor = colors["primary"]

# カラム幅
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 25
ws.column_dimensions["C"].width = 20
ws.column_dimensions["D"].width = 20
ws.column_dimensions["E"].width = 20

# タイトル行
ws.merge_cells("B2:E2")
ws["B2"].value = "AI活用提案レポート — サマリー"
ws["B2"].font = styles["title"]["font"]

# サブタイトル
ws.merge_cells("B3:E3")
ws["B3"].value = f"対象: {target_name} ｜ 日付: {date}"
ws["B3"].font = styles["subtitle"]["font"]

# KPIカード（横並び）
kpis = [
    ("月間削減見込み", f"{min_hours}〜{max_hours}h"),
    ("対象人数", f"{team_size}名"),
    ("自動化候補", f"{candidate_count}つ"),
    ("追加コスト", cost_estimate),
]
for i, (label, value) in enumerate(kpis):
    col = get_column_letter(2 + i)  # B, C, D, E
    ws[f"{col}5"].value = value
    ws[f"{col}5"].font = styles["kpi_value"]["font"]
    ws[f"{col}5"].alignment = styles["kpi_value"]["alignment"]
    ws[f"{col}6"].value = label
    ws[f"{col}6"].font = styles["kpi_label"]["font"]
    ws[f"{col}6"].alignment = styles["kpi_label"]["alignment"]
```

### シート2: 業務分析

```python
ws = wb.create_sheet("業務分析")
ws.sheet_properties.tabColor = colors["accent"]

headers = ["#", "業務名", "頻度", "1回あたり", "月間チーム計", "自動化余地"]
col_widths = [5, 30, 10, 15, 15, 12]

# ヘッダー行
for i, (header, width) in enumerate(zip(headers, col_widths), 1):
    col = get_column_letter(i)
    ws.column_dimensions[col].width = width
    cell = ws[f"{col}1"]
    cell.value = header
    cell.font = styles["header"]["font"]
    cell.fill = styles["header"]["fill"]
    cell.alignment = styles["header"]["alignment"]

# データ行
for row_idx, task in enumerate(top5_tasks, 2):
    ws[f"A{row_idx}"].value = row_idx - 1
    ws[f"B{row_idx}"].value = task["name"]
    ws[f"C{row_idx}"].value = task["frequency"]
    ws[f"D{row_idx}"].value = task["time_per_item"]
    ws[f"E{row_idx}"].value = task["monthly_total"]
    ws[f"F{row_idx}"].value = task["automation_potential"]
    # ボディスタイル適用
    for col in "ABCDEF":
        ws[f"{col}{row_idx}"].font = styles["body"]["font"]
        ws[f"{col}{row_idx}"].border = styles["body"]["border"]
        ws[f"{col}{row_idx}"].alignment = styles["body"]["alignment"]
```

### シート3: ROI試算（計算式付き）

**このシートの最大の価値: ユーザーが数値を変更すると結果が自動更新される。**

```python
ws = wb.create_sheet("ROI試算")
ws.sheet_properties.tabColor = colors["primary"]

# 入力セクション（ユーザーが編集する箇所）
ws["B2"].value = "■ 入力値（変更可能）"
ws["B2"].font = Font(name="Yu Gothic UI", size=12, bold=True, color=colors["primary"])

input_rows = [
    ("チーム人数", team_size, "人"),
    ("1記事あたり作業時間（現状）", current_minutes, "分"),
    ("1人あたり1日の記事数", articles_per_day, "本"),
    ("月間営業日数", 20, "日"),
    ("想定自動化率", 0.6, None),  # 60%
    ("定着率係数", 0.75, None),
    ("Claude API月額費用", api_cost, "円"),
]

for i, (label, value, unit) in enumerate(input_rows, 4):
    ws[f"B{i}"].value = label
    ws[f"B{i}"].font = styles["body"]["font"]
    ws[f"C{i}"].value = value
    if unit:
        ws[f"D{i}"].value = unit
        ws[f"C{i}"].font = styles["number"]["font"] if isinstance(value, (int, float)) else styles["body"]["font"]
    else:
        ws[f"C{i}"].font = styles["percent"]["font"]
        ws[f"C{i}"].number_format = '0%'
    # 入力セルを目立たせる
    ws[f"C{i}"].fill = PatternFill(start_color=colors["highlight_bg"], end_color=colors["highlight_bg"], fill_type="solid")

# 計算セクション（数式で自動計算）
ws["B13"].value = "■ 計算結果（自動計算）"
ws["B13"].font = Font(name="Yu Gothic UI", size=12, bold=True, color=colors["primary"])

calc_rows = [
    ("月間総作業時間（現状）", "=C4*C5*C6*C7/60", "h"),       # 人数×分×記事数×日数÷60
    ("月間削減時間", "=C15*C8*C9", "h"),                       # 現状×自動化率×定着率
    ("年間削減時間", "=C16*12", "h"),
    ("人件費換算（時給2,000円想定）", "=C17*2000", "円"),
    ("年間追加コスト", "=C10*12", "円"),
    ("年間純削減効果", "=C18-C19", "円"),
    ("投資回収期間", '=IF(C20>0,C19/C20*12,"N/A")', "ヶ月"),
]

for i, (label, formula, unit) in enumerate(calc_rows, 15):
    ws[f"B{i}"].value = label
    ws[f"B{i}"].font = styles["body"]["font"]
    ws[f"C{i}"].value = formula
    ws[f"C{i}"].font = styles["number"]["font"]
    ws[f"C{i}"].number_format = '#,##0'
    ws[f"D{i}"].value = unit
```

### シート4: アクション管理

```python
ws = wb.create_sheet("アクション管理")
ws.sheet_properties.tabColor = colors["accent"]

headers = ["#", "アクション", "担当者", "期限", "ステータス", "備考"]
col_widths = [5, 40, 12, 12, 12, 25]

# ヘッダー
for i, (header, width) in enumerate(zip(headers, col_widths), 1):
    col = get_column_letter(i)
    ws.column_dimensions[col].width = width
    cell = ws[f"{col}1"]
    cell.value = header
    cell.font = styles["header"]["font"]
    cell.fill = styles["header"]["fill"]
    cell.alignment = styles["header"]["alignment"]

# データ行 + ドロップダウン（ステータス列）
from openpyxl.worksheet.datavalidation import DataValidation
dv = DataValidation(
    type="list",
    formula1='"未着手,進行中,完了,保留"',
    allow_blank=True,
)
dv.error = "未着手/進行中/完了/保留 から選択してください"
ws.add_data_validation(dv)

for row_idx, action in enumerate(actions, 2):
    ws[f"A{row_idx}"].value = row_idx - 1
    ws[f"B{row_idx}"].value = action["description"]
    ws[f"C{row_idx}"].value = action["assignee"]
    ws[f"D{row_idx}"].value = action["deadline"]
    ws[f"E{row_idx}"].value = "未着手"
    dv.add(ws[f"E{row_idx}"])
    # スタイル適用（省略）
```

---

## ファイル保存

```python
output_path = "output/report.xlsx"
wb.save(output_path)
```

---

## 重要な注意点

- **hexカラーに `#` を付けない** — openpyxlは6桁hexを期待する。`#B87333` ではなく `B87333`
- **数式は文字列として代入する** — `ws["C15"].value = "=C4*C5"` のように `=` から始める
- **ROI試算シートでは必ず計算式を使う** — ハードコードした数値ではなく、入力セルへの参照式にする。ユーザーが数値を変えたら結果が自動更新される設計にする
- **入力セルと計算セルを視覚的に区別する** — 入力セルはハイライト背景、計算セルは通常背景
- **シートタブに色を付ける** — `ws.sheet_properties.tabColor` でパターンのアクセント色を設定
- **カラム幅は内容に合わせて設定する** — `ws.column_dimensions[col].width` を必ず設定。デフォルト幅は狭すぎる
- **日本語フォントは "Yu Gothic UI" を使う** — HTMLレポートの "Zen Kaku Gothic New" はExcelに入っていない
