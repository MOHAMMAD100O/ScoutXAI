from app.ai.ranker import calculate_score
from app.database.database import save_opportunity

from app.scanners.github import fetch_github_projects

from app.fetchers.immunefi import fetch_immunefi_programs
from app.fetchers.hackerone import fetch_hackerone_programs

from app.utils.deduplicator import is_duplicate
from app.utils.security_filter import is_blockchain_security



def safe_fetch(name, function, *args):

    try:
        print(f"🔎 Fetching {name}...")

        data = function(*args)

        print(
            f"✅ {name}: {len(data)} items"
        )

        return data

    except Exception as e:

        print(
            f"❌ {name} failed: {e}"
        )

        return []



def normalize(item, source):

    item["source"] = source

    if "name" not in item:
        item["name"] = "Unknown"

    if "description" not in item:
        item["description"] = ""

    if "url" not in item:
        item["url"] = ""

    return item



def get_threshold(source):

    source = source.lower()

    if "immunefi" in source:
        return 50

    if "hackerone" in source:
        return 50

    if "bugcrowd" in source:
        return 50

    return 60



def run_pipeline():

    print(
        "🚀 ScoutXAI Intelligence Pipeline Started"
    )


    opportunities = []



    github = safe_fetch(
        "GitHub",
        fetch_github_projects,
        60
    )


    for item in github:

        item = normalize(
            item,
            "GitHub"
        )


        if is_blockchain_security(item):

            opportunities.append(item)



    immunefi = safe_fetch(
        "Immunefi",
        fetch_immunefi_programs
    )


    for item in immunefi:

        opportunities.append(
            normalize(
                item,
                "Immunefi"
            )
        )



    hackerone = safe_fetch(
        "HackerOne",
        fetch_hackerone_programs
    )


    for item in hackerone:

        opportunities.append(
            normalize(
                item,
                "HackerOne"
            )
        )



    print(
        f"🧠 Ranking {len(opportunities)} opportunities..."
    )



    saved = 0

    seen_hashes = set()



    for item in opportunities:


        if is_duplicate(
            item,
            seen_hashes
        ):

            continue



        score = calculate_score(item)

        item["score"] = score



        limit = get_threshold(
            item.get(
                "source",
                ""
            )
        )



        if score < limit:

            continue



        result = save_opportunity(item)



        if result:

            saved += 1

            print(
                f"✅ SAVED: {item.get('name')} | Score: {score}"
            )



    print(
        f"🏁 Pipeline Finished | Saved: {saved}"
    )



if __name__ == "__main__":

    run_pipeline()
