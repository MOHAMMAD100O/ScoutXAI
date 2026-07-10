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

    plan = get_plan_text(user.id)

    referral_link = (
        f"https://t.me/{context.bot.username}?start={user.id}"
    )

    message = f"""
🚀 Welcome to ScoutXAI

AI Opportunity Intelligence Platform

━━━━━━━━━━━━━━

ScoutXAI discovers valuable opportunities across the AI ecosystem.

Our intelligence engine analyzes:

🧠 AI Projects
🔍 Open Source Trends
📈 Emerging Technologies
⚡ Early Opportunity Signals

━━━━━━━━━━━━━━

🔥 Features:

✓ AI-powered opportunity ranking
✓ Intelligence reports
✓ Early discovery system
✓ Continuous opportunity scanning

━━━━━━━━━━━━━━

Commands:

🔥 /top
Top AI opportunities

🔍 /scan
Run intelligence scan

💎 /premium
Unlock advanced intelligence

💳 /buy
Get Premium access

🎁 /referral
Invite & earn rewards

📊 /status
Account information

━━━━━━━━━━━━━━

👤 Account:
{user.id}

Plan:
{plan}

━━━━━━━━━━━━━━

Your referral link:

{referral_link}

━━━━━━━━━━━━━━

🚀 Discover the future of AI with ScoutXAI
"""

    await update.message.reply_text(message)

    user = update.effective_user

    create_user(
        user.id,
        user.username
    )

    plan = get_plan_text(user.id)

    referral_link = (
        f"https://t.me/{context.bot.username}?start={user.id}"
    )

    message = f"""
🚀 Welcome to ScoutXAI

AI Opportunity Intelligence Platform

━━━━━━━━━━━━━━

🔥 What ScoutXAI does:

• Finds valuable AI projects
• Detects emerging opportunities
• Ranks projects with AI
• Delivers intelligence reports

━━━━━━━━━━━━━━

Commands:

/top
🔥 Top opportunities

/scan
🔍 Search opportunities

/premium
💎 Upgrade

/buy
💳 Create payment

/referral
🎁 Invite & earn

/status
📊 Account

━━━━━━━━━━━━━━

👤 Account:
{user.id}

Plan:
{plan}

━━━━━━━━━━━━━━

Your referral link:

{referral_link}
"""

    await update.message.reply_text(message)



async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    premium = is_premium_active(user.id)

    limit = 10 if premium else 3

    opportunities = get_top_opportunities(limit)


    if not opportunities:

        await update.message.reply_text(
            "No intelligence data available."
        )
        return


    message = """
🔥 ScoutXAI Intelligence Report

Top AI Opportunities

━━━━━━━━━━━━━━
"""


    for index, item in enumerate(opportunities, start=1):

        message += (
            f"#{index} {item.get('name','Unknown')}\n"
            f"⭐ Score: {item['score']}\n"
            f"🔗 {item['url']}\n\n"
        )


    if not premium:

        message += (
            "━━━━━━━━━━━━━━\n"
            "🆓 FREE ACCESS\n"
            "Showing top 3 opportunities.\n\n"
            "💎 Premium unlocks full rankings."
        )


    await update.message.reply_text(message)



async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
💎 ScoutXAI PREMIUM

Unlock full intelligence engine.

🔥 Benefits:

✓ Full opportunity rankings
✓ Early discoveries
✓ AI analysis
✓ Priority alerts


Available Plans:

Monthly
💰 9.99 USDT
⏳ 30 days

Quarterly
💰 24.99 USDT
⏳ 90 days

Yearly
💰 79.99 USDT
⏳ 365 days


Use:
/buy
"""

    await update.message.reply_text(message)



async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    plans = available_plans()


    message = """
💳 ScoutXAI Payment

Choose your plan:

"""


    for name, data in plans.items():

        message += (
            f"🔥 {name}\n"
            f"💰 {data['amount']} USDT\n"
            f"⏳ {data['days']} days\n\n"
        )


    message += (
        "To create order:\n"
        "/buy monthly\n"
        "/buy quarterly\n"
        "/buy yearly"
    )


    args = context.args


    if args:

        order = create_order(
            user.id,
            args[0]
        )

        message = f"""
✅ Payment Order Created

Order:
{order.order_id}

Amount:
{order.amount} USDT

Network:
{order.network}

Wallet:

{order.wallet}

Status:
{order.status}
"""


    await update.message.reply_text(message)



async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    link = (
        f"https://t.me/{context.bot.username}?start={user.id}"
    )

    await update.message.reply_text(
        f"""
🎁 ScoutXAI Referral Program

Your link:

{link}

Rewards:
Invite users → Premium rewards
"""
    )



async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    plan = get_plan_text(user.id)

    await update.message.reply_text(
        f"""
🚀 ScoutXAI Status

System:
✅ AI Engine
✅ Scanner
✅ Database
✅ Telegram Platform

━━━━━━━━━━━━━━

User:
{user.id}

Plan:
{plan}
"""
    )
async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
🔍 ScoutXAI Intelligence Scan

AI engine is searching for new opportunities.

Analyzing:

• AI projects
• Open source trends
• Market signals

Results will appear in intelligence feed.
"""
    )
