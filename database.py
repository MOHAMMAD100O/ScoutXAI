# app/database/database.py

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

# ==========================
# تنظیمات کلی دیتابیس
# ==========================

DB_PATH = os.path.join(os.path.dirname(__file__), "scoutxai.db")

# تنظیمات Premium / Referral
REFERRAL_INVITES_PER_REWARD = 3       # هر ۳ دعوت معتبر → ۷ روز Premium
REFERRAL_REWARD_DAYS = 7             # تعداد روزهای Premium هدیه
DEFAULT_FREE_PLAN = "free"
DEFAULT_PREMIUM_PLAN = "starter"     # می‌توانی بعداً dynamic کنی


# ==========================
# اتصال و راه‌اندازی دیتابیس
# ==========================

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # جدول کاربران
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TEXT NOT NULL,
            plan TEXT NOT NULL DEFAULT 'free',
            is_premium INTEGER NOT NULL DEFAULT 0,
            premium_until TEXT,
            referral_code TEXT UNIQUE,
            referred_by TEXT,
            invite_count INTEGER NOT NULL DEFAULT 0,
            premium_days_earned INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    # جدول فرصت‌ها
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            external_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            url TEXT,
            score REAL,
            tags TEXT,
            created_at TEXT NOT NULL,
            scanned_at TEXT,
            UNIQUE(source, external_id)
        );
        """
    )

    # جدول Referral (برای لاگ دقیق دعوت‌ها)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_user_id INTEGER NOT NULL,
            referred_user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            reward_applied INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(referrer_user_id) REFERENCES users(id),
            FOREIGN KEY(referred_user_id) REFERENCES users(id)
        );
        """
    )

    # جدول پرداخت‌ها (برای USDT و پلن‌ها)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount_usdt REAL NOT NULL,
            plan TEXT NOT NULL,
            network TEXT,          -- TRC20 / BEP20 / ...
            tx_hash TEXT,
            status TEXT NOT NULL DEFAULT 'pending',  -- pending / confirmed / failed
            created_at TEXT NOT NULL,
            confirmed_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )

    conn.commit()
    conn.close()


# ==========================
# ابزارهای کمکی زمان
# ==========================

def now_str() -> str:
    return datetime.utcnow().isoformat()


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None


# ==========================
# مدیریت کاربران
# ==========================

def create_user_if_not_exists(
    telegram_id: int,
    username: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str] = None,
    referred_by_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    اگر کاربر وجود نداشته باشد، می‌سازد.
    اگر وجود داشته باشد، همان را برمی‌گرداند.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,),
    )
    row = cur.fetchone()

    if row:
        user = dict(row)
        conn.close()
        return user

    created_at = now_str()

    # اگر کد Referral داده شده، بعداً ثبت می‌کنیم
    referral_code = generate_referral_code(telegram_id)

    cur.execute(
        """
        INSERT INTO users (
            telegram_id, username, first_name, last_name,
            created_at, plan, is_premium, premium_until,
            referral_code, referred_by, invite_count, premium_days_earned
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            telegram_id,
            username,
            first_name,
            last_name,
            created_at,
            DEFAULT_FREE_PLAN,
            0,
            None,
            referral_code,
            referred_by_code,
            0,
            0,
        ),
    )

    user_id = cur.lastrowid

    # اگر referred_by_code وجود دارد، ثبت Referral
    if referred_by_code:
        register_referral_by_code(referred_by_code, user_id)

    conn.commit()

    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    return dict(row)


def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def generate_referral_code(telegram_id: int) -> str:
    """
    تولید کد دعوت ساده بر اساس telegram_id.
    می‌توانی بعداً الگوریتم را پیچیده‌تر کنی.
    """
    return f"SCOUT-{telegram_id}"


def get_referral_code_for_user(telegram_id: int) -> str:
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        return generate_referral_code(telegram_id)

    if user.get("referral_code"):
        return user["referral_code"]

    # اگر نبود، تولید و ذخیره کن
    code = generate_referral_code(telegram_id)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET referral_code = ? WHERE telegram_id = ?",
        (code, telegram_id),
    )
    conn.commit()
    conn.close()
    return code


# ==========================
# مدیریت Premium / اشتراک
# ==========================

def is_premium_active(telegram_id: int) -> bool:
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        return False

    premium_until = parse_datetime(user.get("premium_until"))
    if not premium_until:
        return False

    return premium_until > datetime.utcnow()


def set_premium(
    telegram_id: int,
    days: int,
    plan: str = DEFAULT_PREMIUM_PLAN,
) -> Dict[str, Any]:
    """
    اضافه کردن روزهای Premium به کاربر.
    اگر Premium فعال باشد، تمدید می‌شود.
    اگر نباشد، از امروز شروع می‌شود.
    """
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        raise ValueError("User not found")

    current_until = parse_datetime(user.get("premium_until"))
    now = datetime.utcnow()

    if current_until and current_until > now:
        new_until = current_until + timedelta(days=days)
    else:
        new_until = now + timedelta(days=days)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE users
        SET is_premium = 1,
            plan = ?,
            premium_until = ?,
            premium_days_earned = premium_days_earned + ?
        WHERE telegram_id = ?
        """,
        (
            plan,
            new_until.isoformat(),
            days,
            telegram_id,
        ),
    )
    conn.commit()

    cur.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cur.fetchone()
    conn.close()

    return dict(row)


