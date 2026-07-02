import requests
from config import GITHUB_API
from utils.ranker import calculate_score


def fetch_github_opportunities(min_score=40, limit=20):
    """
    Fetch GitHub repos + rank them + filter low quality
    Returns only high-value opportunities
    """

    query = "bug OR vulnerability OR security OR exploit OR rce OR cve"
    url = f"{GITHUB_API}?q={query}&sort=updated"

    try:
        response = requests.get(
            url,
            headers={
                "Accept": "application/vnd.github+json"
            },
            timeout=15
        )

        if response.status_code != 200:
            return []

        data = response.json()

        results = []

        for repo in data.get("items", []):

            item = {
                "name": repo.get("full_name", ""),
                "description": repo.get("description") or "",
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "url": repo.get("html_url", "")
            }

            score = calculate_score(item)

            # attach score
            item["score"] = score

            # filter low-value repos
            if score >= min_score:
                results.append(item)

            # limit output
            if len(results) >= limit:
                break

        # sort best first
        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    except Exception:
        return []
