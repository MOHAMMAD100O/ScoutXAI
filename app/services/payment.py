from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

WALLET_ADDRESS = "0x5f43fada611067b521ec21fd16f0a7a614ef9b84"

NETWORK = "BNB Smart Chain (BEP20)"
CURRENCY = "USDT"


@dataclass
class PaymentOrder:
    order_id: str
    user_id: int
    plan: str
    amount: float
    currency: str
    network: str
    wallet: str
    status: str
    created_at: str
    expires_at: str


PLANS = {
    "monthly": {
        "amount": 9.99,
        "days": 30
    },
    "quarterly": {
        "amount": 24.99,
        "days": 90
    },
    "yearly": {
        "amount": 79.99,
        "days": 365
    }
}


def available_plans():
    return PLANS


def create_order(user_id, plan):

    if plan not in PLANS:
        raise ValueError("Invalid plan")

    now = datetime.utcnow()

    return PaymentOrder(
        order_id=str(uuid.uuid4()).replace("-", "")[:16].upper(),
        user_id=user_id,
        plan=plan,
        amount=PLANS[plan]["amount"],
        currency=CURRENCY,
        network=NETWORK,
        wallet=WALLET_ADDRESS,
        status="PENDING",
        created_at=now.isoformat(),
        expires_at=(now + timedelta(minutes=30)).isoformat()
    )
