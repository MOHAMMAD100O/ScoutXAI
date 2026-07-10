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

    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()

    print("🤖 Telegram Bot Started")

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()
