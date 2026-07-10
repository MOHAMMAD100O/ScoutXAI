import time
import threading
import traceback

from app.services.pipeline import run_pipeline


SCAN_INTERVAL = 600  # 10 minutes


def scheduler_loop():
    print("🚀 ScoutXAI Scheduler Started")

    while True:
        try:
            print("🔍 Starting automatic scan...")

            run_pipeline()

            print("✅ Scan completed")

        except Exception as e:
            print("❌ Scheduler Error:", e)
            traceback.print_exc()

        time.sleep(SCAN_INTERVAL)


def start_scheduler():
    thread = threading.Thread(
        target=scheduler_loop,
        daemon=True
    )

    thread.start()

    return thread
