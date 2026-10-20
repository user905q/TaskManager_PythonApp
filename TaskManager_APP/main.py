# main


import sys
import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from app.config import LOCK_FILE, DB_PATH, BACKUPS_DIR
from app.logging_setup import setup_logging
from app.db.migrations import init_db
import logging

def create_lock():
    if LOCK_FILE.exists():
        print("Приложение уже запущено.")
        sys.exit(1)
    LOCK_FILE.write_text(str(os.getpid()))

def remove_lock():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()

def backup_db():
    if not DB_PATH.exists():
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUPS_DIR / f"tasks_{timestamp}.db"
    try:
        shutil.copy2(DB_PATH, backup_path)
        # Ротация (оставляем 5 последних)
        backups = sorted(BACKUPS_DIR.glob("tasks_*.db"), key=os.path.getmtime)
        while len(backups) > 5:
            oldest = backups.pop(0)
            oldest.unlink()
    except Exception as e:
        logging.error(f"Ошибка бэкапа: {e}")

def main():
    setup_logging()
    create_lock()
    
    try:
        backup_db()
        init_db()
        
        app = QApplication(sys.argv)
        # Заглушка для окна на этапе 1
        from PyQt6.QtWidgets import QLabel
        w = QLabel("Task Manager — каркас готов. Ожидание View.")
        w.show()
        
        exit_code = app.exec()
        remove_lock()
        sys.exit(exit_code)
    except Exception as e:
        logging.error(f"Критическая ошибка при запуске: {e}")
        remove_lock()
        sys.exit(1)

if __name__ == "__main__":
    main()