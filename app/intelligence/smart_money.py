def analyze_wallet(wallet_data):

    score = 0
    signals = []

    volume = wallet_data.get("volume",0)
    buys = wallet_data.get("buys",0)
    sells = wallet_data.get("sells",0)

    if volume >= 100000:
        score += 40
        signals.append("HIGH_VOLUME")

    if buys > sells:
        score += 30
        signals.append("ACCUMULATION")

    if buys >= 5:
        score += 20
        signals.append("ACTIVE_BUYER")

    if sells == 0:
        score += 10
        signals.append("NO_SELL_PRESSURE")

    return {
        "score": min(score,100),
        "signals": signals
    }
