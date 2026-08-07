from telegram import Update
from telegram.ext import ContextTypes

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

    referral_link = (
        f"https://t.me/{context.bot.username}?start={user.id}"
    )

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

Commands:

🔥 /top
🔍 /scan
🛡 /security
💎 /premium
💳 /buy
🎁 /referral
📊 /status

━━━━━━━━━━━━━━

User:
{user.id}

Plan:
{get_plan_text(user.id)}

━━━━━━━━━━━━━━

Referral:
{referral_link}
"""
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
            str(available_plans())
        )

        return


    order = create_order(
        user.id,
        context.args[0]
    )


    await update.message.reply_text(
f"""
✅ Order Created

ID:
{order.order_id}

Amount:
{order.amount} USDT

Wallet:
{order.wallet}
"""
)



async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    await update.message.reply_text(
f"""
🎁 Referral Program

https://t.me/{context.bot.username}?start={user.id}
"""
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
