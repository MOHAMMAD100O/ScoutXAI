import time
import threading

from fetchers.github import fetch_github
from fetchers.hackerone import fetch_hackerone
from fetchers.bugcrowd import fetch_bugcrowd

from utils.ranker import rank_project
from database.sqlite import save_project, project_exists


SCAN_INTERVAL = 600  # 10 minutes


def process_projects(projects, source):
    if not projects:
        return

    for project in projects:
        try:
            url = project.get("url")

            # جلوگیری از خطاهای None یا کلید اشتباه
            if not url:
                continue

            # جلوگیری از تکرار
            if project_exists(url):
                continue

            # امتیازدهی
            score = rank_project(project)

            # فیلتر کیفیت پایین
            if score is None or score < 5:
                continue

            # ذخیره در دیتابیس
            save_project(project, source, score)

            print(f"[+] Saved: {url} | Score: {score}")

        except Exception as e:
            print(f"[!] process error ({source}): {e}")


def scan_loop():
    while True:
        try:
            print("\n[*] Scan cycle started...\n")

            try:
                github_projects = fetch_github()
                process_projects(github_projects, "github")
            except Exception as e:
                print(f"[!] GitHub error: {e}")

            try:
                hackerone_projects = fetch_hackerone()
                process_projects(hackerone_projects, "hackerone")
            except Exception as e:
                print(f"[!] HackerOne error: {e}")

            try:
                bugcrowd_projects = fetch_bugcrowd()
                process_projects(bugcrowd_projects, "bugcrowd")
            except Exception as e:
                print(f"[!] Bugcrowd error: {e}")

            print("\n[*] Scan cycle finished.\n")

        except Exception as e:
            print(f"[!] Fatal loop error: {e}")

        time.sleep(SCAN_INTERVAL)


def start_scheduler():
    thread = threading.Thread(target=scan_loop, daemon=True)
    thread.start()
