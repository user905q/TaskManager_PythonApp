from app.db.connection import get_connection, transactional

class SettingsRepo:
    @staticmethod
    @transactional
    def get(conn, key: str, default: str = None) -> str:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    @staticmethod
    @transactional
    def set(conn, key: str, value: str):
        conn.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?", (key, value, value))