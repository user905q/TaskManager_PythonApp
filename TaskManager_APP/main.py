# # main
import os
import sys
import psutil
from PyQt6.QtWidgets import QApplication
from app.config import LOCK_FILE
from app.logging_setup import setup_logging
from app.db.migrations import init_db
from app.views.main_window import MainWindow
import logging


def create_lock():
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            if psutil.pid_exists(pid):
                print("Приложение уже запущено.")
                sys.exit(1)
            else:
                LOCK_FILE.unlink()
        except Exception:
            LOCK_FILE.unlink()
    LOCK_FILE.write_text(str(os.getpid()))

def remove_lock():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()

def main():
    setup_logging()
    create_lock()
    
    try:
        init_db()
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        exit_code = app.exec()
        remove_lock()
        sys.exit(exit_code)
    except Exception as e:
        logging.error(f"Критическая ошибка при запуске: {e}")
        print(f"Ошибка: {e}")
        remove_lock()
        sys.exit(1)

if __name__ == "__main__":
    main()

# import sys
# from app.db.migrations import init_db
# from app.models.task_repo import TaskRepo
# from app.models.section_repo import SectionRepo
# from app.models.entities import Task, Section
# from app.models.column_repo import ColumnRepo

# init_db()
# print("Генерация тестовых данных...")

# sec_work = SectionRepo.create(Section(name="Работа", color="#EF4444"))
# sec_study = SectionRepo.create(Section(name="Учеба", color="#3B82F6"))


# TaskRepo.create(Task(title="Написать ТЗ", section_id=sec_work))
# TaskRepo.create(Task(title="Сделать UI", section_id=sec_work))
# TaskRepo.create(Task(title="Купить тетради", section_id=sec_study))

# print("Готово.")
# sys.exit(0)