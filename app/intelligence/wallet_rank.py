def rank_wallet(wallet_data):

    score = 0

    volume = wallet_data.get("volume",0)
    buys = wallet_data.get("buys",0)
    sells = wallet_data.get("sells",0)

    if volume >= 100000:
        score += 40

    if buys > sells:
        score += 30

    if buys >= 5:
        score += 20

    if sells == 0:
        score += 10

    if score >= 80:
        return "WHALE"

    if score >= 50:
        return "SMART_WALLET"

    return "NORMAL"
