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
            nick TEXT
        )
        """
    )
    cur.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cur.fetchall()]
    if "avatar_url" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    if "nick" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN nick TEXT")
    conn.commit()
    conn.close()


def add_or_update_user(
    user_id: str,
    name: str,
    discriminator: str,
    avatar_url: str | None,
    nick: str | None,
):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users(user_id, name, discriminator, avatar_url, nick)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name=excluded.name,
            discriminator=excluded.discriminator,
            avatar_url=excluded.avatar_url,
            nick=excluded.nick
        """,
        (user_id, name, discriminator, avatar_url, nick),
    )
    conn.commit()
    conn.close()


def get_user(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT user_id, name, discriminator, avatar_url, nick FROM users WHERE user_id=?",
        (user_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row:
        keys = ["user_id", "name", "discriminator", "avatar_url", "nick"]
        return dict(zip(keys, row))
    return None
