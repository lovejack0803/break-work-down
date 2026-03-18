"""
Slack情報収集スクリプト（MCP非依存フォールバック）

Slack Web APIを直接呼び出し、業務把握に必要な情報をJSON形式で出力する。
MCP経由のSlack接続が利用できない場合のフォールバックとして使用。

使い方:
  python scripts/collect_slack.py --token xoxb-YOUR-BOT-TOKEN [--days 14] [--limit 20]

必要なBot Token Scopes:
  - channels:read, channels:history
  - groups:read, groups:history (プライベートチャンネル)
  - users:read
  - search:read (検索機能を使う場合)

出力: JSON（stdout）
エラー時は exit code 1 で stderr にメッセージを出力。
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta


# --- Slack Web API 呼び出し ---

def slack_api(method, token, params=None):
    """Slack Web API を呼び出して結果を返す"""
    url = f"https://slack.com/api/{method}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = None
    if params:
        data = urllib.parse.urlencode(params).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"Slack API呼び出しに失敗しました ({method}): {e}")

    if not body.get("ok"):
        error = body.get("error", "unknown")
        raise RuntimeError(f"Slack APIエラー ({method}): {error}")

    return body


# --- 収集処理 ---

def get_user_profile(token):
    """認証ユーザーの情報を取得"""
    try:
        resp = slack_api("auth.test", token)
        user_id = resp.get("user_id")
        user_resp = slack_api("users.info", token, {"user": user_id})
        profile = user_resp.get("user", {}).get("profile", {})
        return {
            "user_id": user_id,
            "name": profile.get("real_name", ""),
            "title": profile.get("title", ""),
            "email": profile.get("email", ""),
            "team": resp.get("team", ""),
        }
    except RuntimeError:
        return None


def get_channels(token, limit=50):
    """参加チャンネル一覧を取得"""
    channels = []
    try:
        # パブリックチャンネル
        resp = slack_api("conversations.list", token, {
            "types": "public_channel,private_channel",
            "exclude_archived": "true",
            "limit": str(limit),
        })
        for ch in resp.get("channels", []):
            if ch.get("is_member"):
                channels.append({
                    "id": ch["id"],
                    "name": ch.get("name", ""),
                    "is_private": ch.get("is_private", False),
                    "num_members": ch.get("num_members", 0),
                    "purpose": ch.get("purpose", {}).get("value", "")[:100],
                })
    except RuntimeError as e:
        print(f"警告: チャンネル一覧取得失敗: {e}", file=sys.stderr)

    return channels


def get_recent_messages(token, channel_id, days=14, limit=100):
    """チャンネルの直近メッセージを取得"""
    oldest = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    try:
        resp = slack_api("conversations.history", token, {
            "channel": channel_id,
            "oldest": str(oldest),
            "limit": str(limit),
        })
        messages = resp.get("messages", [])
        return messages
    except RuntimeError:
        return []


def analyze_messages(messages, user_id):
    """メッセージからパターンを抽出"""
    user_msg_count = 0
    total_count = len(messages)
    keywords = {}
    keyword_list = ["依頼", "確認", "報告", "議事録", "レポート", "完了", "対応", "修正", "承認", "共有"]

    for msg in messages:
        text = msg.get("text", "")
        if msg.get("user") == user_id:
            user_msg_count += 1
        for kw in keyword_list:
            if kw in text:
                keywords[kw] = keywords.get(kw, 0) + 1

    return {
        "total_messages": total_count,
        "user_messages": user_msg_count,
        "top_keywords": dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]),
    }


def collect(token, days, channel_limit):
    """メイン収集処理"""
    result = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source": "slack_api",
        "days": days,
        "user_profile": None,
        "channels": [],
        "channel_analysis": [],
    }

    # 1. ユーザー情報
    profile = get_user_profile(token)
    if profile:
        result["user_profile"] = profile

    # 2. チャンネル一覧
    channels = get_channels(token)
    result["channels"] = channels

    if not profile:
        return result

    user_id = profile["user_id"]

    # 3. メンバー数が多い or 名前から業務チャンネルを推定し、上位を分析
    # メンバー数順にソートし、上位N件を取得
    sorted_channels = sorted(channels, key=lambda c: c.get("num_members", 0), reverse=True)
    target_channels = sorted_channels[:min(channel_limit, len(sorted_channels))]

    for ch in target_channels:
        messages = get_recent_messages(token, ch["id"], days=days)
        if not messages:
            continue
        analysis = analyze_messages(messages, user_id)
        result["channel_analysis"].append({
            "channel_id": ch["id"],
            "channel_name": ch["name"],
            **analysis,
        })

    return result


# --- メイン ---

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Slack情報収集（Web API直接）")
    parser.add_argument("--token", required=True, help="Slack Bot Token (xoxb-...)")
    parser.add_argument("--days", type=int, default=14, help="直近何日間を対象にするか（デフォルト: 14）")
    parser.add_argument("--limit", type=int, default=5, help="分析するチャンネル数上限（デフォルト: 5）")
    args = parser.parse_args()

    if not args.token.startswith(("xoxb-", "xoxp-")):
        print("エラー: トークンは xoxb- または xoxp- で始まる必要があります", file=sys.stderr)
        sys.exit(1)

    try:
        result = collect(args.token, args.days, args.limit)
    except RuntimeError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
