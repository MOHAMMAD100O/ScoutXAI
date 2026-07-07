import time
import json
import os

from core.payment_bsc import check_payment


PREMIUM_FILE = "core/premium_users.json"


def load_users():
    if not os.path.exists(PREMIUM_FILE):
        return {}

    with open(PREMIUM_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(PREMIUM_FILE, "w") as f:
        json.dump(data, f, indent=2)


def activate_premium(user_id: str, days: int = 30):
    users = load_users()

    users[str(user_id)] = {
        "expires_at": time.time() + (days * 86400),
        "status": "active"
    }

    save_users(users)


def process_payments(user_wallet_map: dict, min_usdt=10):
    """
    user_wallet_map = {
        "user_id": "wallet_address"
    }
    """

    result = check_payment(min_usdt=min_usdt)

    if result.get("status") in ["paid_usdt", "paid_bnb"]:

        tx_amount = result.get("amount")
        tx_hash = result.get("tx")

        for user_id, wallet in user_wallet_map.items():

            # (ساده‌سازی MVP: همه wallet ها چک می‌شوند)
            activate_premium(user_id)

            print(f"[PAYMENT] User {user_id} activated | TX: {tx_hash} | {tx_amount}")

        return result

    return {"status": "no_payment"}
