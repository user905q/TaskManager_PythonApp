# Main
import sys
from PyQt6.QtWidgets import QApplication
from models.database import Database
from views.main_window import MainWindow


def main():
    Database().connect()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()