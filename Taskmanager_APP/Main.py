# Main
# import sys
# from PyQt6.QtWidgets import QApplication
# from models.database import Database
# from views.main_window import MainWindow


# def main():
#    Database().connect()
#    app = QApplication(sys.argv)
#    window = MainWindow()
#    window.show()
#    sys.exit(app.exec())


#if __name__ == "__main__":
#    main()

import sys
from PyQt6.QtWidgets import QApplication
from models.database import Database

# Закомментировано на время проверки Model:
# from views.main_window import MainWindow


def main():
    # Инициализация БД
    db = Database().connect()
    print("✅ БД создана:", db)
    print("✅ Файл tasks.db существует")
    
    # Проверка таблиц
    cur = db.cursor()
    tables = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    print(f"✅ Таблиц: {len(tables)}")
    for t in tables:
        print(f"   - {t['name']}")
    
    # Проверка предустановок
    tags = cur.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
    columns = cur.execute("SELECT COUNT(*) FROM board_columns").fetchone()[0]
    print(f"✅ Тегов: {tags}")
    print(f"✅ Колонок: {columns}")
    
    # Запуск GUI (закомментировать, если просто проверяете БД)
    # app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec())


if __name__ == "__main__":
    main()