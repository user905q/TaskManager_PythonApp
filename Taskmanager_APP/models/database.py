import sqlite3
import logging
import shutil
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "tasks.db"
INIT_SQL = Path(__file__).parent.parent / "init.sql"
BACKUPS_DIR = Path(__file__).parent.parent / "backups"
LOG_PATH = Path(__file__).parent.parent / "error.log"

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


class Database:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        if self._connection is None:
            self._connection = sqlite3.connect(str(DB_PATH))
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL;")
            self._connection.execute("PRAGMA foreign_keys=ON;")
            self._init_schema()
            self._backup()
        return self._connection

    def _init_schema(self):
        if INIT_SQL.exists():
            with open(INIT_SQL, encoding="utf-8") as f:
                self._connection.executescript(f.read())
            self._connection.commit()

    def _backup(self):
        if not DB_PATH.exists():
            return
        BACKUPS_DIR.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUPS_DIR / f"tasks_{stamp}.db"
        try:
            shutil.copy2(DB_PATH, backup_file)
            backups = sorted(BACKUPS_DIR.glob("tasks_*.db"))
            while len(backups) > 5:
                backups.pop(0).unlink()
        except Exception as e:
            logging.error(f"Backup failed: {e}")

    def cursor(self):
        return self.connect().cursor()

    def commit(self):
        self.connect().commit()

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None