import Database from 'better-sqlite3'
import path from 'path'

const dbPath = path.join(process.cwd(), '..', 'users.db')
const db = new Database(dbPath)

function init() {
  db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    discriminator TEXT NOT NULL,
    avatar_url TEXT,
    nick TEXT,
    honey INTEGER NOT NULL DEFAULT 0
  );
  CREATE TABLE IF NOT EXISTS honey_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    amount INTEGER NOT NULL
  );
  CREATE TABLE IF NOT EXISTS adventure_probabilities (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    success REAL NOT NULL,
    fail REAL NOT NULL,
    normal REAL NOT NULL
  );
  INSERT OR IGNORE INTO adventure_probabilities(id, success, fail, normal)
    VALUES (1, 30, 30, 40);
  `)
}

init()

export function getUser(userId: string) {
  const stmt = db.prepare('SELECT * FROM users WHERE user_id=?')
  return stmt.get(userId)
}

export function addHoney(userId: string, amount: number) {
  const stmt = db.prepare('UPDATE users SET honey = honey + ? WHERE user_id=?')
  stmt.run(amount, userId)
  db.prepare(
    "INSERT INTO honey_history(user_id, timestamp, amount) VALUES (?, strftime('%s','now'), ?)"
  ).run(userId, amount)
}

export function setAdventureProbabilities(success: number, fail: number, normal: number) {
  const stmt = db.prepare('REPLACE INTO adventure_probabilities(id, success, fail, normal) VALUES (1, ?, ?, ?)')
  stmt.run(success, fail, normal)
}

export function getAdventureProbabilities() {
  const row = db.prepare('SELECT success, fail, normal FROM adventure_probabilities WHERE id=1').get()
  if (row) return row as {success: number, fail: number, normal: number}
  return {success:30, fail:30, normal:40}
}
