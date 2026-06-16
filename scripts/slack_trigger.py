import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "")
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ["GITHUB_REPO"]

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)


def trigger_github_workflow(memo: str, platforms: str = "all") -> bool:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "event_type": "generate-note",
        "client_payload": {
            "memo": memo,
            "platforms": platforms,
        },
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code == 204


@app.command("/note")
def handle_note_command(ack, respond, command):
    ack()

    text = command.get("text", "").strip()

    platforms = "all"
    memo = text

    if text.lower().startswith("platforms:"):
        parts = text.split(" ", 1)
        platforms = parts[0].replace("platforms:", "").strip()
        memo = parts[1].strip() if len(parts) > 1 else ""

    if trigger_github_workflow(memo, platforms):
        respond(
            f"記事生成を開始しました。\nメモ: {memo or '(なし)'}\nプラットフォーム: {platforms}\n\nGitHub Actionsで処理中です。完了後に通知します。"
        )
    else:
        respond("エラーが発生しました。GitHub Actionsのトリガーに失敗しました。設定を確認してください。")


if __name__ == "__main__":
    if SLACK_APP_TOKEN:
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
    else:
        app.start(port=int(os.environ.get("PORT", 3000)))
