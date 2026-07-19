from app.database.database import get_top_opportunities


def hunt_opportunities(limit=10):

    opportunities = get_top_opportunities(limit)

    results = []

    for item in opportunities:
        results.append({
            "name": item.get("name"),
            "url": item.get("url"),
            "score": item.get("score"),
            "action": "READY_FOR_SECURITY_AUDIT"
        })

    return results
