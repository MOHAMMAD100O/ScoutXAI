import requests
from bs4 import BeautifulSoup


IGNORE_NAMES = {
    "bug bounty programs",
    "explore bounties",
    "bounties",
    "view bounty",
    "learn more",
    "login",
    "sign up",
}


def fetch_immunefi_programs(limit=50):

    url = "https://immunefi.com/bug-bounty/"

    headers = {
        "User-Agent": "Mozilla/5.0 ScoutXAI"
    }

    results = []
    seen = set()

    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        for a in soup.find_all("a", href=True):

            name = a.get_text(
                " ",
                strip=True
            )

            href = a["href"]

            if not name:
                continue

            if name.lower() in IGNORE_NAMES:
                continue

            if "/bug-bounty/" not in href:
                continue

            if "/information/" not in href:
                continue

            if name in seen:
                continue

            seen.add(name)

            results.append({
                "source": "Immunefi",
                "name": name,
                "url": (
                    "https://immunefi.com" + href
                    if href.startswith("/")
                    else href
                ),
                "description": (
                    f"{name} smart contract "
                    "security bug bounty"
                ),
                "category": "Smart Contract Security",
                "blockchain": "Web3",
                "reward": "Bug Bounty",
                "status": "LIVE"
            })

            if len(results) >= limit:
                break

    except Exception as e:
        print(
            f"Immunefi error: {e}"
        )

    return results
