import math


def keyword_score(text, keywords, value):
    score = 0

    for word in keywords:
        if word in text:
            score += value

    return score


def calculate_score(item):

    name = (
        item.get("name")
        or item.get("title")
        or ""
    ).lower()

    description = (
        item.get("description")
        or ""
    ).lower()

    text = name + " " + description


    score = 0


    # -------------------------
    # Source Intelligence
    # -------------------------

    source = (
        item.get("source")
        or ""
    ).lower()


    if "github" in source:

        stars = item.get("stars", 0) or 0
        forks = item.get("forks", 0) or 0

        score += min(
            math.log1p(stars) * 8,
            35
        )

        score += min(
            math.log1p(forks) * 5,
            15
        )


    # -------------------------
    # Bug Bounty / Security
    # -------------------------

    security_words = [
        "security",
        "smart contract",
        "blockchain",
        "defi",
        "web3",
        "vulnerability",
        "exploit",
        "bug bounty",
        "audit",
        "cve",
        "critical",
        "security researcher"
    ]

    score += min(
        keyword_score(
            text,
            security_words,
            8
        ),
        40
    )


    # -------------------------
    # AI Opportunity
    # -------------------------

    ai_words = [
        "ai",
        "agent",
        "llm",
        "machine learning",
        "automation",
        "robot",
        "framework"
    ]

    score += min(
        keyword_score(
            text,
            ai_words,
            7
        ),
        30
    )


    # -------------------------
    # Market Value
    # -------------------------

    market_words = [
        "platform",
        "api",
        "cloud",
        "enterprise",
        "saas",
        "infrastructure"
    ]

    score += min(
        keyword_score(
            text,
            market_words,
            5
        ),
        20
    )


    # -------------------------
    # Reward / Bounty Signal
    # -------------------------

    reward = str(
        item.get("reward")
        or item.get("max_bounty")
        or ""
    ).lower()


    if reward:
        score += 15


    # -------------------------
    # Final Clamp
    # -------------------------

    return round(
        max(
            0,
            min(score, 100)
        ),
        2
    )
