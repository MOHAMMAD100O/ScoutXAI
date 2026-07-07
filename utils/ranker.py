import math
import time


def calculate_score(item):
    """
    ScoutXAI AI Ranking Engine v3
    Real opportunity signal scoring (0 - 100)
    """

    name = (item.get("name") or "").lower()
    description = (item.get("description") or "").lower()

    stars = item.get("stars", 0)
    forks = item.get("forks", 0)

    score = 0

    # -------------------------
    # 1. Popularity (log scale)
    # -------------------------
    score += math.log1p(stars) * 5
    score += math.log1p(forks) * 3

    # -------------------------
    # 2. High-value security signals
    # -------------------------
    high_keywords = [
        "bug bounty", "vulnerability", "exploit",
        "rce", "remote code execution",
        "privilege escalation", "cve", "0day", "zero-day"
    ]

    medium_keywords = [
        "security", "pentest", "scanner",
        "audit", "hacking", "red team"
    ]

    for kw in high_keywords:
        if kw in name or kw in description:
            score += 30

    for kw in medium_keywords:
        if kw in name or kw in description:
            score += 12

    # -------------------------
    # 3. Quality filters
    # -------------------------
    if not description:
        score -= 20

    if stars < 5:
        score -= 10

    if forks == 0:
        score -= 7

    spam_words = ["test", "demo", "example", "tutorial"]
    if any(w in name for w in spam_words):
        score -= 15

    # -------------------------
    # 4. Freshness signal (if available)
    # -------------------------
    pushed_at = item.get("pushed_at")
    if pushed_at:
        try:
            # rough freshness bonus
            year = int(pushed_at[:4])
            if year >= 2025:
                score += 15
            elif year >= 2024:
                score += 8
        except:
            pass

    # -------------------------
    # 5. Final normalization
    # -------------------------
    score = max(0, min(score, 100))

    return round(score, 2)
