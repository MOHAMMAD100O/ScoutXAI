from datetime import datetime


def calculate_severity(score):

    if score >= 70:
        return "CRITICAL"

    if score >= 40:
        return "HIGH"

    if score >= 10:
        return "MEDIUM"

    if score > 0:
        return "LOW"

    return "INFO"



def bounty_estimate(severity):

    bounty = {

        "CRITICAL":
            "$5,000 - $50,000",

        "HIGH":
            "$1,000 - $5,000",

        "MEDIUM":
            "$250 - $1,000",

        "LOW":
            "Usually no bounty / $50 - $250",

        "INFO":
            "No bounty expected"
    }

    return bounty.get(
        severity,
        "Unknown"
    )



def risk_status(severity):

    status = {

        "CRITICAL":
            "CRITICAL_RISK",

        "HIGH":
            "HIGH_RISK",

        "MEDIUM":
            "MEDIUM_RISK",

        "LOW":
            "LOW_RISK",

        "INFO":
            "INFORMATIONAL"
    }

    return status.get(
        severity,
        "UNKNOWN"
    )



class BugBountyReporter:


    def __init__(self):

        self.name = (
            "ScoutXAI Professional "
            "Bug Bounty Reporter"
        )



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
            f"Repository:\n{repository}"
        )

        report.append(
            f"Date:\n{datetime.utcnow().isoformat()}"
        )

        report.append(
            f"Total Findings: {len(findings)}"
        )

        report.append(
            "━━━━━━━━━━━━━━━━━━"
        )


        for index, item in enumerate(
            findings,
            start=1
        ):


            score = item.get(
                "risk_score",
                0
            )


            severity = calculate_severity(
                score
            )


            report.append(
f"""
#{index}

Contract:
{item.get('contract')}

Risk Score:
{score}/100

Severity:
{severity}

Risk Status:
{risk_status(severity)}

Estimated Bounty:
{bounty_estimate(severity)}

Detected Issues:
{item.get('findings')}

Analysis Status:
{item.get('status')}

━━━━━━━━━━━━━━━━━━
"""
            )


        if not findings:

            report.append(
                "✅ No vulnerabilities detected."
            )


        report.append(
            """
Responsible Disclosure:
ScoutXAI recommends ethical reporting
through official security channels.
"""
        )


        return "\n".join(report)
