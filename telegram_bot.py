import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from core.premium import is_premium, add_premium
from core.scheduler import start_scheduler


BOT_TOKEN = os.getenv("BOT_TOKEN")


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Welcome to ScoutXAI\n\n"
        "Use /status to check access\n"
        "Use /buy to get premium"
    )


# ---------------- STATUS ----------------
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_premium(user_id):
        msg = "✅ You are PREMIUM user"
    else:
        msg = "❌ You are FREE user"

    await update.message.reply_text(msg)


# ---------------- BUY (SIMULATED) ----------------
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    add_premium(user_id, days=30)

    await update.message.reply_text(
        "💰 Premium activated for 30 days\n"
        "Welcome to ScoutXAI Pro 🚀"
    )


# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("buy", buy))

    # start AI scheduler
    start_scheduler()

    print("🚀 ScoutXAI Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
