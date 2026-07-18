import re


RULES = [

    ("reentrancy", r"\.(call|send|transfer)\s*\(", "HIGH", 25),

    ("delegatecall", r"delegatecall\s*\(", "CRITICAL", 35),

    ("tx_origin", r"tx\.origin", "HIGH", 20),

    ("selfdestruct", r"selfdestruct\s*\(", "CRITICAL", 35),

    ("low_level_call", r"\.call\s*\(", "HIGH", 20),

    ("assembly", r"\bassembly\b", "MEDIUM", 10),

    ("unchecked_math", r"unchecked\s*\{", "MEDIUM", 10),

    ("block_timestamp",
     r"block\.timestamp",
     "MEDIUM",
     10),

    ("block_number",
     r"block\.number",
     "LOW",
     5),

    ("proxy_pattern",
     r"(proxy|upgradeTo|initializer)",
     "MEDIUM",
     10),

    ("mint_function",
     r"function\s+mint\s*\(",
     "HIGH",
     20),

    ("burn_function",
     r"function\s+burn\s*\(",
     "LOW",
     5),

    ("blacklist_logic",
     r"(blacklist|blackList)",
     "HIGH",
     20),

    ("pause_control",
     r"(pause|unpause)",
     "MEDIUM",
     10),

    ("owner_control",
     r"onlyOwner",
     "INFO",
     2),

]


def analyze_contract(source_code, contract_name="Unknown"):

    findings = []
    score = 0


    for name, pattern, severity, points in RULES:

        if re.search(
            pattern,
            source_code,
            re.IGNORECASE
        ):

            findings.append(
                {
                    "name": name,
                    "severity": severity
                }
            )

            score += points


    if score > 100:
        score = 100


    if score >= 80:
        status = "CRITICAL"

    elif score >= 50:
        status = "HIGH_RISK"

    elif score >= 25:
        status = "MEDIUM_RISK"

    else:
        status = "LOW_RISK"


    return {

        "contract": contract_name,

        "risk_score": score,

        "findings": findings,

        "status": status

    }
