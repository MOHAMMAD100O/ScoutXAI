import requests

BSC_API = "https://api.bscscan.com/api"
API_KEY = "YourFreeApiKeyHere"  # بعداً می‌تونی عوض کنی

WALLET = "0x67Dc6EB4ACa9422a537Ba1c869f2f92cCacc9FF4"

USDT_CONTRACT = "0x55d398326f99059fF775485246999027B3197955"


def get_bnb_transactions():
    url = f"{BSC_API}?module=account&action=txlist&address={WALLET}&sort=desc&apikey={API_KEY}"
    r = requests.get(url, timeout=10)
    return r.json().get("result", [])


def get_usdt_transactions():
    url = f"{BSC_API}?module=account&action=tokentx&address={WALLET}&contractaddress={USDT_CONTRACT}&sort=desc&apikey={API_KEY}"
    r = requests.get(url, timeout=10)
    return r.json().get("result", [])


def check_payment(min_usdt=10):
    """
    Returns latest valid payment
    """

    try:
        usdt_txs = get_usdt_transactions()

        for tx in usdt_txs:
            value = float(tx.get("value", 0)) / 1e18

            if value >= min_usdt:
                return {
                    "status": "paid_usdt",
                    "amount": value,
                    "tx": tx.get("hash")
                }

        bnb_txs = get_bnb_transactions()

        for tx in bnb_txs:
            value = float(tx.get("value", 0)) / 1e18

            if value > 0.01:  # threshold
                return {
                    "status": "paid_bnb",
                    "amount": value,
                    "tx": tx.get("hash")
                }

        return {"status": "no_payment"}

    except Exception as e:
        return {"status": "error", "error": str(e)}
