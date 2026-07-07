import logging
import os
import threading

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from database.users import init_users_db, add_user

# ✅ FIX: اسم درست تابع
from fetchers.github import fetch_github

from scheduler import start_scheduler


TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(
        user.id,
        user.username or "",
        user.first_name or "",
        user.language_code or "en"
    )

    await update.message.reply_text(
        "🚀 Welcome to ScoutXAI\n\n"
        "AI Engine is running...\n"
        "Use /scan to see results."
    )


# ---------------- SCAN ----------------
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Scanning GitHub...")

    # ✅ FIX HERE
    repos = fetch_github()

    if not repos:
        await update.message.reply_text("No data found.")
        return

    message = "🔥 TOP OPPORTUNITIES\n\n"

    for i, item in enumerate(repos[:5], 1):
        message += (
            f"{i}. {item.get('name','N/A')}\n"
            f"⭐ Stars: {item.get('stars',0)}\n"
            f"🔗 {item.get('url','N/A')}\n\n"
        )

    await update.message.reply_text(message)


# ---------------- MAIN ----------------
def main():
    init_users_db()

    # 🚀 Auto Scanner
    threading.Thread(target=start_scheduler, daemon=True).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    print("🚀 ScoutXAI is running...")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
