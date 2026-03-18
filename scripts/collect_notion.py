"""
Notion 情報収集スクリプト（MCP非依存フォールバック）

Notion REST API を直接呼び出し、業務把握に必要な情報をJSON形式で出力する。
MCP経由のNotion接続が利用できない場合のフォールバックとして使用。

使い方:
  python scripts/collect_notion.py --token ntn_YOUR_TOKEN [--limit 20]

必要な権限:
  - Notionインテグレーションの作成と、対象ページへの接続（共有）が必要
  - https://www.notion.so/profile/integrations で作成

出力: JSON（stdout）
エラー時は exit code 1 で stderr にメッセージを出力。
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"


# --- Notion API 呼び出し ---

def notion_api(method, path, token, body=None):
    """Notion REST API を呼び出して結果を返す"""
    url = f"{NOTION_BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_API_VERSION,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        if e.code == 401:
            raise RuntimeError(
                "認証エラー: Notionトークンが無効です。"
                "https://www.notion.so/profile/integrations でトークンを確認してください。"
            )
        if e.code == 403:
            raise RuntimeError(
                "権限エラー: インテグレーションに対象ページが共有されていません。"
                "Notionのページメニュー →「接続を追加」でインテグレーションを追加してください。"
            )
        raise RuntimeError(f"Notion API エラー (HTTP {e.code}): {error_body[:200]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Notion API 接続エラー: {e}")


# --- ページ / データベース収集 ---

PAGE_CATEGORY_KEYWORDS = {
    "議事録": ["議事録", "MTG", "meeting", "ミーティング", "minutes"],
    "タスク管理": ["タスク", "todo", "task", "backlog", "sprint", "カンバン"],
    "マニュアル": ["マニュアル", "手順", "ガイド", "manual", "how-to", "wiki"],
    "プロジェクト": ["プロジェクト", "project", "ロードマップ", "roadmap"],
    "ナレッジ": ["ナレッジ", "知見", "tips", "FAQ", "ノウハウ"],
    "日報・報告": ["日報", "週報", "月報", "報告", "report", "振り返り"],
    "企画": ["企画", "提案", "計画", "plan", "proposal"],
}


def categorize_page(title):
    """ページタイトルからカテゴリを推定"""
    title_lower = title.lower()
    for category, keywords in PAGE_CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                return category
    return "その他"


def search_pages(token, limit):
    """ワークスペース内のページとデータベースを検索"""
    pages = []
    databases = []

    try:
        result = notion_api("POST", "/search", token, {
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time",
            },
            "page_size": min(limit, 100),
        })
    except RuntimeError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return pages, databases

    for item in result.get("results", []):
        obj_type = item.get("object")

        if obj_type == "page":
            title = extract_title(item)
            pages.append({
                "id": item["id"],
                "title": title[:100],
                "category": categorize_page(title),
                "last_edited": item.get("last_edited_time", ""),
                "created": item.get("created_time", ""),
                "url": item.get("url", ""),
                "parent_type": item.get("parent", {}).get("type", ""),
            })

        elif obj_type == "database":
            title = extract_database_title(item)
            # データベースのプロパティ（スキーマ）を取得
            properties = {}
            for prop_name, prop_data in item.get("properties", {}).items():
                properties[prop_name] = prop_data.get("type", "unknown")

            databases.append({
                "id": item["id"],
                "title": title[:100],
                "category": categorize_page(title),
                "last_edited": item.get("last_edited_time", ""),
                "url": item.get("url", ""),
                "property_count": len(properties),
                "properties": properties,
            })

    return pages, databases


def extract_title(page):
    """ページオブジェクトからタイトルを抽出"""
    props = page.get("properties", {})

    # "title" タイプのプロパティを探す
    for prop_name, prop_data in props.items():
        if prop_data.get("type") == "title":
            title_parts = prop_data.get("title", [])
            if title_parts:
                return "".join(part.get("plain_text", "") for part in title_parts)

    # フォールバック: Name プロパティ
    name_prop = props.get("Name", props.get("name", {}))
    if name_prop.get("type") == "title":
        title_parts = name_prop.get("title", [])
        if title_parts:
            return "".join(part.get("plain_text", "") for part in title_parts)

    return "(無題)"


def extract_database_title(db):
    """データベースオブジェクトからタイトルを抽出"""
    title_parts = db.get("title", [])
    if title_parts:
        return "".join(part.get("plain_text", "") for part in title_parts)
    return "(無題データベース)"


def get_page_content_summary(token, page_id):
    """ページのブロック内容を取得し、先頭部分のサマリを返す"""
    try:
        result = notion_api("GET", f"/blocks/{page_id}/children", token)
    except RuntimeError:
        return ""

    texts = []
    for block in result.get("results", [])[:10]:  # 先頭10ブロックのみ
        block_type = block.get("type", "")
        block_data = block.get(block_type, {})

        # リッチテキストを含むブロックからテキストを抽出
        rich_texts = block_data.get("rich_text", [])
        if rich_texts:
            text = "".join(rt.get("plain_text", "") for rt in rich_texts)
            if text.strip():
                texts.append(text.strip()[:200])

    return " / ".join(texts)[:500]


def query_database_entries(token, database_id, limit=5):
    """データベースの直近エントリを取得"""
    try:
        result = notion_api("POST", f"/databases/{database_id}/query", token, {
            "sorts": [{"timestamp": "last_edited_time", "direction": "descending"}],
            "page_size": min(limit, 10),
        })
    except RuntimeError:
        return []

    entries = []
    for page in result.get("results", []):
        title = extract_title(page)
        entries.append({
            "title": title[:100],
            "last_edited": page.get("last_edited_time", ""),
        })

    return entries


# --- メイン ---

def main():
    # Windows (cp932) で stdout/stderr が UnicodeEncodeError になるのを防ぐ
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Notion情報収集（REST API直接）")
    parser.add_argument("--token", required=True, help="Notion Integration Token (ntn_xxx または secret_xxx)")
    parser.add_argument("--limit", type=int, default=20, help="取得するページ/DB数の上限（デフォルト: 20）")
    parser.add_argument("--include-content", action="store_true",
                        help="上位ページの内容サマリを取得する（API呼び出し増加）")
    parser.add_argument("--include-entries", action="store_true",
                        help="データベースの直近エントリを取得する（API呼び出し増加）")
    args = parser.parse_args()

    # トークン形式の簡易チェック
    if not args.token.startswith(("ntn_", "secret_")):
        print(
            "警告: トークンが ntn_ または secret_ で始まっていません。"
            "Notionインテグレーションのトークンを使用してください。",
            file=sys.stderr,
        )

    # 1. ページとデータベースを検索
    pages, databases = search_pages(args.token, args.limit)

    # 2. オプション: 上位ページの内容サマリ
    if args.include_content and pages:
        for page in pages[:5]:  # 上位5ページのみ
            page["content_summary"] = get_page_content_summary(args.token, page["id"])

    # 3. オプション: データベースの直近エントリ
    if args.include_entries and databases:
        for db in databases[:3]:  # 上位3DBのみ
            db["recent_entries"] = query_database_entries(args.token, db["id"])

    # 4. カテゴリ別サマリ
    page_categories = {}
    for p in pages:
        cat = p["category"]
        page_categories[cat] = page_categories.get(cat, 0) + 1

    db_categories = {}
    for d in databases:
        cat = d["category"]
        db_categories[cat] = db_categories.get(cat, 0) + 1

    # 5. 出力
    result = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source": "notion_api",
        "pages": pages,
        "page_count": len(pages),
        "page_categories": page_categories,
        "databases": databases,
        "database_count": len(databases),
        "database_categories": db_categories,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
