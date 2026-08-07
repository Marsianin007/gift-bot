"""Pull new Telegram messages from the owner and queue them for the agent.

Usage: python scripts/check_owner_messages.py

Reads PROMO_BOT_TOKEN and OWNER_CHAT_ID from the environment. Each cron
session is stateless (fresh clone), so the Telegram update offset is kept
in .telegram_offset and committed to git — that's what makes "only new
messages" work across sessions. New messages are appended to INBOX.md as
unchecked TODO items for the agent to read and act on this session.
"""
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
OFFSET_FILE = ROOT / ".telegram_offset"
INBOX_FILE = ROOT / "INBOX.md"


def main() -> None:
    token = os.getenv("PROMO_BOT_TOKEN")
    owner_id = os.getenv("OWNER_CHAT_ID")
    if not token or not owner_id:
        print("check_owner_messages: PROMO_BOT_TOKEN/OWNER_CHAT_ID not set, skipping")
        return

    offset = int(OFFSET_FILE.read_text().strip()) if OFFSET_FILE.exists() else 0
    resp = requests.get(
        f"https://api.telegram.org/bot{token}/getUpdates",
        params={"offset": offset},
        timeout=30,
    )
    resp.raise_for_status()
    updates = resp.json()["result"]

    new_messages = []
    max_update_id = offset - 1
    for u in updates:
        max_update_id = max(max_update_id, u["update_id"])
        msg = u.get("message")
        if not msg or str(msg.get("from", {}).get("id")) != str(owner_id):
            continue
        text = msg.get("text")
        if text:
            new_messages.append(text)

    if new_messages:
        with open(INBOX_FILE, "a", encoding="utf-8") as f:
            for text in new_messages:
                f.write(f"- [ ] {text}\n")
        print(f"check_owner_messages: {len(new_messages)} new message(s) added to INBOX.md")
    else:
        print("check_owner_messages: no new messages")

    OFFSET_FILE.write_text(str(max_update_id + 1))


if __name__ == "__main__":
    main()
