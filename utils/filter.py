def is_valid_opportunity(repo):
    name = (repo.get("name") or "").lower()
    desc = (repo.get("description") or "").lower()

    blacklist = [
        "awesome",
        "list",
        "cheatsheet",
        "collection",
        "curated",
        "github.io",
        "tutorial"
    ]

    for b in blacklist:
        if b in name or b in desc:
            return False

    return True


def score_repo(repo):
    score = 0

    desc = (repo.get("description") or "").lower()

    stars = repo.get("stargazers_count", 0)
    score += min(stars / 10, 3)

    security_keywords = [
        "security",
        "vulnerability",
        "exploit",
        "pentest",
        "scan"
    ]

    if any(k in desc for k in security_keywords):
        score += 2

    ai_keywords = [
        "ai",
        "agent",
        "automation",
        "machine learning"
    ]

    if any(k in desc for k in ai_keywords):
        score += 2

    if not repo.get("fork", False):
        score += 1

    return round(score, 2)
