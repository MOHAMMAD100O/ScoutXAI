import sqlite3
import os
from datetime import datetime, timedelta


DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "scoutxai.db"
)


def get_connection():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn



def init_database():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        plan TEXT DEFAULT 'free',
        premium_until TEXT,
        referral_code TEXT,
        created_at TEXT
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opportunities
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        url TEXT UNIQUE,
        source TEXT,
        description TEXT,
        score REAL,
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
        """
        INSERT OR IGNORE INTO users
        (
            telegram_id,
            username,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            telegram_id,
            username,
            datetime.utcnow().isoformat()
        )
    )


    conn.commit()
    conn.close()



def get_user_by_telegram_id(
    telegram_id
):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE telegram_id = ?
        """,
        (telegram_id,)
    )


    user = cursor.fetchone()

    conn.close()

    return user



def is_premium_active(
    telegram_id
):

    user = get_user_by_telegram_id(
        telegram_id
    )


    if not user:
        return False


    premium_until = user["premium_until"]


    if not premium_until:
        return False


    try:

        expire = datetime.fromisoformat(
            premium_until
        )

        return expire > datetime.utcnow()

    except:

        return False



def set_premium(
    telegram_id,
    days=30
):

    expire = (
        datetime.utcnow()
        +
        timedelta(days=days)
    ).isoformat()


    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE users
        SET plan='premium',
            premium_until=?
        WHERE telegram_id=?
        """,
        (
            expire,
            telegram_id
        )
    )


    conn.commit()
    conn.close()



def save_opportunity(
    opportunity
):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO opportunities
        (
            name,
            url,
            source,
            description,
            score,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(url)
        DO UPDATE SET

        score=excluded.score,
        description=excluded.description
        """,
        (
            opportunity.get("name"),
            opportunity.get("url"),
            opportunity.get("source"),
            opportunity.get("description"),
            opportunity.get("score"),
            datetime.utcnow().isoformat()
        )
    )


    conn.commit()
    conn.close()

    return True



def get_top_opportunities(
    limit=10
):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM opportunities
        ORDER BY score DESC
        LIMIT ?
        """,
        (limit,)
    )


    rows = cursor.fetchall()

    conn.close()

    return rows
