from app.scanners.github import fetch_github_projects
from app.ai.ranker import calculate_score
from app.database.database import save_opportunity


def run_pipeline():

    print("🚀 ScoutXAI Pipeline Started")

    projects = fetch_github_projects(10)

    saved = 0

    for project in projects:

        score = calculate_score(project)

        project["score"] = score

        if score < 60:
            continue

        result = save_opportunity(project)

        if result:
            saved += 1

            print(
                f"✅ SAVED: {project['name']} | Score: {score}"
            )

    print(
        f"🏁 Pipeline Finished | Saved: {saved}"
    )


if __name__ == "__main__":
    run_pipeline()
