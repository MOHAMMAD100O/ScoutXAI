from datetime import datetime


class BugBountyReporter:

    def __init__(self):
        self.name = "ScoutXAI Security Report Generator"


    def generate(self, scan_result):

        repository = scan_result.get(
            "repository",
            "Unknown"
        )

        findings = scan_result.get(
            "findings",
            []
        )

        report = []

        report.append(
            "🛡 ScoutXAI Bug Bounty Security Report"
        )

        report.append(
            "━━━━━━━━━━━━━━━━━━"
        )

        report.append(
            f"Repository: {repository}"
        )

        report.append(
            f"Date: {datetime.utcnow().isoformat()}"
        )

        report.append(
            f"Findings: {len(findings)}"
        )

        report.append(
            "━━━━━━━━━━━━━━━━━━"
        )


        if findings:

            for index, item in enumerate(
                findings,
                start=1
            ):

                report.append(
                    f"\n#{index}"
                )

                report.append(
                    str(item)
                )

        else:

            report.append(
                "No security issues detected."
            )


        return "\n".join(report)
