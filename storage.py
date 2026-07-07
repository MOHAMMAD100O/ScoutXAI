import os
import json

DATA_DIR = "data"
SEEN_DIR = os.path.join(DATA_DIR, "seen")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


def ensure():
    os.makedirs(SEEN_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)


def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def add_user(user_id, username):
    users = load_users()

    if str(user_id) not in users:
        users[str(user_id)] = {
            "username": username,
            "joined": "now"
        }
        save_users(users)


def load_seen(user_id):
    path = os.path.join(SEEN_DIR, f"{user_id}.json")

    try:
        with open(path, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_seen(user_id, seen):
    path = os.path.join(SEEN_DIR, f"{user_id}.json")

    with open(path, "w") as f:
        json.dump(list(seen), f, indent=2)
