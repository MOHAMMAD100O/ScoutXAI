import math


def keyword_score(text, keywords, value):
    score = 0

    for word in keywords:
        if word in text:
            score += value

    return score


def calculate_score(project):

    name = (
        project.get("name")
        or ""
    ).lower()

    description = (
        project.get("description")
        or ""
    ).lower()

    text = name + " " + description


    stars = project.get(
        "stars",
        0
    )

    forks = project.get(
        "forks",
        0
    )


    # 1. Growth Signal
    growth = 0

    growth += min(
        math.log1p(stars) * 8,
        35
    )

    growth += min(
        math.log1p(forks) * 5,
        15
    )


    # 2. Innovation Signal
    innovation_keywords = [
        "ai",
        "agent",
        "automation",
        "machine learning",
        "llm",
        "robot",
        "framework"
    ]

    innovation = keyword_score(
        text,
        innovation_keywords,
        10
    )

    innovation = min(
        innovation,
        30
    )


    # 3. Market Potential
    market_keywords = [
        "platform",
        "cloud",
        "api",
        "workflow",
        "developer",
        "enterprise",
        "saas"
    ]

    market = keyword_score(
        text,
        market_keywords,
        8
    )

    market = min(
        market,
        25
    )


    # 4. Security Value
    security_keywords = [
        "security",
        "cyber",
        "vulnerability",
        "exploit",
        "bug bounty",
        "cve",
        "pentest"
    ]

    security = keyword_score(
        text,
        security_keywords,
        10
    )

    security = min(
        security,
        25
    )


    # 5. Saturation Risk
    risk = 0

    famous_words = [
        "tensorflow",
        "linux",
        "react",
        "kubernetes"
    ]

    for word in famous_words:
        if word in text:
            risk += 15


    final_score = (
        growth
        + innovation
        + market
        + security
        - risk
    )


    return round(
        max(0, min(final_score, 100)),
        2
    )
