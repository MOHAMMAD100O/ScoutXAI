import os
import logging

from dotenv import load_dotenv

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
)

from app.bot.handlers import (
    start_command,
    top_command,
    scan_command,
    security_command,
    premium_command,
    buy_command,
    referral_command,
    status_command,
    button_handler,
    verify_command,
    approve_command,
    pending_command,
    daily_command,
    live_command,
)


load_dotenv()

logging.basicConfig(
    level=logging.INFO
)


def create_bot():

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise Exception(
            "BOT_TOKEN missing"
        )


    app = (
        Application
        .builder()
        .token(token)
        .build()
    )


    app.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )


    app.add_handler(
        CommandHandler(
            "top",
            top_command
        )
    )


    app.add_handler(
        CommandHandler(
            "scan",
            scan_command
        )
    )


    app.add_handler(
        CommandHandler(
            "security",
            security_command
        )
    )


    app.add_handler(
        CommandHandler(
            "premium",
            premium_command
        )
    )


    app.add_handler(
        CommandHandler(
            "buy",
            buy_command
        )
    )


    app.add_handler(
        CommandHandler(
            "referral",
            referral_command
        )
    )


    app.add_handler(
        CommandHandler(
            "status",
            status_command
        )
    )


    app.add_handler(
        CommandHandler(
            "live",
            live_command
        )
    )

    app.add_handler(
        CommandHandler(
            "daily",
            daily_command
        )
    )

    app.add_handler(
        CommandHandler(
            "verify",
            verify_command
        )
    )


    app.add_handler(
        CommandHandler(
            "approve",
            approve_command
        )
    )


    app.add_handler(
        CommandHandler(
            "pending",
            pending_command
        )
    )



    app.add_handler(
        CallbackQueryHandler(button_handler)
    )


    return app



def run_bot():

    print(
        "🤖 ScoutXAI Telegram Starting..."
    )


    app = create_bot()


    print(
        "✅ Telegram Bot Connected"
    )


    app.run_polling(
        drop_pending_updates=True
    )
