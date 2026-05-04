from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
import os

DB_PATH = "data/progress.db"

def _get_db():
    return sqlite3.connect(DB_PATH)

def _init_db():
    if not os.path.exists(DB_PATH):
        conn = _get_db()
        conn.execute('''
            CREATE TABLE progress (
                progress_key TEXT PRIMARY KEY,
                visited INTEGER DEFAULT 0,
                visited_at TEXT,
                complete INTEGER DEFAULT 0,
                remarks TEXT,
                updated_at TEXT
            )
        ''')
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
            "remarks": row[4] or "",
            "updated_at": row[5]
        }
    return progress

def question_key(topic_slug, question, q_index):
    return f"{topic_slug}/{q_index}/{question['title'].replace(' ', '-').lower()}"

def mark_visited(progress_key):
    conn = _get_db()
    visited_at = datetime.now(timezone.utc).isoformat()
    conn.execute('''
        INSERT OR REPLACE INTO progress (progress_key, visited, visited_at)
        VALUES (?, 1, ?)
    ''', (progress_key, visited_at))
    conn.commit()
    conn.close()

def update_progress(progress_key, complete=False, remarks=""):
    conn = _get_db()
    updated_at = datetime.now(timezone.utc).isoformat()
    conn.execute('''
        INSERT OR REPLACE INTO progress (progress_key, complete, remarks, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (progress_key, int(complete), remarks, updated_at))
    conn.commit()
    conn.close()
    return {
        "complete": complete,
        "remarks": remarks,
        "updated_at": updated_at
    }
