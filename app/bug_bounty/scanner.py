from app.services.security_pipeline import analyze_repository_contracts


class BugBountyScanner:

    def __init__(self):
        self.name = "ScoutXAI Bug Bounty Scanner"


    def scan(self, repository, limit=10):

        try:

            results = analyze_repository_contracts(
                repository,
                limit=limit
            )

            return {
                "repository": repository,
                "findings": results,
                "count": len(results)
            }

        except Exception as e:

            return {
                "repository": repository,
                "findings": [],
                "count": 0,
                "error": str(e)
            }
