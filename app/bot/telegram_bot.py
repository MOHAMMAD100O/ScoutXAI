import os

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler
)

from app.bot.handlers import (
    start_command,
    top_command,
    status_command,
    premium_command,
    buy_command,
    scan_command,
    referral_command
)


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


def create_bot():

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN missing")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("premium", premium_command))
    app.add_handler(CommandHandler("buy", buy_command))
    app.add_handler(CommandHandler("scan", scan_command))
    app.add_handler(CommandHandler("referral", referral_command))

    return app


def run_bot():

    print("🤖 Telegram Bot Started")

    app = create_bot()

    print("🤖 Telegram Bot Connected")

    app.run_polling(
        drop_pending_updates=True
    )
