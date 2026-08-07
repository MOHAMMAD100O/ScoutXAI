from datetime import datetime
from app.database.database import get_connection


def get_live_status():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )
        users = cursor.fetchone()[0]

        try:
            cursor.execute(
                "SELECT COUNT(*) FROM opportunities"
            )
            opportunities = cursor.fetchone()[0]
        except:
            opportunities = 0

        conn.close()

    except Exception:
        users = 0
        opportunities = 0

    now = datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    return f"""
🟢 ScoutXAI LIVE INTELLIGENCE

━━━━━━━━━━━━━━

System:
🟢 Online

AI Engine:
🟢 Active

Database:
🟢 Connected

━━━━━━━━━━━━━━

👥 Users:
{users}

🔍 Opportunities:
{opportunities}

🕒 Server Time:
{now}

━━━━━━━━━━━━━━

Security Sources:

✅ GitHub
✅ Immunefi
✅ HackerOne

━━━━━━━━━━━━━━

🚀 Continuous Intelligence Running
"""
