import sqlite3
import functools
import logging
from app.config import DB_PATH

class DBError(Exception):
    pass

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def transactional(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE")
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            logging.error(f"DB Error in {func.__name__}: {e}")
            raise DBError(str(e))
        finally:
            conn.close()
    return wrapper