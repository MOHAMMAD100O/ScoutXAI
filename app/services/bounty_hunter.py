from app.database.database import get_top_opportunities


HIGH_VALUE_KEYWORDS = [
    "defi",
    "bridge",
    "wallet",
    "dex",
    "protocol",
    "solidity",
    "web3",
    "ethereum",
    "blockchain"
]


def calculate_bounty_score(item):

    score = item.get("score", 0)

    name = str(item.get("name","")).lower()
    url = str(item.get("url","")).lower()

    bonus = 0

    for key in HIGH_VALUE_KEYWORDS:
        if key in name or key in url:
            bonus += 5

    final = min(100, score + bonus)

    return final



def find_bounty_targets(limit=20):

    projects = get_top_opportunities(limit)

    targets=[]

    for p in projects:

        bounty_score = calculate_bounty_score(p)

        if bounty_score >= 70:

            targets.append({
                "name": p.get("name"),
                "url": p.get("url"),
                "score": bounty_score,
                "priority": "HIGH_VALUE_TARGET"
            })


    return sorted(
        targets,
        key=lambda x:x["score"],
        reverse=True
    )
