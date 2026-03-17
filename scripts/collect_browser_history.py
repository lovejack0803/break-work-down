"""
ブラウザ履歴収集スクリプト

Chrome / Edge の履歴DBから直近N日間のアクセス頻度上位を取得し、
ドメイン別にカテゴリ分類してJSON形式で出力する。

使い方:
  python scripts/collect_browser_history.py [--days 14] [--limit 50] [--browser chrome|edge|auto]

出力: JSON（stdout）
  {
    "collected_at": "...",
    "browser": "chrome",
    "days": 14,
    "domains": [ { "domain": "...", "total_visits": 123, "category": "...", "top_pages": [...] } ],
    "raw_count": 50
  }

エラー時は exit code 1 で stderr にメッセージを出力。
"""

import argparse
import json
import os
import platform
import shutil
import sqlite3
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


# --- ブラウザ履歴DBのパス検出 ---

def find_history_paths():
    """OS・ブラウザごとの履歴DBパスを返す"""
    system = platform.system()
    home = Path.home()
    candidates = {}

    if system == "Windows":
        local = home / "AppData" / "Local"
        candidates["chrome"] = local / "Google" / "Chrome" / "User Data" / "Default" / "History"
        candidates["edge"] = local / "Microsoft" / "Edge" / "User Data" / "Default" / "History"
    elif system == "Darwin":
        candidates["chrome"] = home / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "History"
        candidates["edge"] = home / "Library" / "Application Support" / "Microsoft Edge" / "Default" / "History"
    else:  # Linux
        candidates["chrome"] = home / ".config" / "google-chrome" / "Default" / "History"
        candidates["edge"] = home / ".config" / "microsoft-edge" / "Default" / "History"

    return {k: v for k, v in candidates.items() if v.exists()}


def select_browser(available, preference):
    """使用するブラウザを選択"""
    if preference == "auto":
        # Chrome優先、なければEdge
        for browser in ["chrome", "edge"]:
            if browser in available:
                return browser, available[browser]
        return None, None
    elif preference in available:
        return preference, available[preference]
    return None, None


# --- 履歴DBの読み取り ---

def query_history(db_path, days, limit):
    """履歴DBをコピーしてクエリ実行。結果をリストで返す"""
    # ブラウザ起動中はDBがロックされるため、一時ファイルにコピー
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(tmp_fd)

    try:
        shutil.copy2(str(db_path), tmp_path)
    except (PermissionError, OSError) as e:
        os.unlink(tmp_path)
        raise RuntimeError(f"履歴DBのコピーに失敗しました（ブラウザが起動中の可能性があります）: {e}")

    try:
        conn = sqlite3.connect(tmp_path)
        conn.text_factory = str
        cursor = conn.cursor()

        # Chrome/Edgeの last_visit_time は Windows FILETIME epoch (1601-01-01) をマイクロ秒で格納
        # Unix epoch との差分: 11644473600 秒
        chrome_epoch_offset = 11644473600
        cutoff = f"(strftime('%s','now','-{days} days')+{chrome_epoch_offset})*1000000"

        cursor.execute(f"""
            SELECT url, title, visit_count,
                   datetime(last_visit_time/1000000-{chrome_epoch_offset},'unixepoch','localtime') as last_visit
            FROM urls
            WHERE last_visit_time > {cutoff}
            ORDER BY visit_count DESC
            LIMIT {limit}
        """)

        rows = cursor.fetchall()
        conn.close()
        return rows
    finally:
        os.unlink(tmp_path)


# --- ドメイン分類 ---

# 業務ツールのドメインパターン → カテゴリ
DOMAIN_CATEGORIES = {
    # SaaS / プロジェクト管理
    "wrike.com": "プロジェクト管理",
    "asana.com": "プロジェクト管理",
    "trello.com": "プロジェクト管理",
    "monday.com": "プロジェクト管理",
    "linear.app": "プロジェクト管理",
    "clickup.com": "プロジェクト管理",
    # コミュニケーション
    "slack.com": "コミュニケーション",
    "teams.microsoft.com": "コミュニケーション",
    "discord.com": "コミュニケーション",
    "zoom.us": "コミュニケーション",
    "meet.google.com": "コミュニケーション",
    "ovice.com": "コミュニケーション",
    # ドキュメント / ナレッジ
    "docs.google.com": "ドキュメント",
    "sheets.google.com": "ドキュメント",
    "notion.site": "ナレッジ管理",
    "notion.so": "ナレッジ管理",
    "confluence.atlassian.com": "ナレッジ管理",
    # AI
    "chatgpt.com": "AI",
    "chat.openai.com": "AI",
    "claude.ai": "AI",
    "gemini.google.com": "AI",
    "perplexity.ai": "AI",
    # 文章校正
    "enno.jp": "文章校正",
    "bun-ken.net": "文章校正",
    # CMS
    "wordpress.com": "CMS",
    "wp-admin": "CMS",
    # 経費・勤怠
    "freee.co.jp": "経費・勤怠",
    "secure.freee.co.jp": "経費・勤怠",
    "moneyforward.com": "経費・勤怠",
    # 自動化
    "n8n.io": "ワークフロー自動化",
    "zapier.com": "ワークフロー自動化",
    "make.com": "ワークフロー自動化",
    # 情報収集
    "x.com": "情報収集",
    "twitter.com": "情報収集",
}

