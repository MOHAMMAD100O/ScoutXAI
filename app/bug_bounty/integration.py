from app.bug_bounty.scanner import BugBountyScanner
from app.bug_bounty.reporter import BugBountyReporter
from app.bug_bounty.disclosure import ResponsibleDisclosure


class BugBountyEngine:

    def __init__(self):

        self.scanner = BugBountyScanner()
        self.reporter = BugBountyReporter()
        self.disclosure = ResponsibleDisclosure()


    def run(self, repository):

        scan_result = self.scanner.scan(
            repository
        )

        report = self.reporter.generate(
            scan_result
        )

        case = self.disclosure.create_case(
            repository,
            report
        )

        return case



if __name__ == "__main__":

    engine = BugBountyEngine()

    result = engine.run(
        "https://github.com/OpenZeppelin/openzeppelin-contracts"
    )

    print(result["report"])
