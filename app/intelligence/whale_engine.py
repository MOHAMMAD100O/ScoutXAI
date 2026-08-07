from datetime import datetime

from .wallet_rank import rank_wallet
from .wallet_memory import wallet_memory
from .smart_money import analyze_wallet


class WhaleEngine:

    def __init__(self):
        self.name = "ScoutXAI Whale Intelligence V1"


    def analyze(self, wallet_data):

        wallet = wallet_data.get("wallet")

        smart = analyze_wallet(wallet_data)

        rank = rank_wallet(wallet_data)

        wallet_memory.save(
            wallet_data
        )

        return {
            "wallet": wallet,
            "smart_score": smart.get("score",0),
            "wallet_rank": rank,
            "signals": smart.get("signals",[]),
            "timestamp": datetime.utcnow().isoformat()
        }


whale_engine = WhaleEngine()
