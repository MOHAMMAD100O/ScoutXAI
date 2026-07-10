import sqlite3

from datetime import datetime, timedelta

DATABASE = "scoutxai.db"


def get_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_database():

    conn = get_connection()
    cursor = conn.cursor()

    # USERS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        plan TEXT DEFAULT 'free',
        referral_code TEXT,
        invited INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    # OPPORTUNITIES

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opportunities(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        external_id TEXT,
        title TEXT,
        description TEXT,
        url TEXT UNIQUE,
        score REAL,
        tags TEXT,
        created_at TEXT,
        scanned_at TEXT
    )
    """)

    # REFERRALS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS referrals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        friend_id INTEGER UNIQUE,
        created_at TEXT
    )
    """)

    # PREMIUM SUBSCRIPTIONS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        plan TEXT,
        start_date TEXT,
        end_date TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    # PAYMENTS

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        amount REAL,
        currency TEXT,
        txid TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def create_user(
    telegram_id,
    username=None
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    user = cursor.fetchone()

    if user:
        conn.close()
        return dict(user)

    now = datetime.utcnow().isoformat()

    cursor.execute(
        """
        INSERT INTO users
        (
            telegram_id,
            username,
            referral_code,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            telegram_id,
            username,
            f"SCOUT-{telegram_id}",
            now
        )
    )

    conn.commit()

    cursor.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return dict(user)


def get_user_by_telegram_id(
    telegram_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE telegram_id=?",
        (telegram_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)

    return None


def activate_premium(
    telegram_id,
    days=30
):

    conn = get_connection()
    cursor = conn.cursor()

    start = datetime.utcnow()
    end = start + timedelta(days=days)

    cursor.execute(
        """
        INSERT INTO subscriptions
        (
            telegram_id,
            plan,
            start_date,
            end_date,
            active
        )
        VALUES (?, ?, ?, ?, 1)
        """,
        (
            telegram_id,
            "premium",
            start.isoformat(),
            end.isoformat()
        )
    )

    cursor.execute(
        """
        UPDATE users
        SET plan='premium'
        WHERE telegram_id=?
        """,
        (telegram_id,)
    )

    conn.commit()
    conn.close()


def is_premium_active(
    telegram_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM subscriptions
        WHERE telegram_id=?
        AND active=1
        ORDER BY id DESC
        LIMIT 1
        """,
        (telegram_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if not row:
        return False

    return datetime.fromisoformat(
        row["end_date"]
    ) > datetime.utcnow()

def save_opportunity(project):

    conn = get_connection()
    cursor = conn.cursor()

    url = project.get("url")
    now = datetime.utcnow().isoformat()

    cursor.execute(
        "SELECT id FROM opportunities WHERE url=?",
        (url,)
    )

    exists = cursor.fetchone()

    if exists:

        cursor.execute(
            """
            UPDATE opportunities
            SET
                score=?,
                scanned_at=?
            WHERE url=?
            """,
            (
                project.get("score", 0),
                now,
                url
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO opportunities
            (
                source,
                external_id,
                title,
                description,
                url,
                score,
                tags,
                created_at,
                scanned_at
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project.get("source", "github"),
                project.get("id", url),
                project.get("name", "Unknown"),
                project.get("description", ""),
                url,
                project.get("score", 0),
                project.get("tags", ""),
                now,
                now
            )
        )

    conn.commit()
    conn.close()

    return True


def get_top_opportunities(limit=10):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            title AS name,
            score,
            url
        FROM opportunities
        ORDER BY score DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return rows


def add_referral(referrer_id, friend_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO referrals
        (
            referrer_id,
            friend_id,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            referrer_id,
            friend_id,
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_referral_count(referrer_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM referrals
        WHERE referrer_id=?
        """,
        (referrer_id,)
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count


def save_payment(
    telegram_id,
    amount,
    currency,
    txid,
    status="pending"
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO payments
        (
            telegram_id,
            amount,
            currency,
            txid,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            telegram_id,
            amount,
            currency,
            txid,
            status,
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()
    conn.close()
