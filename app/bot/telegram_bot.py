import os

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler
)

from telegram.request import HTTPXRequest

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

    request = HTTPXRequest(
        connect_timeout=60,
        read_timeout=60,
        write_timeout=60,
        pool_timeout=60
    )

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )


    app.add_handler(
        CommandHandler("start", start_command)
    )

    app.add_handler(
        CommandHandler("top", top_command)
    )

    app.add_handler(
        CommandHandler("status", status_command)
    )

    app.add_handler(
        CommandHandler("premium", premium_command)
    )

    app.add_handler(
        CommandHandler("buy", buy_command)
    )

    app.add_handler(
        CommandHandler("scan", scan_command)
    )

    app.add_handler(
        CommandHandler("referral", referral_command)
    )


    return app



def run_bot():

    print("🤖 ScoutXAI Telegram Starting...")

    app = create_bot()

    print("✅ Telegram Connected")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=None
    )
