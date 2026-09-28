"""
ScoutXAI Opportunity Engine V1.1
Scope-Aware Change Intelligence

Purpose:
- Turn existing ScoutXAI opportunities into evidence-backed candidates.
- For GitHub repositories, inspect recent commits and changed files.
- Detect security-relevant CHANGE signals rather than relying only on
  repository/page keywords.
- Never claim a confirmed vulnerability.
- Never perform exploitation or unauthorized active testing.

Status:
    CANDIDATE = requires human review and authorized testing only.

Environment:
    DATABASE_PATH
    GITHUB_API
    GITHUB_TOKEN / GITHUB_API_TOKEN (optional but recommended)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

from app.config.settings import DATABASE_PATH, GITHUB_API


ENGINE_VERSION = "1.1.0"

GITHUB_TOKEN = (
    os.getenv("GITHUB_TOKEN")
    or os.getenv("GITHUB_API_TOKEN")
    or os.getenv("GH_TOKEN")
    or ""
)

GITHUB_API_BASE = (
    GITHUB_API.rstrip("/")
    if GITHUB_API
    else "https://api.github.com"
)

REQUEST_TIMEOUT = 20
RECENT_COMMITS = 5
MAX_PATCH_CHARS = 12000
MAX_COMMIT_EVIDENCE = 5


SECURITY_PATTERNS: Dict[str, List[str]] = {
    "authorization": [
        r"\bauthoriz",
        r"\bpermission",
        r"\baccess[_ -]?control",
        r"\brole\b",
        r"\bprivilege",
        r"\bacl\b",
        r"\bowner\b",
        r"\bonly[_ -]?admin\b",
    ],
    "authentication": [
        r"\bauthentication\b",
        r"\blogin\b",
        r"\bsession\b",
        r"\btoken\b",
        r"\bjwt\b",
        r"\boauth\b",
        r"\bpassword\b",
        r"\bcredential",
    ],
    "external_call": [
        r"\bcall\s*\(",
        r"\bdelegatecall\b",
        r"\bstaticcall\b",
        r"\bexternal\b",
        r"\brequests?\.",
        r"\bhttpx\b",
        r"\bcurl\b",
        r"\bfetch\s*\(",
        r"\burllib\b",
    ],
    "upgradeability": [
        r"\bupgrade",
        r"\bproxy\b",
        r"\bimplementation\b",
        r"\bdelegatecall\b",
        r"\binitializer\b",
        r"\badmin\b",
        r"\bupgradeable\b",
    ],
    "token_logic": [
        r"\btransfer\b",
        r"\btransferfrom\b",
        r"\bapprove\b",
        r"\bpermit\b",
        r"\ballowance\b",
        r"\bmint\b",
        r"\bburn\b",
        r"\bwithdraw\b",
        r"\bdeposit\b",
        r"\btoken\b",
    ],
    "financial_logic": [
        r"\bwithdraw",
        r"\bdeposit",
        r"\bclaim\b",
        r"\breward",
        r"\bfee\b",
        r"\bbalance\b",
        r"\bpayment\b",
        r"\bsettlement\b",
        r"\bamount\b",
        r"\bprice\b",
    ],
    "oracle": [
        r"\boracle\b",
        r"\bprice\s*feed\b",
        r"\bchainlink\b",
        r"\btwap\b",
        r"\bgetprice\b",
        r"\bget_price\b",
    ],
    "reentrancy": [
        r"\breentr",
        r"\bnonreentrant\b",
        r"\bmutex\b",
        r"\block\b",
        r"\bchecks[-_ ]effects\b",
    ],
    "input_validation": [
        r"\bvalidate\b",
        r"\bvalidation\b",
        r"\bsanitize\b",
        r"\bparse\b",
        r"\binput\b",
        r"\bdeserialize\b",
        r"\bdecode\b",
    ],
    "cryptography": [
        r"\bcrypto",
        r"\bencrypt",
        r"\bdecrypt",
        r"\bsignature\b",
        r"\bsigning\b",
        r"\bprivate[_ -]?key\b",
        r"\bsecret\b",
        r"\bnonce\b",
    ],
}


SECURITY_FILE_HINTS = (
    "auth",
    "permission",
    "access",
    "security",
    "wallet",
    "token",
    "contract",
    "oracle",
    "payment",
    "admin",
    "proxy",
    "upgrade",
    "session",
    "crypto",
    "sign",
    "middleware",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()


def clean_text(value: Any, limit: int = 4000) -> str:
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text[:limit]


def github_headers() -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ScoutXAI-OpportunityEngine/1.1",
        "X-GitHub-Api-Version": "2026-03-10",
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


def http_get(
    session: requests.Session,
    url: str,
    params: Optional[Dict[str, Any]] = None,
) -> Optional[requests.Response]:
    try:
        response = session.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            return response

        return None

    except requests.RequestException:
        return None


def github_repo_from_url(url: str) -> Optional[str]:
    if not url:
        return None

    parsed = urlparse(url)

    if parsed.netloc.lower() not in {
        "github.com",
        "www.github.com",
    }:
        return None

    parts = [
        p for p in parsed.path.strip("/").split("/")
        if p
    ]

    if len(parts) < 2:
        return None

    owner = parts[0]
    repo = parts[1]

    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        return None

    return f"{owner}/{repo}"


def extract_github_repos(text: str) -> List[str]:
    if not text:
        return []

    found: List[str] = []

    pattern = re.compile(
        r"https?://github\.com/([^/\s]+)/([^/\s#?]+)",
        re.IGNORECASE,
    )

    for match in pattern.finditer(text):
        owner = match.group(1)
        repo = match.group(2).rstrip(".,);]")

        if repo.endswith(".git"):
            repo = repo[:-4]

        candidate = f"{owner}/{repo}"

        if candidate not in found:
            found.append(candidate)

    return found[:10]


def detect_signals(text: str) -> List[Dict[str, Any]]:
    lowered = (text or "").lower()
    signals: List[Dict[str, Any]] = []

    for category, patterns in SECURITY_PATTERNS.items():
        hits = []

        for pattern in patterns:
            if re.search(pattern, lowered, flags=re.IGNORECASE):
                hits.append(pattern)

        if hits:
            signals.append(
                {
                    "category": category,
                    "confidence": min(
                        95,
                        55 + (len(hits) * 10),
                    ),
                    "matches": len(hits),
                }
            )

    return signals


def security_file_score(filename: str) -> int:
    lower = filename.lower()

    score = 0

    for hint in SECURITY_FILE_HINTS:
        if hint in lower:
            score += 8

    if lower.endswith(
        (
            ".sol",
            ".rs",
            ".go",
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
        )
    ):
        score += 4

    return min(score, 40)


def analyze_commit(commit: Dict[str, Any]) -> Dict[str, Any]:
    sha = commit.get("sha", "")
    html_url = commit.get("html_url", "")

    commit_data = commit.get("commit") or {}
    message = clean_text(
        commit_data.get("message"),
        1000,
    )

    files = commit.get("files") or []

    changed_files = []
    security_files = []
    combined_text_parts = [message]

    additions = 0
    deletions = 0

    for item in files:
        filename = clean_text(
            item.get("filename"),
            500,
        )

        patch = clean_text(
            item.get("patch"),
            MAX_PATCH_CHARS,
        )

        status = clean_text(
            item.get("status"),
            50,
        )

        add = int(item.get("additions") or 0)
        delete = int(item.get("deletions") or 0)

        additions += add
        deletions += delete

        changed_files.append(
            {
                "filename": filename,
                "status": status,
                "additions": add,
                "deletions": delete,
                "changes": int(item.get("changes") or 0),
            }
        )

        if patch:
            combined_text_parts.append(filename)
            combined_text_parts.append(patch)

        file_score = security_file_score(filename)

        if file_score > 0:
            security_files.append(
                {
                    "filename": filename,
                    "score": file_score,
                    "status": status,
                    "additions": add,
                    "deletions": delete,
                    "patch": patch[:4000],
                }
            )

    combined = "\n".join(combined_text_parts)

    signals = detect_signals(combined)

    signal_bonus = min(
        40,
        len(signals) * 8,
    )

    security_file_bonus = min(
        30,
        sum(
            min(10, int(item["score"]) // 2)
            for item in security_files
        ),
    )

    change_size = additions + deletions

    if change_size > 500:
        change_bonus = 4
    elif change_size > 100:
        change_bonus = 7
    elif change_size > 20:
        change_bonus = 10
    else:
        change_bonus = 5

    change_score = min(
        100,
        signal_bonus
        + security_file_bonus
        + change_bonus,
    )

    return {
        "sha": sha,
        "url": html_url,
        "message": message,
        "date": (
            commit_data.get("author") or {}
        ).get("date"),
        "files": changed_files,
        "security_files": security_files,
        "signals": signals,
        "additions": additions,
        "deletions": deletions,
        "change_score": change_score,
    }


def fetch_recent_commits(
    session: requests.Session,
    repo: str,
) -> List[Dict[str, Any]]:
    url = (
        f"{GITHUB_API_BASE}/repos/"
        f"{repo}/commits"
    )

    response = http_get(
        session,
        url,
        params={
            "per_page": RECENT_COMMITS,
        },
    )

    if response is None:
        return []

    try:
        commit_list = response.json()
    except ValueError:
        return []

    if not isinstance(commit_list, list):
        return []

    results = []

    for item in commit_list:
        sha = item.get("sha")

        if not sha:
            continue

        detail_url = (
            f"{GITHUB_API_BASE}/repos/"
            f"{repo}/commits/{sha}"
        )

        detail = http_get(
            session,
            detail_url,
        )

        if detail is None:
            continue

        try:
            commit_data = detail.json()
        except ValueError:
            continue

        if isinstance(commit_data, dict):
            results.append(commit_data)

    return results


def discover_repo(
    opportunity: Dict[str, Any],
    page_text: str,
) -> Optional[str]:
    candidates = []

    direct = github_repo_from_url(
        str(opportunity.get("url") or "")
    )

    if direct:
        candidates.append(direct)

    candidates.extend(
        extract_github_repos(page_text)
    )

    description = str(
        opportunity.get("description") or ""
    )

    candidates.extend(
        extract_github_repos(description)
    )

    for repo in candidates:
        if repo not in candidates[:0]:
            return repo

    return None


def ensure_tables(con: sqlite3.Connection) -> None:
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS opportunity_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id INTEGER UNIQUE,
            source TEXT,
            program_name TEXT,
            program_url TEXT,
            opportunity_score REAL,
            confidence REAL,
            status TEXT DEFAULT 'CANDIDATE',
            scope_status TEXT DEFAULT 'UNKNOWN',
            asset TEXT,
            signal_summary TEXT,
            evidence_count INTEGER DEFAULT 0,
            evidence_json TEXT,
            signals_json TEXT,
            research_plan_json TEXT,
            engine_version TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS opportunity_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER,
            evidence_type TEXT,
            title TEXT,
            url TEXT,
            content_hash TEXT,
            metadata_json TEXT,
            created_at TEXT
        )
        """
    )

    con.commit()


