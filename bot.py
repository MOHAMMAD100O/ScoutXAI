from fetchers.github import fetch_github_opportunities
from database.sqlite import score_repo

def main():
    print("Scanning opportunities...\n")

    repos = fetch_github_opportunities()

    if not repos:
        print("No data received!")
        return

    seen = set()
    scored = []

    for r in repos:
        name = r.get("name", "")

        # جلوگیری از تکراری‌ها
        if name in seen:
            continue
        seen.add(name)

        # امتیازدهی
        r["score"] = score_repo(r)
        scored.append(r)

    # مرتب‌سازی بر اساس امتیاز
    top = sorted(scored, key=lambda x: x["score"], reverse=True)[:5]

    print("TOP 5 OPPORTUNITIES:\n")

    for i, t in enumerate(top, 1):
        print(f"{i}. {t.get('name','N/A')}")
        print(f"   Score: {t.get('score',0)}")
        print(f"   URL: {t.get('url','N/A')}\n")


if __name__ == "__main__":
    main()
