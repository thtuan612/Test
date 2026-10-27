"""SQLite state storage. Set DATABASE_PATH to a persistent path on Railway Volume."""
import json
import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("DATABASE_PATH", "data/giftcodes.sqlite3")


def _connect():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=20)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS seen_codes (
            code TEXT PRIMARY KEY,
            metadata TEXT NOT NULL,
            first_seen_utc TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    return connection


def init_db():
    with _connect():
        pass


def get_seen_codes():
    with _connect() as connection:
        rows = connection.execute("SELECT code FROM seen_codes").fetchall()
    return {row[0] for row in rows}


def mark_seen(code, metadata):
    with _connect() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO seen_codes(code, metadata) VALUES (?, ?)",
            (code.upper(), json.dumps(metadata, ensure_ascii=False)),
        )
