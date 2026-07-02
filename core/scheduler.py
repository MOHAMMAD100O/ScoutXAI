import time
import threading

from fetchers.github import fetch_github
from fetchers.hackerone import fetch_hackerone
from fetchers.bugcrowd import fetch_bugcrowd

from core.ai_engine import analyze_project
from database.sqlite import save_project, project_exists


SCAN_INTERVAL = 600  # 10 minutes


def process_projects(projects, source):
    if not projects:
        return

    for project in projects:
        try:
            url = project.get("url")

            if not url:
                continue

            if project_exists(url):
                continue

            ai_result = analyze_project(project)
            score = ai_result.get("score", 0)

            if score < 5:
                continue

            save_project(project, source, score)

            print(f"[AI] {url} | Score: {score}")

        except Exception as e:
            print(f"[ERROR] {source}: {e}")


def scan_loop():
    while True:
        try:
            print("[*] Scan cycle started")

            process_projects(fetch_github(), "github")
            process_projects(fetch_hackerone(), "hackerone")
            process_projects(fetch_bugcrowd(), "bugcrowd")

            print("[*] Scan cycle finished")

        except Exception as e:
            print(f"[FATAL] {e}")

        time.sleep(SCAN_INTERVAL)


def start_scheduler():
    thread = threading.Thread(target=scan_loop, daemon=True)
    thread.start()
