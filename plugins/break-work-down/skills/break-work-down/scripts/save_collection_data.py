#!/usr/bin/env python3
"""収集データの保存・読み込み・差分検出・リセットを行うユーティリティ。

Usage:
    echo '<JSON>' | PYTHONUTF8=1 python save_collection_data.py save
    PYTHONUTF8=1 python save_collection_data.py load
    echo '<JSON>' | PYTHONUTF8=1 python save_collection_data.py diff
    PYTHONUTF8=1 python save_collection_data.py reset
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# data/ ディレクトリは scripts/ の兄弟
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
LATEST_PATH = DATA_DIR / "latest.json"
CONFIG_PATH = DATA_DIR / "config.json"

DEFAULT_CONFIG = {
    "_comment": "スキル実行時の永続設定。初回実行時にAskUserQuestionで取得し、以降は再利用する。手動編集も可。",
    "messaging_priority_channels": [],
    "constraints": [],
    "browser": "",
    "browser_use": {
        "enabled": False,
        "allowed_domains": [],
        "denied_domains": [],
        "login_method": "user_manual",
    },
}


def cmd_save():
    """stdinからJSONを読み、日付入りスナップショット + latest.json に保存する。"""
    raw = sys.stdin.read().strip()
    if not raw:
        print("Error: no JSON data on stdin.", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 日付入りスナップショット
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot_path = DATA_DIR / f"collection_{date_str}.json"
    snapshot_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # latest.json を上書き
    LATEST_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": "saved",
        "snapshot": str(snapshot_path),
        "latest": str(LATEST_PATH),
    }, ensure_ascii=False, indent=2))


def cmd_load():
    """latest.json を読み込んで stdout に出力する。"""
    if not LATEST_PATH.exists():
        print(json.dumps({"status": "no_data", "message": "latest.json が存在しません。初回実行です。"}))
        return
    data = json.loads(LATEST_PATH.read_text(encoding="utf-8"))
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_diff():
    """stdinの新データと latest.json を比較し、差分サマリーを出力する。"""
    raw = sys.stdin.read().strip()
    if not raw:
        print("Error: no JSON data on stdin.", file=sys.stderr)
        sys.exit(1)
    try:
        new_data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)

    if not LATEST_PATH.exists():
        print(json.dumps({
            "status": "no_previous_data",
            "message": "前回データなし。差分検出をスキップします。",
        }, ensure_ascii=False, indent=2))
        return

    old_data = json.loads(LATEST_PATH.read_text(encoding="utf-8"))
    diff = _compute_diff(old_data, new_data)
    print(json.dumps(diff, ensure_ascii=False, indent=2))


def _compute_diff(old: dict, new: dict) -> dict:
    """2つの収集データの差分を算出する。"""
    result: dict = {
        "status": "diff",
        "previous_date": old.get("collected_at", "unknown"),
        "current_date": new.get("collected_at", "unknown"),
        "changes": [],
    }

    # ツール環境の差分
    old_tools = {t["name"] for t in old.get("tool_environment", [])}
    new_tools = {t["name"] for t in new.get("tool_environment", [])}
    added_tools = new_tools - old_tools
    removed_tools = old_tools - new_tools
    if added_tools:
        result["changes"].append({"type": "tools_added", "items": sorted(added_tools)})
    if removed_tools:
        result["changes"].append({"type": "tools_removed", "items": sorted(removed_tools)})

    # 推定タスクの差分
    old_tasks = {t["name"] for t in old.get("estimated_tasks", [])}
    new_tasks = {t["name"] for t in new.get("estimated_tasks", [])}
    added_tasks = new_tasks - old_tasks
    removed_tasks = old_tasks - new_tasks
    if added_tasks:
        result["changes"].append({"type": "tasks_added", "items": sorted(added_tasks)})
    if removed_tasks:
        result["changes"].append({"type": "tasks_removed", "items": sorted(removed_tasks)})

    # ソースの差分
    old_sources = set(old.get("sources", []))
    new_sources = set(new.get("sources", []))
    added_sources = new_sources - old_sources
    removed_sources = old_sources - new_sources
    if added_sources:
        result["changes"].append({"type": "sources_added", "items": sorted(added_sources)})
    if removed_sources:
        result["changes"].append({"type": "sources_removed", "items": sorted(removed_sources)})

    # 前回の confirmed_question
    prev_question = old.get("confirmed_question")
    if prev_question:
        result["previous_confirmed_question"] = prev_question

    if not result["changes"]:
        result["changes"].append({"type": "no_significant_changes"})

    return result


def cmd_reset():
    """config.json を初期化し、collection_*.json と latest.json を削除する。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # config.json を初期化
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")

    # collection_*.json と latest.json を削除
    deleted = []
    for f in DATA_DIR.glob("collection_*.json"):
        f.unlink()
        deleted.append(f.name)
    if LATEST_PATH.exists():
        LATEST_PATH.unlink()
        deleted.append("latest.json")

    print(json.dumps({
        "status": "reset",
        "config_reset": True,
        "deleted_files": deleted,
    }, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="収集データの保存・読み込み・差分検出・リセット"
    )
    parser.add_argument(
        "command", choices=["save", "load", "diff", "reset"],
        help="実行するコマンド"
    )
    args = parser.parse_args()

    commands = {
        "save": cmd_save,
        "load": cmd_load,
        "diff": cmd_diff,
        "reset": cmd_reset,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
