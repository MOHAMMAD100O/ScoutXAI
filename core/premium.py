import os
import json
import time

PREMIUM_FILE = "core/premium_users.json"


def load_premium_users():
    if not os.path.exists(PREMIUM_FILE):
        return {}

    with open(PREMIUM_FILE, "r") as f:
        return json.load(f)


def save_premium_users(data):
    with open(PREMIUM_FILE, "w") as f:
        json.dump(data, f, indent=2)


def is_premium(user_id: str) -> bool:
    users = load_premium_users()

    user = users.get(str(user_id))

    if not user:
        return False

    # check expiry
    if user.get("expires_at", 0) < time.time():
        return False

    return True


def add_premium(user_id: str, days: int = 30):
    users = load_premium_users()

    users[str(user_id)] = {
        "expires_at": time.time() + (days * 86400)
    }

    save_premium_users(users)
