import math

def calculate_score(item):
    """
    ScoutXAI AI Ranking Engine v2 (Production Logic)
    Score: 0 - 100 (realistic distribution)
    """

    name = (item.get("name") or "").lower()
    description = (item.get("description") or "").lower()

    stars = item.get("stars", 0)
    forks = item.get("forks", 0)

    score = 0

    # -------------------------
    # 1. GitHub popularity (log scaling)
    # -------------------------
    score += math.log1p(stars) * 6
    score += math.log1p(forks) * 4

    # -------------------------
    # 2. Keyword intelligence
    # -------------------------
    high_keywords = [
        "bug bounty", "vulnerability", "exploit",
        "rce", "remote code execution",
        "privilege escalation", "cve", "0day"
    ]

    medium_keywords = [
        "security", "pentest", "scanner",
        "audit", "exploit tool", "hacking"
    ]

    for kw in high_keywords:
        if kw in name or kw in description:
            score += 25

    for kw in medium_keywords:
        if kw in name or kw in description:
            score += 10

    # -------------------------
    # 3. Quality penalties
    # -------------------------
    if not description:
        score -= 15

    if stars < 5:
        score -= 10

    if forks == 0:
        score -= 5

    # suspicious naming spam filter
    spam_words = ["test", "demo", "example", "tutorial"]
    if any(w in name for w in spam_words):
        score -= 10

    # -------------------------
    # 4. Normalize (IMPORTANT FIX)
    # -------------------------
    score = max(0, min(score, 100))

    return round(score, 2)
