import sqlite3
import uuid
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "conversations.db")


def _get_db():
    return sqlite3.connect(DB_PATH)

def _init_db():
    if not os.path.exists(DB_PATH):
        conn = _get_db()
        conn.execute('''
            CREATE TABLE conversations (
                id INTEGER PRIMARY KEY,
                session_id TEXT,
                mode TEXT,
                role TEXT,
                content TEXT,
                topic_slug TEXT,
                topic_title TEXT,
                question_key TEXT,
                question_title TEXT,
                timestamp TEXT,
                language_hint TEXT
            )
        ''')
        conn.commit()
        conn.close()

_init_db()

def new_session_id():
    return str(uuid.uuid4())

def save_message(session_id, mode, role, content, topic_slug=None, topic_title=None, question_key=None, question_title=None):
    conn = _get_db()
    message = {
        "session_id": session_id,
        "mode": mode,
        "role": role,
        "content": content,
        "topic_slug": topic_slug,
        "topic_title": topic_title,
        "question_key": question_key,
        "question_title": question_title,
        "timestamp": datetime.now().isoformat(),
        "language_hint": detect_language_hint(content)
    }
    conn.execute('''
        INSERT INTO conversations (session_id, mode, role, content, topic_slug, topic_title, question_key, question_title, timestamp, language_hint)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (message["session_id"], message["mode"], message["role"], message["content"], message["topic_slug"], message["topic_title"], message["question_key"], message["question_title"], message["timestamp"], message["language_hint"]))
    conn.commit()
    conn.close()
    return message

def search_memories(content, mode=None, topic_slug=None, limit=5):
    conn = _get_db()
    query = "SELECT * FROM conversations WHERE 1=1"
    params = []
    if mode:
        query += " AND mode = ?"
        params.append(mode)
    if topic_slug:
        query += " AND topic_slug = ?"
        params.append(topic_slug)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    # Convert rows to dicts
    columns = [desc[0] for desc in cursor.description]
    memories = [dict(zip(columns, row)) for row in rows]
    # Filter by content similarity
    similar = [m for m in memories if content.lower() in m["content"].lower()][:limit]
    return similar

def get_session_messages(session_id, limit=8):
    conn = _get_db()
    cursor = conn.execute(
        '''
        SELECT session_id, mode, role, content, topic_slug, topic_title, question_key, question_title, timestamp, language_hint
        FROM conversations
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        ''',
        (session_id, limit),
    )
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in reversed(rows)]

def detect_language_hint(content):
    # Simple detection
    if any(word in content.lower() for word in ["bhai", "yaar", "kya", "hai", "kar", "raha", "tha", "mujhe", "tum", "tera"]):
        return "hinglish"
    elif any(word in content.lower() for word in ["ami", "tumi", "ki", "keno", "bujhlam", "shona", "shona"]):
        return "bengali_roman"
    return "english"
