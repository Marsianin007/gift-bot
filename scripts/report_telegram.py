"""Send a session report to the project owner on Telegram.

Usage:
    python scripts/report_telegram.py "text summary" [image.png ...]

Reads PROMO_BOT_TOKEN and OWNER_CHAT_ID from the environment (.env via
python-dotenv). Silently no-ops if either is missing — reporting is
best-effort, never a build blocker.
"""
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    token = os.getenv("PROMO_BOT_TOKEN")
    chat_id = os.getenv("OWNER_CHAT_ID")
    if not token or not chat_id:
        print("report_telegram: PROMO_BOT_TOKEN/OWNER_CHAT_ID not set, skipping")
        return

    if len(sys.argv) < 2:
        print("usage: report_telegram.py <text> [image ...]")
        return

    text, images = sys.argv[1], sys.argv[2:]
    api = f"https://api.telegram.org/bot{token}"

    requests.post(f"{api}/sendMessage", data={"chat_id": chat_id, "text": text}, timeout=30)

    for path in images:
        with open(path, "rb") as f:
            requests.post(f"{api}/sendPhoto", data={"chat_id": chat_id}, files={"photo": f}, timeout=30)


if __name__ == "__main__":
    main()
