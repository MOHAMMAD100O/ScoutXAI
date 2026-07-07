from bot.telegram_bot import TelegramBot
from scheduler import start_scheduler
from config import BOT_TOKEN
from scanner_engine import scan


def main():
    print("🚀 ScoutXAI Core v2 Starting...")

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN missing in config.py")
        return

    # start scheduler
    start_scheduler()

    print("⏱ Scheduler started")

    # init bot
    bot = TelegramBot(BOT_TOKEN)

    # test scan
    print("🔍 Running initial scan...")

    results = scan()

    if results:
        print("🔥 TOP:", results[0])
    else:
        print("⚠️ No results")

    # run bot
    bot.run()


if __name__ == "__main__":
    main()
