import json
import re
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.config.settings import DATABASE_PATH
from app.fetchers.immunefi import fetch_immunefi_programs
from app.fetchers.hackerone import fetch_hackerone_programs
from app.ai.ranker import calculate_score


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Android 15; ScoutXAI Opportunity Radar)"
}

TIMEOUT = 25


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def clean_text(value):
    if not value:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def fetch_page(url):
    if not url:
        return ""

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
        )

        if response.status_code != 200:
            print(
                f"⚠️ Radar HTTP {response.status_code}: {url}"
            )
            return ""

        return response.text

    except Exception as exc:
        print(
            f"⚠️ Radar fetch failed: {url} | {exc}"
        )
        return ""


def page_text(html):
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    return clean_text(
        soup.get_text(" ", strip=True)
    )


def extract_max_bounty(text):
    patterns = [
        r"Maximum Bounty\s+\$?\s*([\d,]+(?:\.\d+)?)",
        r"maximum bounty[^$]*\$?\s*([\d,]+(?:\.\d+)?)",
        r"up to:\s*\$?\s*([\d,]+(?:\.\d+)?)",
        r"Max:\s*\$?\s*([\d,]+(?:\.\d+)?)",
        r"maximum\s+reward[^$]*\$?\s*([\d,]+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            raw = match.group(1).replace(",", "")

            try:
                return float(raw)
            except ValueError:
                continue

    return None


def extract_date(text, label):
    pattern = (
        rf"{re.escape(label)}"
        r"\s*:?\s*"
        r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})"
    )

    match = re.search(
        pattern,
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1)

    return None


def extract_flag(text, label):
    match = re.search(
        rf"{re.escape(label)}",
        text,
        re.IGNORECASE,
    )

    return bool(match)


def extract_chains(text):
    known = [
        "Ethereum",
        "ETH",
        "Arbitrum",
        "Optimism",
        "Base",
        "Polygon",
        "BSC",
        "Avalanche",
        "Solana",
        "Cosmos",
        "BNB Chain",
        "Linea",
        "Scroll",
        "Mantle",
        "Celo",
        "Gnosis",
        "Fantom",
        "Astar",
        "Aurora",
        "Injective",
        "Kava",
        "Starknet",
        "zkSync",
    ]

    lower_text = text.lower()

    found = [
        chain
        for chain in known
        if chain.lower() in lower_text
    ]

    return sorted(set(found))


def extract_scope_section(text):
    markers = [
        "Assets in Scope",
        "Impacts in Scope",
        "Scope",
    ]

    lower = text.lower()
    start = None

    for marker in markers:
        index = lower.find(marker.lower())

        if index != -1:
            if start is None or index < start:
                start = index

    if start is None:
        return ""

    section = text[start:start + 5000]

    return clean_text(section)


def extract_security_signals(text):
    checks = {
        "smart_contract": [
            "smart contract",
            "solidity",
            "vyper",
        ],
        "defi": [
            "defi",
            "lending",
            "dex",
            "amm",
            "staking",
            "yield",
        ],
        "bridge": [
            "bridge",
            "cross-chain",
            "cross chain",
            "interoperability",
        ],
        "blockchain": [
            "blockchain",
            "evm",
            "layer 1",
            "layer 2",
        ],
    }

    lower = text.lower()
    result = []

    for category, words in checks.items():
        if any(word in lower for word in words):
            result.append(category)

    return result


def enrich_program(item):
    source = item.get("source", "")
    url = item.get("url", "")

    enriched = dict(item)

    enriched["radar_checked_at"] = utc_now()

    html = fetch_page(url)

    if not html:
        enriched["radar_status"] = "FETCH_FAILED"
        return enriched

    text = page_text(html)

    max_bounty = extract_max_bounty(text)

    if max_bounty is not None:
        enriched["max_bounty"] = max_bounty

    enriched["last_updated"] = extract_date(
        text,
        "Last Updated",
    )

    enriched["live_since"] = extract_date(
        text,
        "Live Since",
    )

    enriched["poc_required"] = extract_flag(
        text,
        "PoC Required",
    )

    enriched["kyc_required"] = extract_flag(
        text,
        "KYC required",
    )

    enriched["chains"] = extract_chains(text)

    enriched["security_signals"] = extract_security_signals(
        text
    )

    enriched["scope_excerpt"] = extract_scope_section(
        text
    )

    enriched["radar_status"] = "ENRICHED"

    enriched["description"] = clean_text(
        enriched.get("description", "")
        + " "
        + "Live bounty metadata collected by "
        + "ScoutXAI Opportunity Radar."
    )

    if source.lower() == "immunefi":
        if "/information/" in url:
            enriched["scope_url"] = url.replace(
                "/information/",
                "/scope/",
            )
        else:
            enriched["scope_url"] = url

    return enriched


def ensure_radar_columns(conn):
    cursor = conn.cursor()

    columns = {
        "radar_data": "TEXT",
        "max_bounty": "REAL",
        "program_status": "TEXT",
        "last_updated": "TEXT",
        "poc_required": "INTEGER",
        "kyc_required": "INTEGER",
        "scope_url": "TEXT",
        "radar_checked_at": "TEXT",
    }

    existing = {
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(opportunities)"
        ).fetchall()
    }

    for name, column_type in columns.items():
        if name not in existing:
            cursor.execute(
                f"""
                ALTER TABLE opportunities
                ADD COLUMN {name} {column_type}
                """
            )

    conn.commit()


