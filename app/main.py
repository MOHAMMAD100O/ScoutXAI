import threading
import time

from app.database.database import init_database
from app.services.scheduler import start_scheduler
from app.bot.telegram_bot import run_bot


def main():

    print("=" * 50)
    print("🚀 ScoutXAI Production Platform")
    print("=" * 50)

    init_database()

    print("✅ Database Ready")

    threading.Thread(
        target=start_scheduler,
        daemon=True
    ).start()

    print("✅ Scanner Started")

    print("🤖 Telegram Bot Starting")

    run_bot()


if __name__ == "__main__":
    main()
