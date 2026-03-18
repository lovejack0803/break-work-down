"""
収集データの保存・読み込み・差分検出スクリプト

使い方:
  # 保存（stdinからJSONを受け取り、data/ に保存）
  echo '{"sources":["slack"],...}' | python scripts/save_collection_data.py save

  # 最新データの読み込み
  python scripts/save_collection_data.py load

  # 差分検出（latest.json と stdin の新データを比較）
  echo '{"sources":["slack"],...}' | python scripts/save_collection_data.py diff

出力: JSON（stdout）
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_data_dir():
    """data/ ディレクトリのパスを返す（なければ作成）"""
    # スクリプトの親の親 = スキルのルートディレクトリ
    skill_root = Path(__file__).resolve().parent.parent
    data_dir = skill_root / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


# --- 保存 ---

def save(data):
    """収集データをdata/に保存"""
    data_dir = get_data_dir()

    # collected_at がなければ現在時刻を付与
    if "collected_at" not in data:
        data["collected_at"] = datetime.now(timezone.utc).isoformat()

    # 日付入りスナップショット
    date_str = datetime.now().strftime("%Y-%m-%d")
    snapshot_path = data_dir / f"collection_{date_str}.json"

    # 同日に複数回実行された場合は上書き
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # latest.json を常に上書き
    latest_path = data_dir / "latest.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    result = {
        "status": "saved",
        "snapshot": str(snapshot_path),
        "latest": str(latest_path),
        "collected_at": data["collected_at"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


# --- 読み込み ---

def load():
    """latest.json を読み込んで出力"""
    data_dir = get_data_dir()
    latest_path = data_dir / "latest.json"

    if not latest_path.exists():
        print(json.dumps({"status": "no_previous_data"}, ensure_ascii=False, indent=2))
        return

    with open(latest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["_status"] = "loaded"
    data["_path"] = str(latest_path)
    print(json.dumps(data, ensure_ascii=False, indent=2))


# --- 差分検出 ---

def diff(new_data):
    """latest.json と新データを比較し、差分を出力"""
    data_dir = get_data_dir()
    latest_path = data_dir / "latest.json"

    if not latest_path.exists():
        print(json.dumps({
            "status": "no_previous_data",
            "message": "前回のデータがありません。初回実行です。",
        }, ensure_ascii=False, indent=2))
        return

    with open(latest_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    changes = {
        "status": "diff_detected",
        "previous_date": old_data.get("collected_at", "不明"),
        "previous_question": old_data.get("confirmed_question", None),
        "tool_changes": detect_tool_changes(old_data, new_data),
        "task_changes": detect_task_changes(old_data, new_data),
    }

    # 変化がなければステータスを変更
    if not changes["tool_changes"] and not changes["task_changes"]:
        changes["status"] = "no_changes"
        changes["message"] = "前回からの大きな変化はありません"

    print(json.dumps(changes, ensure_ascii=False, indent=2))


def detect_tool_changes(old_data, new_data):
    """ツール環境の変化を検出"""
    changes = []

    old_tools = {t.get("name", t.get("domain", "")): t for t in old_data.get("tool_environment", old_data.get("domains", []))}
    new_tools = {t.get("name", t.get("domain", "")): t for t in new_data.get("tool_environment", new_data.get("domains", []))}

    old_names = set(old_tools.keys())
    new_names = set(new_tools.keys())

    # 新規ツール
    for name in new_names - old_names:
        changes.append({
            "type": "added",
            "name": name,
            "category": new_tools[name].get("category", "不明"),
        })

    # 消えたツール
    for name in old_names - new_names:
        changes.append({
            "type": "removed",
            "name": name,
            "category": old_tools[name].get("category", "不明"),
        })

    # アクセス頻度の大幅変化（±50%以上）
    for name in old_names & new_names:
        old_count = old_tools[name].get("total_visits", old_tools[name].get("access_count", 0))
        new_count = new_tools[name].get("total_visits", new_tools[name].get("access_count", 0))
        if old_count > 0 and new_count > 0:
            ratio = new_count / old_count
            if ratio >= 1.5:
                changes.append({
                    "type": "increased",
                    "name": name,
                    "old_count": old_count,
                    "new_count": new_count,
                    "change": f"+{int((ratio - 1) * 100)}%",
                })
            elif ratio <= 0.5:
                changes.append({
                    "type": "decreased",
                    "name": name,
                    "old_count": old_count,
                    "new_count": new_count,
                    "change": f"{int((ratio - 1) * 100)}%",
                })

    return changes


def detect_task_changes(old_data, new_data):
    """業務一覧の変化を検出"""
    changes = []

    old_tasks = {t.get("name", ""): t for t in old_data.get("estimated_tasks", [])}
    new_tasks = {t.get("name", ""): t for t in new_data.get("estimated_tasks", [])}

    old_names = set(old_tasks.keys())
    new_names = set(new_tasks.keys())

    for name in new_names - old_names:
        changes.append({"type": "added", "name": name})

    for name in old_names - new_names:
        changes.append({"type": "removed", "name": name})

    return changes


# --- メイン ---

def main():
    # Windows (cp932) で stdout/stderr が UnicodeEncodeError になるのを防ぐ
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="収集データの保存・読み込み・差分検出")
    parser.add_argument("command", choices=["save", "load", "diff"], help="実行するコマンド")
    args = parser.parse_args()

    if args.command == "load":
        load()
        return

    # save / diff はstdinからJSONを受け取る
    if sys.stdin.isatty():
        print("エラー: stdinからJSONデータを入力してください", file=sys.stderr)
        print("例: echo '{...}' | python scripts/save_collection_data.py save", file=sys.stderr)
        sys.exit(1)

    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"エラー: 入力がJSON形式ではありません: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "save":
        save(input_data)
    elif args.command == "diff":
        diff(input_data)


if __name__ == "__main__":
    main()
