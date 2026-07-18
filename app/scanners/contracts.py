import requests


def get_repo_info(repo_url):

    parts = repo_url.rstrip("/").split("/")

    if len(parts) < 5:
        return None

    owner = parts[-2]
    repo = parts[-1]

    return owner, repo



def extract_solidity_files(repo_url):

    results = []

    info = get_repo_info(repo_url)

    if not info:
        return results

    owner, repo = info

    try:

        api_url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}/git/trees/HEAD?recursive=1"
        )

        response = requests.get(
            api_url,
            timeout=30
        )

        if response.status_code != 200:

            print(
                f"GitHub API error: {response.status_code}"
            )

            return results


        data = response.json()


        for item in data.get("tree", []):

            path = item.get("path", "")


            if path.endswith(".sol"):

                results.append({

                    "contract": path,

                    "repository": repo_url,

                    "type": "Solidity Contract",

                    "status": "FOUND"

                })


    except Exception as e:

        print(
            f"Contract Scanner Error: {e}"
        )


    return results



def scan_contracts(repositories):

    contracts = []


    for repo in repositories:

        contracts.extend(
            extract_solidity_files(repo)
        )


    return contracts
