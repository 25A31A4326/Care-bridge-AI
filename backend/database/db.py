import sqlite3
import os
from contextlib import contextmanager
from backend.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    with get_db() as conn:
        conn.executescript(schema_sql)
    print("Database initialized successfully at", Config.DATABASE_PATH)

if __name__ == '__main__':
    init_db()
