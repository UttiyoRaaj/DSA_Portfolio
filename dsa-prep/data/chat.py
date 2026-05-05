from __future__ import annotations

import json
from datetime import datetime, timezone
from data.db import get_db


def init_chat_db():
    """Initialize chat database tables"""
    conn = get_db()

    # Create chat_sessions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_name TEXT NOT NULL,
            selected_topics TEXT NOT NULL, -- JSON array of topic slugs
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Create chat_messages table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL, -- 'teacher' or 'student'
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


def create_chat_session(user_id: int, session_name: str, selected_topics: list[str]) -> int:
    """Create a new chat session and return its ID"""
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()

    cursor = conn.execute('''
        INSERT INTO chat_sessions (user_id, session_name, selected_topics, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, session_name, json.dumps(selected_topics), now, now))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def add_chat_message(session_id: int, role: str, message: str):
    """Add a message to a chat session"""
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()

    conn.execute('''
        INSERT INTO chat_messages (session_id, role, message, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (session_id, role, message, now))

    conn.commit()
    conn.close()


def get_chat_sessions(user_id: int) -> list[dict]:
    """Get all chat sessions for a user"""
    conn = get_db()
    cursor = conn.execute('''
        SELECT id, session_name, selected_topics, created_at, updated_at
        FROM chat_sessions
        WHERE user_id = ?
        ORDER BY updated_at DESC
    ''', (user_id,))

    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            'id': row[0],
            'session_name': row[1],
            'selected_topics': json.loads(row[2]),
            'created_at': row[3],
            'updated_at': row[4],
        })

    conn.close()
    return sessions


def get_chat_messages(session_id: int) -> list[dict]:
    """Get all messages for a chat session"""
    conn = get_db()
    cursor = conn.execute('''
        SELECT role, message, timestamp
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY timestamp ASC
    ''', (session_id,))

    messages = []
    for row in cursor.fetchall():
        messages.append({
            'role': row[0],
            'message': row[1],
            'timestamp': row[2],
        })

    conn.close()
    return messages


def delete_chat_session(session_id: int, user_id: int) -> bool:
    """Delete a chat session and all its messages"""
    conn = get_db()

    # Verify the session belongs to the user
    cursor = conn.execute('SELECT user_id FROM chat_sessions WHERE id = ?', (session_id,))
    row = cursor.fetchone()
    if not row or row[0] != user_id:
        conn.close()
        return False

    # Delete messages first (due to foreign key constraint)
    conn.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
    conn.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))

    conn.commit()
    conn.close()
    return True


def update_session_timestamp(session_id: int):
    """Update the updated_at timestamp for a session"""
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()

    conn.execute('''
        UPDATE chat_sessions
        SET updated_at = ?
        WHERE id = ?
    ''', (now, session_id))

    conn.commit()
    conn.close()