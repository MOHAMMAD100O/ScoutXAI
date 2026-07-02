import re


def analyze_project(project: dict) -> dict:
    """
    Simple production-safe AI scoring engine
    for GitHub / Bug bounty / smart contract projects.
    """

    text = (
        project.get("name", "") + " " +
        project.get("description", "") + " " +
        str(project.get("language", ""))
    ).lower()

    score = 0
    risks = []
    signals = []

    # ----------------------------
    # 1. Tech stack signals
    # ----------------------------
    if "solidity" in text:
        score += 25
        signals.append("Smart Contract detected")

    if "rust" in text:
        score += 15
        signals.append("Low-level safe language")

    if "web3" in text or "blockchain" in text:
        score += 20
        signals.append("Blockchain project")

    # ----------------------------
    # 2. Security keywords (positive signal)
    # ----------------------------
    if re.search(r"\bsecurity\b", text):
        score += 10
        signals.append("Security-related project")

    if re.search(r"\baudit\b", text):
        score += 15
        signals.append("Audit-related project")

    # ----------------------------
    # 3. Risk patterns (negative signals)
    # ----------------------------
    dangerous_patterns = [
        ("reentrancy", "Reentrancy risk pattern"),
        ("tx.origin", "Unsafe authentication (tx.origin)"),
        ("delegatecall", "Dangerous delegatecall usage"),
        ("selfdestruct", "Contract destruction risk"),
    ]

    for pattern, label in dangerous_patterns:
        if pattern in text:
            score -= 10
            risks.append(label)

    # ----------------------------
    # 4. Quality signals
    # ----------------------------
    stars = project.get("stars", 0)

    if stars > 1000:
        score += 20
        signals.append("High popularity project")

    elif stars > 100:
        score += 10
        signals.append("Medium popularity project")

    # ----------------------------
    # Final normalization
    # ----------------------------
    score = max(0, min(score, 100))

    return {
        "project": project.get("name"),
        "score": score,
        "signals": signals,
        "risks": risks
    }
