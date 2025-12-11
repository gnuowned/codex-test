import os
import sqlite3
from pathlib import Path
from typing import Iterator

DB_PATH = Path(os.environ.get("DB_PATH", "data.db"))


def get_connection() -> sqlite3.Connection:
    # Each call opens a fresh connection; callers must close it.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    # Create table on startup if it does not exist.
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            notes TEXT
        );
        """
    )
    conn.commit()
    conn.close()
