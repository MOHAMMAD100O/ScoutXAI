def score_repo(repo):
    score = 0

    name = (repo.get("name") or "").lower()
    desc = (repo.get("description") or "").lower()

    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)

    # ⭐ ارزش واقعی = stars + forks
    score += min(stars / 25, 4)
    score += min(forks / 40, 2)

    text = name + " " + desc

    # 🧠 سیگنال‌های مهم (واقعی بازار)
    signals = {
        "security": 3,
        "siem": 3,
        "ai": 2,
        "machine learning": 2,
        "automation": 2,
        "agent": 2,
        "bot": 1.5,
        "tool": 1,
        "framework": 1.5
    }

    # ❌ پروژه‌های بی‌ارزش
    noise = [
        "awesome", "list", "cheatsheet",
        "tutorial", "example", "demo",
        "learning", "roadmap", "collection"
    ]

    for n in noise:
        if n in text:
            score -= 2

    for k, v in signals.items():
        if k in text:
            score += v

    # 🔥 پروژه‌های واقعی قوی
    if stars > 100 and forks > 50:
        score += 2

    # 🚫 جلوگیری از منفی شدن
    if score < 0:
        score = 0

    return round(score, 2)
