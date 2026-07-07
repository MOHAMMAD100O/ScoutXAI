import math


def score_repo(repo):
    """
    Simple AI scoring engine (stable version)
    """

    stars = repo.get("stars", 0)
    name = (repo.get("name") or "").lower()
    desc = (repo.get("description") or "").lower()

    score = 0

    # ⭐ stars weight
    score += min(stars / 50, 5)

    # 🧠 keyword boost
    if "ai" in name or "ai" in desc:
        score += 3

    if "security" in name or "exploit" in desc:
        score += 4

    if "blockchain" in name or "web3" in desc:
        score += 3

    if "hack" in name:
        score += 2

    return round(score, 2)
