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
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS honey_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            amount INTEGER NOT NULL
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
        """
        CREATE TABLE IF NOT EXISTS guild_channels (
            guild_id TEXT NOT NULL,
            channel_id TEXT NOT NULL,
            PRIMARY KEY (guild_id, channel_id)
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
    cur.execute(
        "INSERT INTO honey_history(user_id, timestamp, amount)"
        " VALUES (?, strftime('%s','now'), ?)",
        (user_id, amount),
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
    cur.execute(
        "INSERT INTO honey_history(user_id, timestamp, amount)"
        " VALUES (?, strftime('%s','now'), ?)",
        (from_user_id, -amount),
    )
    cur.execute("UPDATE users SET honey = honey + ? WHERE user_id=?", (amount, to_user_id))
    cur.execute(
        "INSERT INTO honey_history(user_id, timestamp, amount)"
        " VALUES (?, strftime('%s','now'), ?)",
        (to_user_id, amount),
    )
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


def get_earned_ranking(start_ts: int, end_ts: int, limit: int = 10):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT u.user_id, u.name, u.discriminator, u.nick, SUM(h.amount) AS total
        FROM honey_history h
        JOIN users u ON h.user_id = u.user_id
        WHERE h.timestamp >= ? AND h.timestamp < ? AND h.amount > 0
        GROUP BY h.user_id
        ORDER BY total DESC
        LIMIT ?
        """,
        (start_ts, end_ts, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "user_id": row[0],
            "name": row[1],
            "discriminator": row[2],
            "nick": row[3],
            "earned": row[4],
        }
        for row in rows
    ]


def get_total_ranking(limit: int = 10):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, name, discriminator, nick, honey FROM users ORDER BY honey DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "user_id": row[0],
            "name": row[1],
            "discriminator": row[2],
            "nick": row[3],
            "honey": row[4],
        }
        for row in rows
    ]


def add_allowed_channel(guild_id: str, channel_id: str):
    """Allow using commands in the specified channel."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO guild_channels(guild_id, channel_id) VALUES (?, ?)",
        (guild_id, channel_id),
    )
    conn.commit()
    conn.close()


def remove_allowed_channel(guild_id: str, channel_id: str):
    """Remove a channel from the allowed list for the guild."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM guild_channels WHERE guild_id=? AND channel_id=?",
        (guild_id, channel_id),
    )
    conn.commit()
    conn.close()


def get_allowed_channels(guild_id: str) -> list[str]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT channel_id FROM guild_channels WHERE guild_id=?",
        (guild_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


def set_allowed_channel(guild_id: str, channel_id: str | None):
    """Backward compatible helper to set a single allowed channel."""
    if channel_id is None:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("DELETE FROM guild_channels WHERE guild_id=?", (guild_id,))
        conn.commit()
        conn.close()
    else:
        add_allowed_channel(guild_id, channel_id)


def get_allowed_channel(guild_id: str) -> str | None:
    channels = get_allowed_channels(guild_id)
    return channels[0] if channels else None
