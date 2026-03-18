"""
Google Workspace 情報収集スクリプト（MCP非依存フォールバック）

Google Drive と Google Calendar の REST API を直接呼び出し、
業務把握に必要な情報をJSON形式で出力する。
MCP経由のGoogle Workspace接続が利用できない場合のフォールバックとして使用。

使い方:
  python scripts/collect_google_workspace.py --token ya29.ACCESS_TOKEN [--days 14] [--drive-limit 20] [--cal-limit 50]

必要なOAuth Scopes:
  - https://www.googleapis.com/auth/drive.readonly (Drive)
  - https://www.googleapis.com/auth/calendar.readonly (Calendar)

Access Token の取得方法:
  方法1: gcloud CLI
    gcloud auth application-default print-access-token
  方法2: OAuth Playground
    https://developers.google.com/oauthplayground/

出力: JSON（stdout）
エラー時は exit code 1 で stderr にメッセージを出力。
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone


# --- Google API 呼び出し ---

def google_api(url, token, params=None):
    """Google REST API を呼び出して結果を返す"""
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        if e.code == 401:
            raise RuntimeError(
                "認証エラー: Access Tokenが無効または期限切れです。"
                "トークンを再取得してください。"
            )
        raise RuntimeError(f"Google API エラー (HTTP {e.code}): {body[:200]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Google API 接続エラー: {e}")


# --- Drive 収集 ---

FILE_CATEGORY_KEYWORDS = {
    "進捗管理": ["進捗", "管理", "ステータス", "status", "tracking"],
    "議事録": ["議事録", "MTG", "meeting", "minutes", "ミーティング"],
    "報告書": ["報告", "レポート", "report", "日報", "週報", "月報"],
    "マニュアル": ["マニュアル", "手順", "ガイド", "manual", "guide", "howto"],
    "データ集計": ["集計", "分析", "売上", "analytics", "KPI", "数値"],
    "企画": ["企画", "提案", "計画", "plan", "proposal"],
    "請求・経理": ["請求", "見積", "経費", "invoice", "budget", "請求書"],
}

MIME_TYPE_LABELS = {
    "application/vnd.google-apps.spreadsheet": "スプレッドシート",
    "application/vnd.google-apps.document": "ドキュメント",
    "application/vnd.google-apps.presentation": "スライド",
    "application/vnd.google-apps.form": "フォーム",
    "application/vnd.google-apps.folder": "フォルダ",
    "application/pdf": "PDF",
}


def categorize_file(name):
    """ファイル名からカテゴリを推定"""
    name_lower = name.lower()
    for category, keywords in FILE_CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in name_lower:
                return category
    return "その他"


def get_mime_label(mime_type):
    """MIMEタイプを日本語ラベルに変換"""
    return MIME_TYPE_LABELS.get(mime_type, "ファイル")


def collect_drive(token, days, limit):
    """Google Drive の最近更新されたファイルを取得"""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    try:
        result = google_api(
            "https://www.googleapis.com/drive/v3/files",
            token,
            {
                "q": f"modifiedTime > '{cutoff}' and trashed = false",
                "orderBy": "modifiedTime desc",
                "pageSize": str(limit),
                "fields": "files(id,name,mimeType,modifiedTime,owners,shared,viewedByMeTime)",
            },
        )
    except RuntimeError as e:
        print(f"警告: Drive取得失敗: {e}", file=sys.stderr)
        return []

    files = []
    for f in result.get("files", []):
        # フォルダは除外
        if f.get("mimeType") == "application/vnd.google-apps.folder":
            continue

        name = f.get("name", "")
        files.append({
            "name": name[:100],
            "type": get_mime_label(f.get("mimeType", "")),
            "category": categorize_file(name),
            "modified": f.get("modifiedTime", ""),
            "viewed": f.get("viewedByMeTime", ""),
            "shared": f.get("shared", False),
        })

    return files


# --- Calendar 収集 ---

def collect_calendar(token, days, limit):
    """Google Calendar の直近イベントを取得"""
    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=days)).isoformat()
    time_max = now.isoformat()

    try:
        result = google_api(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            token,
            {
                "timeMin": time_min,
                "timeMax": time_max,
                "maxResults": str(limit),
                "singleEvents": "true",
                "orderBy": "startTime",
            },
        )
    except RuntimeError as e:
        print(f"警告: Calendar取得失敗: {e}", file=sys.stderr)
        return [], {}

    events = []
    pattern_counter = {}  # タイトルごとの出現回数で定例を検出

    for ev in result.get("items", []):
        # 終日イベントやキャンセル済みは除外
        if ev.get("status") == "cancelled":
            continue

        title = ev.get("summary", "(無題)")
        attendees = ev.get("attendees", [])
        start = ev.get("start", {})
        end = ev.get("end", {})

        # 所要時間を計算（分単位）
        duration_min = None
        start_dt = start.get("dateTime")
        end_dt = end.get("dateTime")
        if start_dt and end_dt:
            try:
                s = datetime.fromisoformat(start_dt)
                e = datetime.fromisoformat(end_dt)
                duration_min = int((e - s).total_seconds() / 60)
            except (ValueError, TypeError):
                pass

        # 定例パターン検出用
        title_key = title.strip().lower()
        pattern_counter[title_key] = pattern_counter.get(title_key, 0) + 1

        events.append({
            "title": title[:100],
            "start": start.get("dateTime", start.get("date", "")),
            "duration_min": duration_min,
            "attendee_count": len(attendees),
            "is_recurring": ev.get("recurringEventId") is not None,
        })

    # 定例パターンのサマリ
    recurring_patterns = {}
    for title_key, count in sorted(pattern_counter.items(), key=lambda x: x[1], reverse=True):
        if count >= 2:
            # 該当イベントの平均参加者数と平均時間
            matching = [e for e in events if e["title"].strip().lower() == title_key]
            avg_attendees = sum(e["attendee_count"] for e in matching) / len(matching)
            durations = [e["duration_min"] for e in matching if e["duration_min"] is not None]
            avg_duration = sum(durations) / len(durations) if durations else None

            frequency = "毎日" if count >= days * 0.7 else "毎週" if count >= days / 7 * 0.7 else f"{count}回/{days}日"

            recurring_patterns[matching[0]["title"]] = {
                "frequency": frequency,
                "count": count,
                "avg_attendees": round(avg_attendees, 1),
                "avg_duration_min": round(avg_duration) if avg_duration else None,
            }

    return events, recurring_patterns


# --- メイン ---

def main():
    # Windows (cp932) で stdout/stderr が UnicodeEncodeError になるのを防ぐ
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Google Workspace情報収集（REST API直接）")
    parser.add_argument("--token", required=True, help="Google OAuth Access Token (ya29.xxx)")
    parser.add_argument("--days", type=int, default=14, help="直近何日間を対象にするか（デフォルト: 14）")
    parser.add_argument("--drive-limit", type=int, default=20, help="Drive取得件数上限（デフォルト: 20）")
    parser.add_argument("--cal-limit", type=int, default=50, help="Calendar取得件数上限（デフォルト: 50）")
    parser.add_argument("--skip-drive", action="store_true", help="Drive収集をスキップ")
    parser.add_argument("--skip-calendar", action="store_true", help="Calendar収集をスキップ")
    args = parser.parse_args()

    result = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source": "google_workspace_api",
        "days": args.days,
    }

    # Drive
    if not args.skip_drive:
        files = collect_drive(args.token, args.days, args.drive_limit)
        result["drive_files"] = files
        result["drive_file_count"] = len(files)

        # カテゴリ別サマリ
        category_counts = {}
        for f in files:
            cat = f["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
        result["drive_categories"] = category_counts

    # Calendar
    if not args.skip_calendar:
        events, patterns = collect_calendar(args.token, args.days, args.cal_limit)
        result["calendar_events"] = events
        result["calendar_event_count"] = len(events)
        result["calendar_recurring_patterns"] = patterns

        # 会議時間の合計
        total_meeting_min = sum(
            e["duration_min"] for e in events if e["duration_min"] is not None
        )
        result["calendar_total_meeting_hours"] = round(total_meeting_min / 60, 1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
