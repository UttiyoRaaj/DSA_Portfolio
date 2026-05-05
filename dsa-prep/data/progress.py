from __future__ import annotations

from datetime import datetime, timezone
from data.db import get_db


def _init_db():
    conn = get_db()

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='progress'"
    )
    progress_exists = cursor.fetchone() is not None

    if not progress_exists:
        conn.execute('''
            CREATE TABLE progress (
                progress_key TEXT NOT NULL,
                user_id INTEGER NOT NULL DEFAULT 0,
                visited INTEGER DEFAULT 0,
                visited_at TEXT,
                complete INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Unsolved',
                remarks TEXT,
                tricky INTEGER DEFAULT 0,
                updated_at TEXT,
                PRIMARY KEY(progress_key, user_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
        return

    existing_columns = [row[1] for row in conn.execute("PRAGMA table_info(progress)")]
    required_columns = {
        "progress_key",
        "user_id",
        "visited",
        "visited_at",
        "complete",
        "status",
        "remarks",
        "tricky",
        "updated_at",
    }

    if not required_columns.issubset(existing_columns):
        conn.execute('ALTER TABLE progress RENAME TO progress_old')
        conn.execute('''
            CREATE TABLE progress (
                progress_key TEXT NOT NULL,
                user_id INTEGER NOT NULL DEFAULT 0,
                visited INTEGER DEFAULT 0,
                visited_at TEXT,
                complete INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Unsolved',
                remarks TEXT,
                tricky INTEGER DEFAULT 0,
                updated_at TEXT,
                PRIMARY KEY(progress_key, user_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        old_columns = [
            col for col in [
                "progress_key",
                "visited",
                "visited_at",
                "complete",
                "status",
                "remarks",
                "tricky",
                "updated_at",
            ]
            if col in existing_columns
        ]
        insert_columns = ", ".join(old_columns + ["user_id"])
        select_columns = ", ".join(old_columns + ["0"])
        conn.execute(
            f"INSERT INTO progress ({insert_columns}) SELECT {select_columns} FROM progress_old"
        )

        conn.execute('DROP TABLE progress_old')
        conn.commit()
    conn.close()


_init_db()


def load_progress(user_id: int = 0):
    conn = get_db()
    cursor = conn.execute(
        "SELECT * FROM progress WHERE user_id = ?", (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    progress = {}
    for row in rows:
        progress[row[0]] = {
            "visited": bool(row[2]),
            "visited_at": row[3],
            "complete": bool(row[4]),
            "status": row[5] or "Unsolved",
            "remarks": row[6] or "",
            "tricky": bool(row[7]),
            "updated_at": row[8],
        }
    return progress


def question_key(topic_slug, question, q_index):
    return f"{topic_slug}/{q_index}/{question['title'].replace(' ', '-').lower()}"


def mark_visited(progress_key, user_id: int = 0):
    conn = get_db()
    visited_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        '''
        INSERT INTO progress (
            progress_key,
            user_id,
            visited,
            visited_at,
            complete,
            status,
            remarks,
            tricky,
            updated_at
        ) VALUES (?, ?, 1, ?, 0, 'Unsolved', '', 0, ?)
        ON CONFLICT(progress_key, user_id) DO UPDATE SET
            visited=1,
            visited_at=excluded.visited_at
    ''', (progress_key, user_id, visited_at, visited_at))
    conn.commit()
    conn.close()


def update_progress(progress_key, status="Unsolved", remarks="", tricky=False, user_id: int = 0):
    status = status if status in ("Solved", "Unsolved") else "Unsolved"
    complete = status == "Solved"
    updated_at = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute(
        '''
        INSERT INTO progress (
            progress_key,
            user_id,
            visited,
            visited_at,
            complete,
            status,
            remarks,
            tricky,
            updated_at
        ) VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(progress_key, user_id) DO UPDATE SET
            visited=COALESCE(progress.visited, excluded.visited),
            visited_at=COALESCE(progress.visited_at, excluded.visited_at),
            complete=excluded.complete,
            status=excluded.status,
            remarks=excluded.remarks,
            tricky=excluded.tricky,
            updated_at=excluded.updated_at
    ''', (progress_key, user_id, updated_at, int(complete), status, remarks, int(bool(tricky)), updated_at))
    conn.commit()
    conn.close()
    return {
        "complete": complete,
        "status": status,
        "remarks": remarks,
        "tricky": bool(tricky),
        "updated_at": updated_at,
    }


def clear_progress(user_id: int = 0):
    conn = get_db()
    conn.execute(
        "DELETE FROM progress WHERE user_id = ?",
        (user_id,),
    )
    conn.commit()
    conn.close()
