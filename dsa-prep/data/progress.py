from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
import os

DB_PATH = "data/progress.db"


def _get_db():
    return sqlite3.connect(DB_PATH)


def _init_db():
    conn = _get_db()
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='progress'"
    )
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        conn.execute('''
            CREATE TABLE progress (
                progress_key TEXT PRIMARY KEY,
                visited INTEGER DEFAULT 0,
                visited_at TEXT,
                complete INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Unsolved',
                remarks TEXT,
                tricky INTEGER DEFAULT 0,
                updated_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        return

    existing_columns = [row[1] for row in conn.execute("PRAGMA table_info(progress)")]
    required_columns = {"progress_key", "visited", "visited_at", "complete", "status", "remarks", "tricky", "updated_at"}

    if not required_columns.issubset(existing_columns):
        conn.execute('ALTER TABLE progress RENAME TO progress_old')
        conn.execute('''
            CREATE TABLE progress (
                progress_key TEXT PRIMARY KEY,
                visited INTEGER DEFAULT 0,
                visited_at TEXT,
                complete INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Unsolved',
                remarks TEXT,
                tricky INTEGER DEFAULT 0,
                updated_at TEXT
            )
        ''')

        copy_columns = [col for col in [
            "progress_key",
            "visited",
            "visited_at",
            "complete",
            "status",
            "remarks",
            "tricky",
            "updated_at",
        ] if col in existing_columns]
        if copy_columns:
            cols = ", ".join(copy_columns)
            conn.execute(
                f"INSERT INTO progress ({cols}) SELECT {cols} FROM progress_old"
            )
        conn.execute('DROP TABLE progress_old')
        conn.commit()
    conn.close()


_init_db()


def load_progress():
    conn = _get_db()
    cursor = conn.execute("SELECT * FROM progress")
    rows = cursor.fetchall()
    conn.close()
    progress = {}
    for row in rows:
        progress[row[0]] = {
            "visited": bool(row[1]),
            "visited_at": row[2],
            "complete": bool(row[3]),
            "status": row[4] or "Unsolved",
            "remarks": row[5] or "",
            "tricky": bool(row[6]),
            "updated_at": row[7]
        }
    return progress


def question_key(topic_slug, question, q_index):
    return f"{topic_slug}/{q_index}/{question['title'].replace(' ', '-').lower()}"


def mark_visited(progress_key):
    conn = _get_db()
    visited_at = datetime.now(timezone.utc).isoformat()
    conn.execute('''
        INSERT INTO progress (
            progress_key,
            visited,
            visited_at,
            complete,
            status,
            remarks,
            tricky,
            updated_at
        ) VALUES (?, 1, ?, 0, 'Unsolved', '', 0, ?)
        ON CONFLICT(progress_key) DO UPDATE SET
            visited=1,
            visited_at=excluded.visited_at
    ''', (progress_key, visited_at, visited_at))
    conn.commit()
    conn.close()


def update_progress(progress_key, status="Unsolved", remarks="", tricky=False):
    status = status if status in ("Solved", "Unsolved") else "Unsolved"
    complete = status == "Solved"
    updated_at = datetime.now(timezone.utc).isoformat()
    conn = _get_db()
    conn.execute('''
        INSERT INTO progress (
            progress_key,
            visited,
            visited_at,
            complete,
            status,
            remarks,
            tricky,
            updated_at
        ) VALUES (?, 1, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(progress_key) DO UPDATE SET
            visited=COALESCE(progress.visited, excluded.visited),
            visited_at=COALESCE(progress.visited_at, excluded.visited_at),
            complete=excluded.complete,
            status=excluded.status,
            remarks=excluded.remarks,
            tricky=excluded.tricky,
            updated_at=excluded.updated_at
    ''', (progress_key, updated_at, int(complete), status, remarks, int(bool(tricky)), updated_at))
    conn.commit()
    conn.close()
    return {
        "complete": complete,
        "status": status,
        "remarks": remarks,
        "tricky": bool(tricky),
        "updated_at": updated_at
    }
