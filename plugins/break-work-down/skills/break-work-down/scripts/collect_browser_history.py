#!/usr/bin/env python3
"""ブラウザ履歴からドメイン別アクセス頻度を取得し、業務ツールを推定する。

Usage:
    PYTHONUTF8=1 python collect_browser_history.py --browser chrome --days 14 --limit 50
    PYTHONUTF8=1 python collect_browser_history.py --browser edge --days 14 --limit 50
"""

import argparse
import json
import os
import platform
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

# --- ブラウザ履歴DBのパス検出 ---

def _detect_chrome_history() -> Path | None:
    """Chrome の History DB パスを検出する。"""
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", ""))
        candidates = [base / "Google/Chrome/User Data/Default/History"]
    elif system == "Darwin":
        candidates = [Path.home() / "Library/Application Support/Google/Chrome/Default/History"]
    else:  # Linux
        candidates = [Path.home() / ".config/google-chrome/Default/History"]
    return next((p for p in candidates if p.exists()), None)


def _detect_edge_history() -> Path | None:
    """Edge の History DB パスを検出する。"""
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", ""))
        candidates = [base / "Microsoft/Edge/User Data/Default/History"]
    elif system == "Darwin":
        candidates = [Path.home() / "Library/Application Support/Microsoft Edge/Default/History"]
    else:
        candidates = [Path.home() / ".config/microsoft-edge/Default/History"]
    return next((p for p in candidates if p.exists()), None)


def detect_history_db(browser: str) -> Path:
    """指定ブラウザの履歴DBパスを返す。見つからなければ終了。"""
    detectors = {"chrome": _detect_chrome_history, "edge": _detect_edge_history}
    detector = detectors.get(browser)
    if detector is None:
        print(f"Error: unknown browser '{browser}'. Use 'chrome' or 'edge'.", file=sys.stderr)
        sys.exit(1)
    path = detector()
    if path is None:
        print(f"Error: {browser} history DB not found.", file=sys.stderr)
        sys.exit(1)
    return path


# --- プライベートサイト除外 ---

PRIVATE_DOMAINS = {
    # SNS・動画・エンタメ
    "youtube.com", "facebook.com", "twitter.com", "x.com",
    "instagram.com", "reddit.com", "tiktok.com",
    "netflix.com", "spotify.com", "twitch.tv",
    "pixiv.net", "nicovideo.jp",
    # その他
    "linkedin.com", "localhost",
}

BUSINESS_CATEGORIES = {
    # SaaS / 業務ツール
    "salesforce.com": "CRM", "hubspot.com": "CRM",
    "slack.com": "チャット", "teams.microsoft.com": "チャット",
    "notion.so": "ナレッジ管理", "confluence.atlassian.net": "ナレッジ管理",
    "trello.com": "タスク管理", "asana.com": "タスク管理", "clickup.com": "タスク管理",
    "jira.atlassian.net": "プロジェクト管理", "backlog.com": "プロジェクト管理",
    "kintone.com": "業務アプリ", "cybozu.com": "グループウェア",
    "freee.co.jp": "会計", "moneyforward.com": "会計",
    "smarthr.jp": "人事労務", "jobcan.ne.jp": "勤怠管理",
    "docs.google.com": "ドキュメント", "sheets.google.com": "スプレッドシート",
    "drive.google.com": "クラウドストレージ",
    "calendar.google.com": "カレンダー", "outlook.office.com": "メール/カレンダー",
    "mail.google.com": "メール",
    "zoom.us": "ビデオ会議", "meet.google.com": "ビデオ会議",
    "figma.com": "デザイン", "canva.com": "デザイン",
    "github.com": "開発", "gitlab.com": "開発", "bitbucket.org": "開発",
    "chatwork.com": "チャット", "line.me": "チャット",
    "discord.com": "チャット", "telegram.org": "チャット",
    # 自動化
    "zapier.com": "自動化", "make.com": "自動化",
}


def extract_root_domain(url: str) -> str | None:
    """URLからルートドメインを抽出する。"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname
        if not host:
            return None
        # サブドメインを残す（sheets.google.com と drive.google.com を区別）
        return host.removeprefix("www.")
    except Exception:
        return None


def classify_domain(domain: str) -> str | None:
    """ドメインを業務カテゴリに分類する。プライベートなら None を返す。"""
    # 完全一致チェック
    if domain in BUSINESS_CATEGORIES:
        return BUSINESS_CATEGORIES[domain]
    # ルートドメインでプライベート判定
    parts = domain.split(".")
    for i in range(len(parts) - 1):
        root = ".".join(parts[i:])
        if root in PRIVATE_DOMAINS:
            return None
        if root in BUSINESS_CATEGORIES:
            return BUSINESS_CATEGORIES[root]
    # 不明なドメインは「その他」として残す（業務ツールの可能性がある）
    return "その他"


# --- メイン処理 ---

def collect(db_path: Path, days: int, limit: int) -> list[dict]:
    """履歴DBからドメイン別アクセス頻度を集計する。"""
    # ブラウザ起動中のロックを回避するため一時コピー
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite")
    tmp.close()
    try:
        # SQLite backup API 経由でコピー
        src = sqlite3.connect(f"file:{db_path}?mode=ro&nolock=1", uri=True)
        dst = sqlite3.connect(tmp.name)
        src.backup(dst)
        src.close()
        dst.close()

        conn = sqlite3.connect(tmp.name)
        # Chromium の timestamps は 1601-01-01 からのマイクロ秒
        epoch_diff = 11644473600  # 1601→1970 の秒差
        cutoff_us = (
            int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp()) + epoch_diff
        ) * 1_000_000

        cursor = conn.execute(
            """
            SELECT url, visit_count
            FROM urls
            WHERE last_visit_time >= ?
            ORDER BY visit_count DESC
            """,
            (cutoff_us,),
        )

        domain_stats: dict[str, dict] = {}
        for url, visit_count in cursor:
            domain = extract_root_domain(url)
            if not domain:
                continue
            category = classify_domain(domain)
            if category is None:  # プライベート
                continue
            if domain not in domain_stats:
                domain_stats[domain] = {"domain": domain, "category": category, "visits": 0}
            domain_stats[domain]["visits"] += visit_count

        conn.close()

        # 上位N件を返す
        sorted_stats = sorted(domain_stats.values(), key=lambda x: x["visits"], reverse=True)
        return sorted_stats[:limit]
    finally:
        os.unlink(tmp.name)


def main():
    parser = argparse.ArgumentParser(
        description="ブラウザ履歴からドメイン別アクセス頻度を取得し、業務ツールを推定する"
    )
    parser.add_argument(
        "--browser", required=True, choices=["chrome", "edge"],
        help="対象ブラウザ（chrome / edge）"
    )
    parser.add_argument(
        "--days", type=int, default=14,
        help="何日前までの履歴を取得するか（デフォルト: 14）"
    )
    parser.add_argument(
        "--limit", type=int, default=50,
        help="上位何件のドメインを出力するか（デフォルト: 50）"
    )
    args = parser.parse_args()

    db_path = detect_history_db(args.browser)
    results = collect(db_path, args.days, args.limit)

    output = {
        "browser": args.browser,
        "days": args.days,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "domains": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
