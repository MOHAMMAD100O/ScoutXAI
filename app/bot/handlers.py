from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from app.database.database import (
    activate_premium,
    get_connection,
    add_referral,
    get_referral_count,
)

from app.database.database import (
    create_user,
    get_top_opportunities,
    is_premium_active,
)

from app.services.payment import (
    create_order,
    available_plans,
)

from app.services.security_pipeline import (
    analyze_repository_contracts,
)

from app.ai.daily_picks import generate_daily_picks
from app.services.live_status import get_live_status


def get_plan_text(user_id):

    if is_premium_active(user_id):
        return "💎 PREMIUM"

    return "🆓 FREE"



async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    create_user(
        user.id,
        user.username
    )

    if context.args:
        try:
            referrer_id = int(context.args[0])

            if referrer_id != user.id:
                add_referral(
                    referrer_id,
                    user.id
                )

        except Exception:
            pass

    referral_link = (
        f"https://t.me/{context.bot.username}?start={user.id}"
    )

    keyboard = [
        [
            InlineKeyboardButton("🔥 Top", callback_data="top"),
            InlineKeyboardButton("🔍 Scan", callback_data="scan"),
            InlineKeyboardButton("🏆 Daily AI Picks", callback_data="daily"),
        ],
        [
            InlineKeyboardButton("🛡 Security", callback_data="security"),
            InlineKeyboardButton("🎯 Targets", callback_data="targets"),
        ],
        [
            InlineKeyboardButton("💎 Premium", callback_data="premium"),
            InlineKeyboardButton("📊 Status", callback_data="status"),
        ],
        [
            InlineKeyboardButton("💳 Buy", callback_data="buy"),
            InlineKeyboardButton("🎁 Referral", callback_data="referral"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
f"""
🚀 Welcome to ScoutXAI

AI Opportunity Intelligence Platform

━━━━━━━━━━━━━━

🧠 AI Intelligence
🔍 Smart Scanner
🛡 Security Research
📈 Opportunity Discovery

━━━━━━━━━━━━━━

User:
{user.id}

Plan:
{get_plan_text(user.id)}

━━━━━━━━━━━━━━

Referral:
{referral_link}
""",
        reply_markup=reply_markup
    )



async def security_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
"""
🛡 ScoutXAI Security Scanner

Usage:

/security github_url

Example:

/security https://github.com/OpenZeppelin/openzeppelin-contracts
"""
        )
        return


    repo = context.args[0]

    await update.message.reply_text(
        "🔍 Scanning Solidity contracts..."
    )


    try:

        reports = analyze_repository_contracts(
            repo,
            limit=5
        )


        if not reports:

            await update.message.reply_text(
                "❌ No contracts found."
            )
            return


        text = """
🛡 ScoutXAI Security Report

━━━━━━━━━━━━━━
"""


        for r in reports:

            text += (
                f"📄 {r['contract']}\n"
                f"Risk: {r['risk_score']}/100\n"
                f"Status: {r['status']}\n"
                f"Findings: {', '.join(r['findings']) if r['findings'] else 'None'}\n"
                "━━━━━━━━━━━━━━\n"
            )


        await update.message.reply_text(text)


    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )



async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    limit = 10 if is_premium_active(user.id) else 3

    data = get_top_opportunities(limit)


    text = "🔥 ScoutXAI Intelligence Report\n\n"


    for i,item in enumerate(data,1):

        text += (
            f"⭐ #{i} {item.get('name')}\n"
            f"Score: {item.get('score')}\n"
            f"{item.get('url')}\n\n"
        )


    await update.message.reply_text(text)



async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
"""
🔍 ScoutXAI Scan

Searching:

• AI Projects
• Web3 Opportunities
• Security Signals

Please wait...
"""
)



async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
"""
💎 ScoutXAI PREMIUM

✅ Full rankings
✅ Security Scanner
✅ Early opportunities
✅ Priority alerts

Monthly:
9.99 USDT

Quarterly:
24.99 USDT

Yearly:
79.99 USDT

Use:
/buy
"""
)



