from fetchers.github import fetch_github
from database.sqlite import score_repo
from database.users import get_all_users, get_seen_repos, save_seen_repo


def scan_and_notify(bot):
    repos = fetch_github()
    users = get_all_users()

    for repo in repos:

        name = repo.get("name")
        if not name:
            continue

        repo["score"] = score_repo(repo)

        if repo["score"] < 6:
            continue

        for user_id in users:

            seen = get_seen_repos(user_id)

            if name in seen:
                continue

            message = (
                "🚀 HIGH VALUE SIGNAL\n\n"
                f"📦 {repo.get('name')}\n"
                f"⭐ Score: {repo.get('score')}\n"
                f"🔗 {repo.get('url')}\n"
            )

            try:
                bot.send_message(chat_id=user_id, text=message)
                save_seen_repo(user_id, name)
            except Exception as e:
                print("Send error:", e)
