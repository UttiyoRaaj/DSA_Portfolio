import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "progress.db")


def get_db():
    return sqlite3.connect(DB_PATH)
