from app.database.database import get_top_opportunities


def generate_daily_picks(limit=5):
    """
    Generate daily AI picks from ranked opportunities.
    """

    try:
        opportunities = get_top_opportunities(limit)

    except Exception as e:
        return [
            {
                "name": "System Error",
                "score": 0,
                "reason": str(e)
            }
        ]

    picks = []

    for item in opportunities:

        name = item.get("name", "Unknown")
        score = item.get("score", 0)
        source = item.get("source", "Unknown")

        picks.append(
            {
                "name": name,
                "score": score,
                "source": source,
                "reason": generate_reason(score)
            }
        )

    return picks



def generate_reason(score):

    try:
        score = int(score)
    except:
        score = 0


    if score >= 90:
        return "🔥 Premium security opportunity"

    elif score >= 75:
        return "⚡ Strong AI ranked opportunity"

    elif score >= 60:
        return "📌 Interesting research target"

    return "📝 Monitor opportunity"
