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

            # ---------------- AI ANALYSIS (NEW) ----------------
            ai_result = analyze_project(project)

            score = ai_result["score"]
            risks = ai_result["risks"]
            signals = ai_result["signals"]

            # فیلتر کیفیت پایین
            if score < 5:
                continue

            # ذخیره در دیتابیس
            save_project(project, source, score)

            # ذخیره وضعیت آخرین پردازش
            update_state("last_scanned", url)

            print(f"[AI] {url} | Score: {score} | Risks: {len(risks)}")

        except Exception as e:
            print(f"[!] process error ({source}): {e}")
