from apscheduler.schedulers.background import BackgroundScheduler
from scanner_engine import scan_and_notify
import time

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(scan_and_notify, "interval", minutes=30)
    scheduler.start()

    print("🚀 Auto Scanner Running...")

    while True:
        time.sleep(60)
