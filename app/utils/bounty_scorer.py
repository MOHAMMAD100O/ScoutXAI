"""
ScoutXAI Blockchain Bug Bounty Scorer

امتیازدهی مخصوص فرصت‌های امنیت Web3
"""


HIGH_VALUE_KEYWORDS = {

    "smart contract": 25,
    "solidity": 25,
    "vyper": 20,

    "defi": 25,
    "dex": 20,
    "bridge": 30,

    "reentrancy": 35,
    "flash loan": 30,

    "audit": 20,
    "security audit": 25,

    "bug bounty": 30,
    "immunefi": 30,

    "ethereum": 15,
    "evm": 15,
    "web3": 15,

    "erc20": 15,
    "erc721": 15,
    "token": 10,

}



def calculate_bounty_score(item):

    text = " ".join([
        str(item.get("name", "")),
        str(item.get("description", "")),
        str(item.get("category", "")),
        str(item.get("source", "")),
    ]).lower()


    score = 0

    reasons = []


    for keyword, value in HIGH_VALUE_KEYWORDS.items():

        if keyword in text:

            score += value

            reasons.append(keyword)



    # Source bonus

    source = str(
        item.get(
            "source",
            ""
        )
    ).lower()


    if "immunefi" in source:

        score += 30
        reasons.append("Immunefi")



    if "hackerone" in source:

        score += 15
        reasons.append("HackerOne")



    if score > 100:

        score = 100



    item["bounty_score"] = score

    item["bounty_reasons"] = reasons


    return score
