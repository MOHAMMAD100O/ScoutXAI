import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from fetchers.github import fetch_github_opportunities

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 ScoutXAI Online\n\n/scan = Get top opportunities"
    )


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Scanning opportunities...")

    repos = fetch_github_opportunities()

    top = repos[:5]

    message = "🔥 TOP OPPORTUNITIES:\n\n"

    for i, item in enumerate(top, 1):
        message += (
            f"{i}. {item['name']}\n"
            f"⭐ Score: {item['score']}\n"
            f"🔗 {item['url']}\n\n"
        )

    await update.message.reply_text(message)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    print("🚀 ScoutXAI is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
