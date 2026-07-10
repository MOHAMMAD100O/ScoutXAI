import requests

from app.config.settings import GITHUB_API


SEARCH_TERMS = [
    "AI",
    "security",
    "cybersecurity",
    "machine learning",
    "automation",
    "web3"
]


def fetch_github_projects(limit=10):

    projects = []

    for term in SEARCH_TERMS:

        url = f"{GITHUB_API}/search/repositories"

        params = {
            "q": term,
            "sort": "stars",
            "order": "desc",
            "per_page": limit
        }

        try:
            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            if response.status_code != 200:
                continue

            data = response.json()

            for repo in data.get("items", []):

                project = {
                    "name": repo.get("name"),
                    "description": repo.get("description") or "",
                    "url": repo.get("html_url"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language"),
                    "source": "github"
                }

                projects.append(project)

        except Exception as e:
            print("Github scanner error:", e)

    return projects
