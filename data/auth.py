from __future__ import annotations

import os
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

from data.db import get_db


def _init_db():
    conn = get_db()
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
    )
    if cursor.fetchone() is None:
        conn.execute(
            '''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                auth_method TEXT NOT NULL DEFAULT 'password',
                oauth_provider TEXT,
                created_at TEXT NOT NULL
            )
            '''
        )
        conn.commit()
    else:
        existing_columns = [row[1] for row in conn.execute("PRAGMA table_info(users)")]
        if 'auth_method' not in existing_columns:
            conn.execute("ALTER TABLE users ADD COLUMN auth_method TEXT NOT NULL DEFAULT 'password'")
        if 'oauth_provider' not in existing_columns:
            conn.execute("ALTER TABLE users ADD COLUMN oauth_provider TEXT")
        conn.commit()
    conn.close()


_init_db()


def create_user(email: str, password: str | None = None, auth_method: str = 'password', oauth_provider: str | None = None) -> dict | None:
    email = email.strip().lower()
    if auth_method == 'password':
        if not password:
            return None
        password_hash = generate_password_hash(password)
    else:
        password_hash = generate_password_hash(os.urandom(32).hex())

    created_at = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    try:
        conn.execute(
            '''
            INSERT INTO users (email, password_hash, auth_method, oauth_provider, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (email, password_hash, auth_method, oauth_provider, created_at),
        )
        conn.commit()
    except Exception:
        conn.close()
        return None
    user = get_user_by_email(email)
    conn.close()
    return user


def create_or_get_oauth_user(email: str, provider: str) -> dict | None:
    user = get_user_by_email(email)
    if user:
        return user
    return create_user(email, password=None, auth_method='oauth', oauth_provider=provider)


def get_user_by_email(email: str) -> dict | None:
    conn = get_db()
    cursor = conn.execute(
        'SELECT id, email, password_hash, auth_method, oauth_provider, created_at FROM users WHERE email = ?',
        (email.strip().lower(),),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        'id': row[0],
        'email': row[1],
        'password_hash': row[2],
        'auth_method': row[3],
        'oauth_provider': row[4],
        'created_at': row[5],
    }


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_db()
    cursor = conn.execute(
        'SELECT id, email, password_hash, auth_method, oauth_provider, created_at FROM users WHERE id = ?',
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        'id': row[0],
        'email': row[1],
        'password_hash': row[2],
        'auth_method': row[3],
        'oauth_provider': row[4],
        'created_at': row[5],
    }


def authenticate_user(email: str, password: str) -> dict | None:
    user = get_user_by_email(email)
    if not user:
        return None
    if user['auth_method'] != 'password':
        return None
    if not check_password_hash(user['password_hash'], password):
        return None
    return user