def save_evidence(
    con: sqlite3.Connection,
    case_id: int,
    evidence_type: str,
    title: str,
    url: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    raw = json.dumps(
        metadata,
        ensure_ascii=False,
        sort_keys=True,
    )

    content_hash = sha256_text(
        f"{evidence_type}|{title}|{url}|{raw}"
    )

    con.execute(
        """
        INSERT INTO opportunity_evidence (
            case_id,
            evidence_type,
            title,
            url,
            content_hash,
            metadata_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            case_id,
            evidence_type,
            title,
            url,
            content_hash,
            raw,
            utc_now(),
        ),
    )

    return {
        "type": evidence_type,
        "title": title,
        "url": url,
        "hash": content_hash,
        "metadata": metadata,
    }


def calculate_case(
    opportunity: Dict[str, Any],
    commit_results: List[Dict[str, Any]],
    github_repo: Optional[str],
) -> Tuple[float, float, List[Dict[str, Any]], List[Dict[str, Any]]]:
    signals: Dict[str, Dict[str, Any]] = {}
    evidence: List[Dict[str, Any]] = []

    if github_repo:
        evidence.append(
            {
                "type": "repository",
                "title": f"GitHub repository: {github_repo}",
                "url": f"https://github.com/{github_repo}",
                "metadata": {
                    "repository": github_repo,
                },
            }
        )

    recent_security_changes = 0
    strongest_change = 0

    for result in commit_results:
        for signal in result["signals"]:
            category = signal["category"]

            if category not in signals:
                signals[category] = {
                    "category": category,
                    "occurrences": 0,
                    "confidence": 0,
                }

            signals[category]["occurrences"] += 1
            signals[category]["confidence"] = max(
                signals[category]["confidence"],
                signal["confidence"],
            )

        if (
            result["signals"]
            or result["security_files"]
        ):
            recent_security_changes += 1

        strongest_change = max(
            strongest_change,
            int(result["change_score"]),
        )

        evidence.append(
            {
                "type": "github_commit",
                "title": clean_text(
                    result["message"],
                    300,
                ),
                "url": result["url"],
                "metadata": {
                    "sha": result["sha"],
                    "date": result["date"],
                    "additions": result["additions"],
                    "deletions": result["deletions"],
                    "security_files": [
                        x["filename"]
                        for x in result["security_files"]
                    ],
                    "signals": [
                        x["category"]
                        for x in result["signals"]
                    ],
                },
            }
        )

    base_score = float(
        opportunity.get("score") or 0
    )

    bounty = float(
        opportunity.get("max_bounty") or 0
    )

    bounty_bonus = 0

    if bounty >= 100000:
        bounty_bonus = 20
    elif bounty >= 50000:
        bounty_bonus = 15
    elif bounty >= 10000:
        bounty_bonus = 10
    elif bounty > 0:
        bounty_bonus = 5

    change_bonus = min(
        35,
        strongest_change,
    )

    recurrence_bonus = min(
        15,
        recent_security_changes * 3,
    )

    final_score = min(
        100,
        round(
            (base_score * 0.25)
            + bounty_bonus
            + change_bonus
            + recurrence_bonus,
            1,
        ),
    )

    signal_count = len(signals)

    evidence_quality = min(
        30,
        len(evidence) * 4,
    )

    confidence = min(
        100,
        round(
            45
            + evidence_quality
            + min(20, signal_count * 5)
            + (10 if recent_security_changes else 0),
            1,
        ),
    )

    return (
        final_score,
        confidence,
        list(signals.values()),
        evidence[:MAX_COMMIT_EVIDENCE + 1],
    )


def research_plan(
    signals: List[Dict[str, Any]],
    github_repo: Optional[str],
) -> List[str]:
    categories = {
        item.get("category")
        for item in signals
    }

    plan = []

    if github_repo:
        plan.append(
            "Review the cited repository and exact recent commits."
        )

    if "authorization" in categories:
        plan.append(
            "Review authorization boundaries and privilege transitions "
            "within the authorized scope."
        )

    if "authentication" in categories:
        plan.append(
            "Review authentication/session changes and access-control "
            "regression points."
        )

    if "upgradeability" in categories:
        plan.append(
            "Review upgrade/proxy/initializer changes for access-control "
            "and initialization assumptions."
        )

    if "external_call" in categories:
        plan.append(
            "Review external-call paths and trust boundaries."
        )

    if "financial_logic" in categories:
        plan.append(
            "Review value-transfer and accounting invariants."
        )

    if "token_logic" in categories:
        plan.append(
            "Review token state transitions and authorization checks."
        )

    if "oracle" in categories:
        plan.append(
            "Review oracle assumptions, freshness and validation."
        )

    if "reentrancy" in categories:
        plan.append(
            "Review state-update ordering around external interactions."
        )

    if "input_validation" in categories:
        plan.append(
            "Review validation and parsing boundaries for unsafe inputs."
        )

    if "cryptography" in categories:
        plan.append(
            "Review signing, nonce and secret-handling changes."
        )

    plan.append(
        "Confirm the asset and testing activity are explicitly authorized "
        "by the applicable program scope before active testing."
    )

    return plan[:10]


def upsert_case(
    con: sqlite3.Connection,
    opportunity: Dict[str, Any],
    github_repo: Optional[str],
    score: float,
    confidence: float,
    signals: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
    plan: List[str],
) -> int:
    now = utc_now()

    signal_summary = ", ".join(
        item["category"]
        for item in signals
    )

    asset = (
        github_repo
        or opportunity.get("scope_url")
        or opportunity.get("url")
        or ""
    )

    con.execute(
        """
        INSERT INTO opportunity_cases (
            opportunity_id,
            source,
            program_name,
            program_url,
            opportunity_score,
            confidence,
            status,
            scope_status,
            asset,
            signal_summary,
            evidence_count,
            evidence_json,
            signals_json,
            research_plan_json,
            engine_version,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, 'CANDIDATE', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(opportunity_id)
        DO UPDATE SET
            source = excluded.source,
            program_name = excluded.program_name,
            program_url = excluded.program_url,
            opportunity_score = excluded.opportunity_score,
            confidence = excluded.confidence,
            status = 'CANDIDATE',
            scope_status = excluded.scope_status,
            asset = excluded.asset,
            signal_summary = excluded.signal_summary,
            evidence_count = excluded.evidence_count,
            evidence_json = excluded.evidence_json,
            signals_json = excluded.signals_json,
            research_plan_json = excluded.research_plan_json,
            engine_version = excluded.engine_version,
            updated_at = excluded.updated_at
        """,
        (
            int(opportunity["id"]),
            opportunity.get("source"),
            opportunity.get("name"),
            opportunity.get("url"),
            score,
            confidence,
            (
                "CONFIRMED"
                if opportunity.get("scope_url")
                else "UNKNOWN"
            ),
            asset,
            signal_summary,
            len(evidence),
            json.dumps(
                evidence,
                ensure_ascii=False,
            ),
            json.dumps(
                signals,
                ensure_ascii=False,
            ),
            json.dumps(
                plan,
                ensure_ascii=False,
            ),
            ENGINE_VERSION,
            now,
            now,
        ),
    )

    row = con.execute(
        """
        SELECT id
        FROM opportunity_cases
        WHERE opportunity_id = ?
        """,
        (int(opportunity["id"]),),
    ).fetchone()

    if not row:
        raise RuntimeError(
            "Failed to create opportunity case."
        )

    case_id = int(row["id"])

    con.execute(
        """
        DELETE FROM opportunity_evidence
        WHERE case_id = ?
        """,
        (case_id,),
    )

    for item in evidence:
        save_evidence(
            con,
            case_id,
            item["type"],
            item["title"],
            item["url"],
            item["metadata"],
        )

    con.commit()

    return case_id


def load_opportunities(
    con: sqlite3.Connection,
    limit: int,
) -> List[Dict[str, Any]]:
    rows = con.execute(
        """
        SELECT
            id,
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
            scope_url
        FROM opportunities
        ORDER BY
            COALESCE(score, 0) DESC,
            id DESC
        LIMIT ?
        """,
        (int(limit),),
    ).fetchall()

    return [dict(row) for row in rows]


def run_opportunity_engine(
    limit: int = 25,
) -> List[Dict[str, Any]]:
    db_path = str(DATABASE_PATH)

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    session = requests.Session()

    try:
        ensure_tables(con)

        opportunities = load_opportunities(
            con,
            limit,
        )

        print("=" * 70)
        print("SCOUTXAI OPPORTUNITY ENGINE V1.1")
        print("=" * 70)
        print(f"Database: {db_path}")
        print(f"Engine:   {ENGINE_VERSION}")
        print(
            f"GitHub:   {'AUTHENTICATED' if GITHUB_TOKEN else 'PUBLIC API'}"
        )
        print()
        print(
            f"Input opportunities: {len(opportunities)}"
        )
        print()

        results = []

        for index, opportunity in enumerate(
            opportunities,
            start=1,
        ):
            name = opportunity.get("name") or "Unknown"
            source = opportunity.get("source") or "unknown"

            description = (
                opportunity.get("description") or ""
            )

            radar_data = (
                opportunity.get("radar_data") or ""
            )

            page_text = (
                f"{name}\n"
                f"{description}\n"
                f"{radar_data}\n"
                f"{opportunity.get('scope_url') or ''}"
            )

            github_repo = discover_repo(
                opportunity,
                page_text,
            )

            commit_results = []

            if github_repo:
                commit_data = fetch_recent_commits(
                    session,
                    github_repo,
                )

                for commit in commit_data:
                    commit_results.append(
                        analyze_commit(commit)
                    )

            score, confidence, signals, evidence = (
                calculate_case(
                    opportunity,
                    commit_results,
                    github_repo,
                )
            )

            plan = research_plan(
                signals,
                github_repo,
            )

            case_id = upsert_case(
                con,
                opportunity,
                github_repo,
                score,
                confidence,
                signals,
                evidence,
                plan,
            )

            result = {
                "case_id": case_id,
                "opportunity_id": opportunity["id"],
                "name": name,
                "source": source,
                "repo": github_repo,
                "score": score,
                "confidence": confidence,
                "evidence": len(evidence),
                "signals": len(signals),
                "commits": len(commit_results),
                "status": "CANDIDATE",
            }

            results.append(result)

            print(
                f"[{index}/{len(opportunities)}] "
                f"{source} :: {name}"
            )
            print(
                f"   REPO       : "
                f"{github_repo or 'NONE'}"
            )
            print(
                f"   COMMITS    : "
                f"{len(commit_results)}"
            )
            print(
                f"   SCORE      : "
                f"{score:.1f}"
            )
            print(
                f"   CONFIDENCE : "
                f"{confidence:.1f}"
            )
            print(
                f"   EVIDENCE   : "
                f"{len(evidence)}"
            )
            print(
                f"   SIGNALS    : "
                f"{len(signals)}"
            )
            print()

        results.sort(
            key=lambda item: (
                item["score"],
                item["confidence"],
                item["signals"],
            ),
            reverse=True,
        )

        print("=" * 70)
        print("ENGINE RESULT")
        print("=" * 70)
        print(
            f"Cases generated: {len(results)}"
        )
        print()

        for index, item in enumerate(
            results[:10],
            start=1,
        ):
            print(
                f"{index}. {item['name']}"
            )
            print(
                f"   Score: {item['score']:.1f} | "
                f"Confidence: {item['confidence']:.1f}"
            )
            print(
                f"   Repo: {item['repo'] or 'NONE'}"
            )
            print(
                f"   Commits: {item['commits']} | "
                f"Evidence: {item['evidence']} | "
                f"Signals: {item['signals']}"
            )
            print(
                f"   Status: {item['status']}"
            )
            print()

        print("=" * 70)
        print("IMPORTANT")
        print("=" * 70)
        print(
            "CANDIDATE means research lead only; "
            "it is NOT a confirmed vulnerability."
        )
        print(
            "Active testing must remain inside an explicitly "
            "authorized program scope."
        )
        print("=" * 70)

        return results

    finally:
        session.close()
        con.close()


def get_opportunity_case(
    case_id: int,
) -> Optional[Dict[str, Any]]:
    con = sqlite3.connect(
        str(DATABASE_PATH)
    )
    con.row_factory = sqlite3.Row

    try:
        row = con.execute(
            """
            SELECT *
            FROM opportunity_cases
            WHERE id = ?
            """,
            (int(case_id),),
        ).fetchone()

        if not row:
            return None

        result = dict(row)

        result["evidence"] = json.loads(
            result.get("evidence_json") or "[]"
        )

        result["signals"] = json.loads(
            result.get("signals_json") or "[]"
        )

        result["research_plan"] = json.loads(
            result.get("research_plan_json") or "[]"
        )

        return result

    finally:
        con.close()


if __name__ == "__main__":
    run_opportunity_engine(limit=25)
