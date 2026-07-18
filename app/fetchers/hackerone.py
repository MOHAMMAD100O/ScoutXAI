import requests
from bs4 import BeautifulSoup


URL = "https://hackerone.com/directory/programs"


def fetch_hackerone_programs():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        r = requests.get(
            URL,
            headers=headers,
            timeout=20
        )

        r.raise_for_status()

    except Exception as e:

        print(
            f"❌ HackerOne Error: {e}"
        )

        return []

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )

    results = []

    seen = set()

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "/programs/" not in href:
            continue

        name = a.get_text(
            strip=True
        )

        if len(name) < 3:
            continue

        if name in seen:
            continue

        seen.add(name)

        results.append({

            "source": "HackerOne",

            "name": name,

            "url": "https://hackerone.com" + href,

            "description": (
                f"{name} bug bounty "
                "security vulnerability disclosure"
            ),

            "category": "Bug Bounty",

            "blockchain": None,

            "reward": "Bug Bounty",

            "status": "LIVE"
        })

    return results