def downgrade_if_expired(telegram_id: int) -> Dict[str, Any]:
    """
    اگر Premium کاربر منقضی شده باشد، او را به Free برمی‌گرداند.
    """
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        raise ValueError("User not found")

    premium_until = parse_datetime(user.get("premium_until"))
    now = datetime.utcnow()

    if premium_until and premium_until > now:
        # هنوز فعال است
        return user

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE users
        SET is_premium = 0,
            plan = ?,
            premium_until = NULL
        WHERE telegram_id = ?
        """,
        (
            DEFAULT_FREE_PLAN,
            telegram_id,
        ),
    )
    conn.commit()

    cur.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cur.fetchone()
    conn.close()

    return dict(row)


# ==========================
# Referral System
# ==========================

def register_referral_by_code(referrer_code: str, new_user_id: int):
    """
    ثبت دعوت جدید بر اساس کد دعوت referrer.
    """
    conn = get_connection()
    cur = conn.cursor()

    # پیدا کردن referrer
    cur.execute(
        "SELECT * FROM users WHERE referral_code = ?",
        (referrer_code,),
    )
    referrer = cur.fetchone()
    if not referrer:
        conn.close()
        return

    referrer_id = referrer["id"]

    # ثبت در جدول referrals
    created_at = now_str()
    cur.execute(
        """
        INSERT INTO referrals (
            referrer_user_id, referred_user_id, created_at, reward_applied
        )
        VALUES (?, ?, ?, 0)
        """,
        (referrer_id, new_user_id, created_at),
    )

    # افزایش invite_count
    cur.execute(
        """
        UPDATE users
        SET invite_count = invite_count + 1
        WHERE id = ?
        """,
        (referrer_id,),
    )

    conn.commit()

    # بررسی اینکه آیا به حد دعوت برای جایزه رسیده است یا نه
    apply_referral_rewards_if_needed(referrer_id, conn)

    conn.close()


def apply_referral_rewards_if_needed(referrer_user_id: int, conn: Optional[sqlite3.Connection] = None):
    """
    اگر تعداد دعوت‌های معتبر به حد لازم رسیده باشد،
    ۷ روز Premium به کاربر اضافه می‌کند.
    """
    internal_conn = False
    if conn is None:
        conn = get_connection()
        internal_conn = True

    cur = conn.cursor()

    # تعداد دعوت‌ها
    cur.execute(
        "SELECT invite_count FROM users WHERE id = ?",
        (referrer_user_id,),
    )
    row = cur.fetchone()
    if not row:
        if internal_conn:
            conn.close()
        return

    invite_count = row["invite_count"]

    # تعداد پاداش‌های ممکن
    rewards_possible = invite_count // REFERRAL_INVITES_PER_REWARD

    # تعداد پاداش‌های اعمال‌شده تا الان
    cur.execute(
        """
        SELECT COUNT(*) AS rewards_applied
        FROM referrals
        WHERE referrer_user_id = ?
          AND reward_applied = 1
        """,
        (referrer_user_id,),
    )
    applied_row = cur.fetchone()
    rewards_applied = applied_row["rewards_applied"] if applied_row else 0

    # اگر پاداش جدیدی قابل اعمال است
    if rewards_possible > rewards_applied:
        rewards_to_apply = rewards_possible - rewards_applied

        # اضافه کردن روزهای Premium
        cur.execute(
            "SELECT telegram_id FROM users WHERE id = ?",
            (referrer_user_id,),
        )
        user_row = cur.fetchone()
        if user_row:
            telegram_id = user_row["telegram_id"]
            total_days = rewards_to_apply * REFERRAL_REWARD_DAYS
            # استفاده از تابع set_premium
            conn.commit()  # قبل از خروج از context
            if internal_conn:
                conn.close()
            set_premium(telegram_id, total_days)
            # دوباره اتصال برای آپدیت reward_applied
            conn2 = get_connection()
            cur2 = conn2.cursor()
            cur2.execute(
                """
                UPDATE referrals
                SET reward_applied = 1
                WHERE referrer_user_id = ?
                  AND reward_applied = 0
                """,
                (referrer_user_id,),
            )
            conn2.commit()
            conn2.close()
            return

    if internal_conn:
        conn.close()


def get_referral_stats_by_telegram_id(telegram_id: int) -> Dict[str, Any]:
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        return {
            "invites": 0,
            "earned_premium_days": 0,
        }

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*) AS total_invites
        FROM referrals
        WHERE referrer_user_id = ?
        """,
        (user["id"],),
    )
    row = cur.fetchone()
    total_invites = row["total_invites"] if row else 0

    conn.close()

    return {
        "invites": total_invites,
        "earned_premium_days": user.get("premium_days_earned", 0),
    }


