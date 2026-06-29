import requests
from config import GITHUB_API

def fetch_github_opportunities():
    query = "bug OR vulnerability OR security OR exploit"
    
    url = f"{GITHUB_API}?q={query}&sort=updated"
    res = requests.get(url)

    if res.status_code != 200:
        return []

    data = res.json()
    items = data.get("items", [])

    results = []

    for repo in items[:20]:
        results.append({
            "name": repo["name"],
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "description": repo["description"] or "",
        })

    return results
