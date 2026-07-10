import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Environment
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

GITHUB_API = os.getenv(
    "GITHUB_API",
    "https://api.github.com"
)


# Database
DATABASE_PATH = BASE_DIR / "data" / "scoutxai.db"


# Scanner
SCAN_INTERVAL = int(
    os.getenv("SCAN_INTERVAL", "600")
)


# AI Ranking
MINIMUM_SCORE = int(
    os.getenv("MINIMUM_SCORE", "60")
)


# Runtime
ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
)


LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)
