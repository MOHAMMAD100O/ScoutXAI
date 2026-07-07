# Simple in-memory DB (stable version for MVP)

USERS = {}
SEEN_REPOS = {}


def init_users_db():
    global USERS, SEEN_REPOS
    USERS = {}
    SEEN_REPOS = {}


def add_user(user_id, username, first_name, language):
    if user_id not in USERS:
        USERS[user_id] = {
            "username": username,
            "first_name": first_name,
            "language": language
        }


def get_all_users():
    return list(USERS.keys())


def get_seen_repos(user_id):
    if user_id not in SEEN_REPOS:
        SEEN_REPOS[user_id] = set()
    return SEEN_REPOS[user_id]


def save_seen_repo(user_id, repo_name):
    if user_id not in SEEN_REPOS:
        SEEN_REPOS[user_id] = set()

    SEEN_REPOS[user_id].add(repo_name)