# プライベート判定用（除外対象）
PRIVATE_DOMAINS = {
    "youtube.com", "netflix.com", "amazon.co.jp", "rakuten.co.jp",
    "yahoo.co.jp", "facebook.com", "instagram.com", "tiktok.com",
    "reddit.com", "pornhub.com", "xvideos.com",
}


def categorize_domain(domain, url=""):
    """ドメインからカテゴリを推定"""
    domain_lower = domain.lower()

    # プライベート除外
    for private in PRIVATE_DOMAINS:
        if private in domain_lower:
            return None  # 除外

    # 既知カテゴリ
    for pattern, category in DOMAIN_CATEGORIES.items():
        if pattern in domain_lower:
            return category

    # WordPress管理画面
    if "/wp-admin" in url or "/wp/wp-admin" in url:
        return "CMS"

    # n8nの自社ホスト
    if "n8n" in domain_lower:
        return "ワークフロー自動化"

    # Google系
    if "google.com" in domain_lower or "google.co.jp" in domain_lower:
        return "Google Workspace"

    # その他のlocalhostやイントラ
    if "localhost" in domain_lower or "127.0.0.1" in domain_lower:
        return None  # 除外

    return "その他"


def group_by_domain(rows):
    """URLリストをドメイン別にグルーピング"""
    domain_data = defaultdict(lambda: {"total_visits": 0, "pages": []})

    for url, title, visit_count, last_visit in rows:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            if not domain:
                continue

            category = categorize_domain(domain, url)
            if category is None:
                continue  # プライベート除外

            domain_data[domain]["total_visits"] += visit_count
            domain_data[domain]["category"] = category
            domain_data[domain]["pages"].append({
                "title": (title or "")[:100],
                "visits": visit_count,
            })
        except Exception:
            continue

    # ソートして上位を返す
    result = []
    for domain, data in sorted(domain_data.items(), key=lambda x: x[1]["total_visits"], reverse=True):
        top_pages = sorted(data["pages"], key=lambda p: p["visits"], reverse=True)[:5]
        result.append({
            "domain": domain,
            "total_visits": data["total_visits"],
            "category": data["category"],
            "top_pages": top_pages,
        })

    return result


# --- メイン ---

def main():
    parser = argparse.ArgumentParser(description="ブラウザ履歴を収集しJSON出力")
    parser.add_argument("--days", type=int, default=14, help="直近何日間を対象にするか（デフォルト: 14）")
    parser.add_argument("--limit", type=int, default=50, help="取得する上位件数（デフォルト: 50）")
    parser.add_argument("--browser", choices=["chrome", "edge", "auto"], default="auto", help="対象ブラウザ（デフォルト: auto）")
    args = parser.parse_args()

    # 1. ブラウザ検出
    available = find_history_paths()
    if not available:
        print("エラー: Chrome/Edgeの履歴DBが見つかりません", file=sys.stderr)
        sys.exit(1)

    browser, db_path = select_browser(available, args.browser)
    if browser is None:
        print(f"エラー: 指定されたブラウザ '{args.browser}' の履歴DBが見つかりません", file=sys.stderr)
        print(f"利用可能: {list(available.keys())}", file=sys.stderr)
        sys.exit(1)

    # 2. 履歴取得
    try:
        rows = query_history(db_path, args.days, args.limit)
    except RuntimeError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        print("警告: 指定期間内の履歴が見つかりません", file=sys.stderr)
        result = {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "browser": browser,
            "days": args.days,
            "domains": [],
            "raw_count": 0,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    # 3. ドメイン分類
    domains = group_by_domain(rows)

    # 4. JSON出力
    result = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "browser": browser,
        "days": args.days,
        "domains": domains,
        "raw_count": len(rows),
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
