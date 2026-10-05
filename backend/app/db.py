import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    phone         TEXT NOT NULL,
    address       TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS health_data (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    inputs_json TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS predictions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    health_data_id      INTEGER NOT NULL REFERENCES health_data(id) ON DELETE CASCADE,
    status              TEXT NOT NULL,
    risk_level          TEXT NOT NULL,
    probability_healthy REAL NOT NULL,
    probability_at_risk REAL NOT NULL,
    details_json        TEXT NOT NULL,
    created_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def init_db() -> None:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(SCHEMA)


def seed_demo_user(password_hash: str) -> None:
    demo = config.DEMO_USER
    with connect() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO users (name, email, phone, address, password_hash)
               VALUES (?, ?, ?, ?, ?)""",
            (demo["name"], demo["email"], demo["phone"], demo["address"], password_hash),
        )


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