# ==========================
# مدیریت فرصت‌ها (Opportunities)
# ==========================

def save_opportunity(
    source: str,
    external_id: Optional[str],
    title: str,
    description: Optional[str],
    url: Optional[str],
    score: Optional[float],
    tags: Optional[str],
) -> Dict[str, Any]:
    """
    ذخیره یا آپدیت فرصت در جدول opportunities.
    """
    conn = get_connection()
    cur = conn.cursor()

    created_at = now_str()

    cur.execute(
        """
        INSERT INTO opportunities (
            source, external_id, title, description,
            url, score, tags, created_at, scanned_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source, external_id)
        DO UPDATE SET
            title = excluded.title,
            description = excluded.description,
            url = excluded.url,
            score = excluded.score,
            tags = excluded.tags,
            scanned_at = excluded.scanned_at
        """,
        (
            source,
            external_id,
            title,
            description,
            url,
            score,
            tags,
            created_at,
            created_at,
        ),
    )

    conn.commit()

    cur.execute(
        "SELECT * FROM opportunities WHERE source = ? AND external_id = ?",
        (source, external_id),
    )
    row = cur.fetchone()
    conn.close()

    return dict(row) if row else {}


def get_top_opportunities(limit: int = 10) -> List[Dict[str, Any]]:
    """
    گرفتن Top فرصت‌ها بر اساس score.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT *
        FROM opportunities
        WHERE score IS NOT NULL
        ORDER BY score DESC, created_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_opportunities_for_user(
    telegram_id: int,
    free_limit: int = 3,
    premium_limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    اگر کاربر Premium باشد، تعداد بیشتری می‌گیرد.
    اگر Free باشد، فقط ۳ تا.
    """
    if is_premium_active(telegram_id):
        return get_top_opportunities(limit=premium_limit)
    return get_top_opportunities(limit=free_limit)


# ==========================
# مدیریت پرداخت‌ها (USDT)
# ==========================

def create_payment(
    telegram_id: int,
    amount_usdt: float,
    plan: str,
    network: Optional[str],
    tx_hash: Optional[str],
) -> Dict[str, Any]:
    """
    ثبت پرداخت جدید (در حالت pending).
    """
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        raise ValueError("User not found")

    conn = get_connection()
    cur = conn.cursor()

    created_at = now_str()

    cur.execute(
        """
        INSERT INTO payments (
            user_id, amount_usdt, plan, network,
            tx_hash, status, created_at, confirmed_at
        )
        VALUES (?, ?, ?, ?, ?, 'pending', ?, NULL)
        """,
        (
            user["id"],
            amount_usdt,
            plan,
            network,
            tx_hash,
            created_at,
        ),
    )

    payment_id = cur.lastrowid
    conn.commit()

    cur.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
    row = cur.fetchone()
    conn.close()

    return dict(row)


def confirm_payment(payment_id: int, premium_days: int):
    """
    تایید پرداخت و فعال‌سازی Premium برای کاربر.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
    payment = cur.fetchone()
    if not payment:
        conn.close()
        raise ValueError("Payment not found")

    user_id = payment["user_id"]
    plan = payment["plan"]

    # گرفتن telegram_id کاربر
    cur.execute("SELECT telegram_id FROM users WHERE id = ?", (user_id,))
    user_row = cur.fetchone()
    if not user_row:
        conn.close()
        raise ValueError("User not found for payment")

    telegram_id = user_row["telegram_id"]

    confirmed_at = now_str()

    # آپدیت وضعیت پرداخت
    cur.execute(
        """
        UPDATE payments
        SET status = 'confirmed',
            confirmed_at = ?
        WHERE id = ?
        """,
        (confirmed_at, payment_id),
    )

    conn.commit()
    conn.close()

    # فعال‌سازی Premium
    set_premium(telegram_id, premium_days, plan=plan)