async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not context.args:

        await update.message.reply_text(
f"""
💳 ScoutXAI Payment

Choose plan:

/buy monthly
/buy quarterly
/buy yearly

Network:
BNB Smart Chain (BEP20)

Currency:
USDT
"""
        )

        return


    order = create_order(
        user.id,
        context.args[0]
    )


    await update.message.reply_text(
f"""
✅ Payment Order Created

Order ID:
{order.order_id}

Plan:
{order.plan}

Amount:
{order.amount} USDT

Network:
{order.network}

Wallet:
{order.wallet}

After payment send TXID.
"""
)



async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    count = get_referral_count(
        user.id
    )

    link = (
        f"https://t.me/{context.bot.username}?start={user.id}"
    )

    await update.message.reply_text(
f"""
🎁 ScoutXAI Referral Program

👥 Invited Users:
{count}

⭐ Referral Points:
{count * 10}

━━━━━━━━━━━━━━

🔗 Your Referral Link:

{link}

Invite users and earn rewards 🚀
"""
)



async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    picks = generate_daily_picks(5)

    text = """
🏆 ScoutXAI Daily Intelligence

━━━━━━━━━━━━━━
"""

    for i, item in enumerate(picks, start=1):

        text += f"""
🥇 #{i}
{item['name']}

⭐ AI Score: {item['score']}

{item['reason']}

━━━━━━━━━━━━━━
"""

    await update.message.reply_text(text)



async def live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = get_live_status()

    await update.message.reply_text(
        text
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    await update.message.reply_text(
f"""
🚀 ScoutXAI Status

✅ AI Engine
✅ Database
✅ Scanner
✅ Security Analyzer
✅ Telegram Bot

User:
{user.id}

Plan:
{get_plan_text(user.id)}
"""
)


from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "top":
        await query.message.reply_text(
            "🔥 Top Opportunities\n\n"
            "Use /top to get latest ranking."
        )

    elif data == "scan":
        await query.message.reply_text(
            "🔍 Scanner started...\n"
            "Use /scan for full scan."
        )

    elif data == "daily":
        picks = generate_daily_picks(5)

        text = """
🏆 ScoutXAI Daily Intelligence

━━━━━━━━━━━━━━
"""

        for i, item in enumerate(picks, start=1):
            text += f"""
🥇 #{i}
{item['name']}

⭐ AI Score: {item['score']}

{item['reason']}

━━━━━━━━━━━━━━
"""

        await query.message.reply_text(text)

    elif data == "security":
        await query.message.reply_text(
            "🛡 Security Scanner\n"
            "Use /security <github_url>"
        )

    elif data == "premium":
        await query.message.reply_text(
            "💎 Premium\n"
            "Use /premium"
        )

    elif data == "buy":
        await query.message.reply_text(
            "💳 Buy Premium\n"
            "Use /buy"
        )

    elif data == "referral":
        await query.message.reply_text(
            "🎁 Referral\n"
            "Use /referral"
        )

    elif data == "status":
        await query.message.reply_text(
            "📊 System Status\n"
            "All systems online."
        )

    elif data == "targets":
        await query.message.reply_text(
            "🎯 Targets\n"
            "Use /targets"
        )


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "❌ Usage:\n/verify TXID"
        )
        return

    txid = context.args[0]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO payments
        (telegram_id, amount, currency, txid, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user.id,
            0,
            "USDT",
            txid,
            "PENDING",
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()
    conn.close()

    await update.message.reply_text(
        f"""
✅ Payment Submitted

TXID:
{txid}

Status:
PENDING

Waiting for approval.
"""
    )


async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Usage: /approve USER_ID"
        )
        return

    user_id = int(context.args[0])

    activate_premium(user_id, 30)

    await update.message.reply_text(
        f"""
✅ Premium Activated

User:
{user_id}

Plan:
PREMIUM

Days:
30
"""
    )


ADMIN_ID = 8601933736


async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id != ADMIN_ID:
        await update.message.reply_text(
            "⛔ Access denied"
        )
        return

    from app.database.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT telegram_id, amount, currency, txid, status, created_at
        FROM payments
        WHERE status='PENDING'
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text(
            "✅ No pending payments"
        )
        return

    text = "💳 Pending Payments\n\n"

    for r in rows:
        text += f"""
👤 User: {r[0]}
💰 Amount: {r[1]} {r[2]}
🔗 TXID: {r[3]}
📌 Status: {r[4]}
🕒 {r[5]}

"""

    await update.message.reply_text(text)
