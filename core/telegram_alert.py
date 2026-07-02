import os
import requests


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("[!] Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            print(f"[!] Telegram error: {r.text}")
    except Exception as e:
        print(f"[!] Telegram exception: {e}")


def format_alert(project, ai_result):
    name = project.get("name", "Unknown")
    url = project.get("url", "")
    score = ai_result.get("score", 0)
    risks = ai_result.get("risks", [])

    msg = f"""
🚨 <b>ScoutXAI Alert</b>

📦 Project: {name}
⭐ Score: {score}

⚠ Risks:
"""

    if risks:
        for r in risks:
            msg += f"- {r}\n"
    else:
        msg += "- No major risks detected\n"

    msg += f"\n🔗 {url}"

    return msg
