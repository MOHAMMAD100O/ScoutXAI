from datetime import datetime


class ResponsibleDisclosure:

    def __init__(self):
        self.name = "ScoutXAI Responsible Disclosure Manager"


    def create_case(self, repository, report):

        return {
            "repository": repository,
            "status": "FOUND",
            "created_at": datetime.utcnow().isoformat(),
            "report": report
        }


    def update_status(self, case, status):

        case["status"] = status
        case["updated_at"] = datetime.utcnow().isoformat()

        return case


    def developer_message(self, case):

        return f"""
🛡 Security Report Notification

Repository:
{case['repository']}

Status:
{case['status']}

A security review has been prepared.

Please contact ScoutXAI for technical details.
"""
