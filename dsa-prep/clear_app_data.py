#!/usr/bin/env python3
"""Clear saved DSA prep app data so the local app starts fresh."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
APP_DIR = SCRIPT_DIR / "dsa-prep"
if not (APP_DIR / "data").is_dir():
    APP_DIR = SCRIPT_DIR

DATA_DIR = APP_DIR / "data"
PROGRESS_DB = DATA_DIR / "progress.db"
CONVERSATIONS_DB = DATA_DIR / "conversations.db"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(SCRIPT_DIR))
    except ValueError:
        return str(path)


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def clear_tables(db_path: Path, table_names: list[str]) -> None:
    if not db_path.exists():
        print(f"Skipping missing database: {display_path(db_path)}")
        return

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")

        for table_name in table_names:
            if table_exists(conn, table_name):
                conn.execute(f"DELETE FROM {table_name}")
                print(f"Cleared {display_path(db_path)}:{table_name}")

        if table_exists(conn, "sqlite_sequence"):
            placeholders = ", ".join("?" for _ in table_names)
            conn.execute(
                f"DELETE FROM sqlite_sequence WHERE name IN ({placeholders})",
                table_names,
            )

        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clear local DSA prep progress, chat, memory, and account data."
    )
    parser.add_argument(
        "--keep-users",
        action="store_true",
        help="Keep user accounts and clear only progress/chat/history data.",
    )
    args = parser.parse_args()

    progress_tables = ["chat_messages", "chat_sessions", "progress"]
    if not args.keep_users:
        progress_tables.append("users")

    clear_tables(PROGRESS_DB, progress_tables)
    clear_tables(CONVERSATIONS_DB, ["conversations"])
    print("Done. Restart the app to begin with fresh local data.")


if __name__ == "__main__":
    main()