def save_radar_opportunity(item):
    database = str(DATABASE_PATH)

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row

    try:
        ensure_radar_columns(conn)

        cursor = conn.cursor()

        url = clean_text(item.get("url", ""))

        if not url:
            return False

        name = clean_text(
            item.get("name", "Unknown")
        )

        source = clean_text(
            item.get("source", "Unknown")
        )

        description = clean_text(
            item.get("description", "")
        )

        score = calculate_score(item)

        item["score"] = score

        radar_data = {
            "source": source,
            "name": name,
            "url": url,
            "category": item.get("category"),
            "blockchain": item.get("blockchain"),
            "status": item.get("status"),
            "reward": item.get("reward"),
            "max_bounty": item.get("max_bounty"),
            "chains": item.get("chains", []),
            "security_signals": item.get(
                "security_signals",
                [],
            ),
            "scope_excerpt": item.get(
                "scope_excerpt",
                "",
            ),
            "scope_url": item.get(
                "scope_url",
            ),
            "poc_required": item.get(
                "poc_required",
            ),
            "kyc_required": item.get(
                "kyc_required",
            ),
            "live_since": item.get(
                "live_since",
            ),
            "last_updated": item.get(
                "last_updated",
            ),
            "radar_status": item.get(
                "radar_status",
            ),
            "radar_checked_at": item.get(
                "radar_checked_at",
            ),
        }

        radar_json = json.dumps(
            radar_data,
            ensure_ascii=False,
        )

        now = utc_now()

        cursor.execute(
            """
            SELECT id
            FROM opportunities
            WHERE url = ?
            LIMIT 1
            """,
            (url,),
        )

        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE opportunities
                SET
                    source = ?,
                    name = ?,
                    description = ?,
                    score = ?,
                    radar_data = ?,
                    max_bounty = ?,
                    program_status = ?,
                    last_updated = ?,
                    poc_required = ?,
                    kyc_required = ?,
                    scope_url = ?,
                    radar_checked_at = ?
                WHERE url = ?
                """,
                (
                    source,
                    name,
                    description,
                    score,
                    radar_json,
                    item.get("max_bounty"),
                    item.get("status"),
                    item.get("last_updated"),
                    int(bool(item.get("poc_required"))),
                    int(bool(item.get("kyc_required"))),
                    item.get("scope_url"),
                    item.get("radar_checked_at"),
                    url,
                ),
            )

        else:
            cursor.execute(
                """
                INSERT INTO opportunities
                (
                    name,
                    url,
                    source,
                    description,
                    score,
                    created_at,
                    radar_data,
                    max_bounty,
                    program_status,
                    last_updated,
                    poc_required,
                    kyc_required,
                    scope_url,
                    radar_checked_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    url,
                    source,
                    description,
                    score,
                    now,
                    radar_json,
                    item.get("max_bounty"),
                    item.get("status"),
                    item.get("last_updated"),
                    int(bool(item.get("poc_required"))),
                    int(bool(item.get("kyc_required"))),
                    item.get("scope_url"),
                    item.get("radar_checked_at"),
                ),
            )

        conn.commit()

        return True

    except Exception as exc:
        conn.rollback()

        print(
            f"❌ Radar database save failed: "
            f"{item.get('name', 'Unknown')} | {exc}"
        )

        return False

    finally:
        conn.close()


def collect_programs():
    programs = []

    print("🔎 Opportunity Radar: Immunefi")

    try:
        immunefi = fetch_immunefi_programs(limit=50)

        print(
            f"   Immunefi discovered: {len(immunefi)}"
        )

        programs.extend(immunefi)

    except Exception as exc:
        print(
            f"❌ Immunefi collection failed: {exc}"
        )

    print("🔎 Opportunity Radar: HackerOne")

    try:
        hackerone = fetch_hackerone_programs()

        print(
            f"   HackerOne discovered: {len(hackerone)}"
        )

        programs.extend(hackerone)

    except Exception as exc:
        print(
            f"❌ HackerOne collection failed: {exc}"
        )

    return programs


def run_opportunity_radar():
    print(
        "\n"
        "========================================\n"
        "🛰️  SCOUTXAI OPPORTUNITY RADAR\n"
        "========================================"
    )

    programs = collect_programs()

    saved = 0
    enriched_count = 0
    failed_count = 0

    seen = set()

    for item in programs:
        url = clean_text(
            item.get("url", "")
        )

        if not url or url in seen:
            continue

        seen.add(url)

        enriched = enrich_program(item)

        if enriched.get("radar_status") == "ENRICHED":
            enriched_count += 1

        elif enriched.get("radar_status") == "FETCH_FAILED":
            failed_count += 1

        if save_radar_opportunity(enriched):
            saved += 1

            bounty = enriched.get("max_bounty")

            if bounty is None:
                bounty_display = "UNKNOWN"
            else:
                bounty_display = f"${bounty:,.0f}"

            print(
                "✅ RADAR | "
                f"{enriched.get('name')} | "
                f"{bounty_display} | "
                f"Score={enriched.get('score')} | "
                f"PoC={enriched.get('poc_required')} | "
                f"KYC={enriched.get('kyc_required')}"
            )

    print(
        "\n"
        "========================================"
    )

    print(
        f"📡 Programs discovered : {len(programs)}"
    )

    print(
        f"🧠 Programs enriched   : {enriched_count}"
    )

    print(
        f"⚠️ Fetch failed        : {failed_count}"
    )

    print(
        f"💾 Programs saved      : {saved}"
    )

    print(
        "========================================\n"
    )

    return saved


if __name__ == "__main__":
    run_opportunity_radar()
