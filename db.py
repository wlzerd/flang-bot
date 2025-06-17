import sqlite3

DB_FILE = "users.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            discriminator TEXT NOT NULL,
            avatar_url TEXT,
            nick TEXT,
            honey INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS adventure_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            result TEXT NOT NULL,
            amount INTEGER NOT NULL,
            change INTEGER NOT NULL
        )
        """
    )
    cur.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cur.fetchall()]
    if "avatar_url" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    if "nick" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN nick TEXT")
    if "honey" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN honey INTEGER NOT NULL DEFAULT 0")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS adventure_probabilities (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            success REAL NOT NULL,
            fail REAL NOT NULL,
            normal REAL NOT NULL
        )
        """
    )
    cur.execute(
        "INSERT OR IGNORE INTO adventure_probabilities(id, success, fail, normal) VALUES (1, 30, 30, 40)"
    )
    conn.commit()
    conn.close()


def add_or_update_user(
    user_id: str,
    name: str,
    discriminator: str,
    avatar_url: str | None,
    nick: str | None,
    honey: int = 0,
):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users(user_id, name, discriminator, avatar_url, nick, honey)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name=excluded.name,
            discriminator=excluded.discriminator,
            avatar_url=excluded.avatar_url,
            nick=excluded.nick
        """,
        (user_id, name, discriminator, avatar_url, nick, honey),
    )
    conn.commit()
    conn.close()


def get_user(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, name, discriminator, avatar_url, nick, honey FROM users WHERE user_id=?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row:
        keys = ["user_id", "name", "discriminator", "avatar_url", "nick", "honey"]
        return dict(zip(keys, row))
    return None


def add_honey(user_id: str, amount: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET honey = honey + ? WHERE user_id=?",
        (amount, user_id),
    )
    conn.commit()
    conn.close()


def transfer_honey(from_user_id: str, to_user_id: str, amount: int) -> bool:
    """Transfer honey from one user to another.

    Returns True if the sender had enough honey and the transfer succeeded,
    otherwise returns False without modifying any balances.
    """
    if amount <= 0:
        return False

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT honey FROM users WHERE user_id=?", (from_user_id,))
    row = cur.fetchone()
    if not row or row[0] < amount:
        conn.close()
        return False

    cur.execute("UPDATE users SET honey = honey - ? WHERE user_id=?", (amount, from_user_id))
    cur.execute("UPDATE users SET honey = honey + ? WHERE user_id=?", (amount, to_user_id))
    conn.commit()
    conn.close()
    return True


def get_adventure_probabilities():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT success, fail, normal FROM adventure_probabilities WHERE id=1"
    )
    row = cur.fetchone()
    if not row:
        row = (30.0, 30.0, 40.0)
        cur.execute(
            "INSERT OR REPLACE INTO adventure_probabilities(id, success, fail, normal) VALUES (1, ?, ?, ?)",
            row,
        )
        conn.commit()
    conn.close()
    return row


def set_adventure_probabilities(success: float, fail: float, normal: float):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "REPLACE INTO adventure_probabilities(id, success, fail, normal) VALUES (1, ?, ?, ?)",
        (success, fail, normal),
    )
    conn.commit()
    conn.close()


def add_adventure_log(user_id: str, result: str, amount: int, change: int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO adventure_logs(user_id, timestamp, result, amount, change)"
        " VALUES (?, strftime('%s','now'), ?, ?, ?)",
        (user_id, result, amount, change),
    )
    conn.commit()
    conn.close()


def get_recent_adventure_logs(user_id: str, limit: int = 5):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT timestamp, result, amount, change
        FROM adventure_logs
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "timestamp": row[0],
            "result": row[1],
            "amount": row[2],
            "change": row[3],
        }
        for row in rows
    ]
