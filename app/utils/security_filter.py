"""
ScoutXAI Blockchain Security Relevance Filter

هدف:
جدا کردن فرصت‌های واقعی امنیتی Web3 از پروژه‌های عمومی GitHub

ورودی:
opportunity item

خروجی:
True  = مرتبط با Blockchain Security
False = غیرمرتبط
"""


BLOCKCHAIN_SECURITY_KEYWORDS = {

    # Smart Contract
    "solidity",
    "smart contract",
    "contract audit",
    "smartcontract",
    "vyper",

    # Blockchain
    "blockchain",
    "web3",
    "ethereum",
    "evm",
    "bsc",
    "polygon",
    "arbitrum",
    "optimism",
    "avalanche",

    # DeFi
    "defi",
    "dex",
    "amm",
    "dao",
    "liquidity",
    "yield",
    "staking",

    # Security
    "security",
    "audit",
    "vulnerability",
    "exploit",
    "bug bounty",
    "penetration",
    "reentrancy",
    "flash loan",

    # Token / NFT
    "erc20",
    "erc721",
    "erc1155",
    "token",
    "nft",

    # Infrastructure
    "bridge",
    "cross chain",
    "layer2",
    "zk",
}



BLOCKCHAIN_PRIORITY_WORDS = {

    "smart contract",
    "solidity",
    "defi",
    "reentrancy",
    "flash loan",
    "audit",
    "exploit",
    "bug bounty",
}



def security_relevance_score(item):

    text = " ".join([
        str(item.get("name", "")),
        str(item.get("description", "")),
        str(item.get("category", "")),
        str(item.get("source", "")),
    ]).lower()


    score = 0


    for keyword in BLOCKCHAIN_SECURITY_KEYWORDS:

        if keyword in text:

            score += 5



    for keyword in BLOCKCHAIN_PRIORITY_WORDS:

        if keyword in text:

            score += 10



    return score




def is_blockchain_security(item, threshold=10):

    score = security_relevance_score(item)

    item["security_score"] = score

    return score >= threshold
