from datetime import datetime

from app.database.database import get_connection


REFERRAL_LIMIT = 3
REWARD_DAYS = 7


def create_referral_link(bot_username, telegram_id):
    return f"https://t.me/{bot_username}?start={telegram_id}"


def register_referral(referrer_id, friend_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO referrals
        (
            referrer_id,
            friend_id,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            referrer_id,
            friend_id,
            datetime.utcnow().isoformat()
        )
    )

    cursor.execute(
        """
        UPDATE users
        SET invited = invited + 1
        WHERE telegram_id = ?
        """,
        (
            referrer_id,
        )
    )

    conn.commit()
    conn.close()



def get_referral_stats(telegram_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT invited
        FROM users
        WHERE telegram_id=?
        """,
        (
            telegram_id,
        )
    )

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {
            "invited": 0,
            "remaining": REFERRAL_LIMIT
        }

    invited = row["invited"]

    return {
        "invited": invited,
        "remaining": REFERRAL_LIMIT - (invited % REFERRAL_LIMIT)
    }



def referral_text(telegram_id, bot_username):

    stats = get_referral_stats(
        telegram_id
    )

    link = create_referral_link(
        bot_username,
        telegram_id
    )

    return f"""
🎁 ScoutXAI Referral

Invite friends and earn Premium.

🔗 Your referral link:

{link}

👥 Successful invites:
{stats['invited']}

🎯 Next reward:
{stats['remaining']} more users

💎 Reward:
{REWARD_DAYS} days Premium
"""
