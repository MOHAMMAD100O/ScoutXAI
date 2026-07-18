import requests

from app.scanners.contracts import extract_solidity_files
from app.scanners.solidity_analyzer import analyze_contract



def fetch_file_content(repository, contract_path):

    try:

        parts = repository.rstrip("/").split("/")

        if len(parts) < 5:
            return ""

        owner = parts[3]
        repo = parts[4]


        branches = [
            "main",
            "master",
            "develop"
        ]


        for branch in branches:

            url = (
                f"https://raw.githubusercontent.com/"
                f"{owner}/{repo}/{branch}/{contract_path}"
            )


            response = requests.get(
                url,
                timeout=15
            )


            if response.status_code == 200:

                return response.text


    except Exception as e:

        print(
            f"Content Fetch Error: {e}"
        )


    return ""




def analyze_repository_contracts(
    repository_url,
    limit=10
):

    reports = []


    contracts = extract_solidity_files(
        repository_url
    )


    print(
        f"🔍 Found {len(contracts)} Solidity contracts"
    )


    checked = 0


    for contract in contracts:

        if checked >= limit:
            break


        code = fetch_file_content(
            repository_url,
            contract["contract"]
        )


        if not code:
            continue


        report = analyze_contract(
            code,
            contract["contract"]
        )


        report["repository"] = repository_url

        reports.append(
            report
        )


        checked += 1


    return reports





def print_security_report(reports):

    print(
        "\n🛡 ScoutXAI Security Report\n"
    )


    if not reports:

        print(
            "No readable Solidity files analyzed"
        )

        return


    for report in reports:

        print(
            "Contract:",
            report["contract"]
        )

        print(
            "Risk Score:",
            report["risk_score"]
        )

        print(
            "Findings:",
            report["findings"]
        )

        print(
            "Status:",
            report["status"]
        )

        print(
            "-" * 40
        )
