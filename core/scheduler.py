import os
import requests


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_message(text: str):
    """
    Send message to Telegram bot
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("[!] Telegram not configured (BOT_TOKEN or CHAT_ID missing)")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, data=payload, timeout=10)

        if response.status_code != 200:
            print(f"[!] Telegram API error: {response.text}")

    except Exception as e:
        print(f"[!] Telegram request failed: {e}")


def format_alert(project: dict, ai_result: dict) -> str:
    """
    Format ScoutXAI alert message
    """

    name = project.get("name", "Unknown Project")
    url = project.get("url", "No URL")
    score = ai_result.get("score", 0)
    risks = ai_result.get("risks", [])
    signals = ai_result.get("signals", [])

    msg = f"""🚨 <b>ScoutXAI Security Alert</b>

📦 <b>Project:</b> {name}
⭐ <b>AI Score:</b> {score}/100

"""

    if signals:
        msg += "🧠 <b>Signals:</b>\n"
        for s in signals:
            msg += f"• {s}\n"
        msg += "\n"

    if risks:
        msg += "⚠️ <b>Risks:</b>\n"
        for r in risks:
            msg += f"• {r}\n"
        msg += "\n"
    else:
        msg += "⚠️ <b>Risks:</b> None detected\n\n"

    msg += f"🔗 <b>URL:</b> {url}"

    return msg
